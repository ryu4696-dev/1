#!/usr/bin/env python3
import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text()
marker = "class LoRAWeights:"
if marker not in s:
    raise SystemExit("LoRAWeights marker missing")

cls = r'''
class SafeTensorConvRotWeights:
    """Lazy reader for ComfyUI INT8 ConvRot safetensors."""

    def __init__(self, path, gate_first=True):
        from safetensors import safe_open
        self.f = safe_open(path, framework="pt", device="cpu")
        self.keys = set(self.f.keys())
        self.gate_first = gate_first
        self._gate_cache = {}

    def _cfg(self, base):
        k = base + ".comfy_quant"
        if k not in self.keys:
            return {}
        raw = self.f.get_tensor(k).to(torch.uint8).numpy().tobytes()
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    @staticmethod
    def _regular_hadamard_inplace(w, gs):
        # Comfy ConvRot uses a normalized regular H4 Kronecker Hadamard.
        # It is symmetric and orthogonal, so applying the same transform
        # once more reconstructs the unrotated weight.
        if gs not in (16, 64, 256):
            raise ValueError(f"unsupported ConvRot group size {gs}")
        if w.shape[1] % gs:
            raise ValueError((w.shape, gs))
        dims = {16: 2, 64: 3, 256: 4}[gs]
        norm = float(gs) ** 0.5
        chunk_rows = 256
        for st in range(0, w.shape[0], chunk_rows):
            en = min(st + chunk_rows, w.shape[0])
            x = w[st:en].reshape(en - st, w.shape[1] // gs, *([4] * dims))
            for axis in range(2, 2 + dims):
                z = x.movedim(axis, -1)
                a, b, c, d = z.unbind(-1)
                z = torch.stack(
                    (a + b + c - d,
                     a + b - c + d,
                     a - b + c + d,
                     -a + b + c + d),
                    dim=-1,
                )
                x = z.movedim(-1, axis)
            w[st:en].copy_(x.reshape(en - st, w.shape[1]) / norm)
        return w

    def _load(self, name):
        t = self.f.get_tensor(name)
        if t.dtype == torch.int8:
            sk = name + "_scale"
            if sk not in self.keys:
                raise KeyError(f"INT8 tensor without scale: {name}")
            scale = self.f.get_tensor(sk).float()
            w = t.float()
            w.mul_(scale)
            base = name[:-len(".weight")] if name.endswith(".weight") else name
            cfg = self._cfg(base)
            if cfg.get("convrot"):
                self._regular_hadamard_inplace(w, int(cfg.get("convrot_groupsize", 256)))
            return w
        return t.float()

    def __call__(self, name):
        if name.endswith(".img_mlp.gate_layer") or name.endswith(".img_mlp.proj"):
            base = name.rsplit(".", 1)[0]
            gate_name = base + ".gate_layer"
            proj_name = base + ".proj"
            if name in self._gate_cache:
                return self._gate_cache.pop(name)
            w = self._load(base + ".gate_up.weight")
            a, b = w.chunk(2, dim=0)
            gate, proj = (a, b) if self.gate_first else (b, a)
            if name == gate_name:
                self._gate_cache[proj_name] = proj.contiguous()
                return gate.contiguous()
            self._gate_cache[gate_name] = gate.contiguous()
            return proj.contiguous()
        return self._load(name + ".weight")

    def param(self, name):
        return self._load(name)


'''

s = s.replace(marker, cls + marker, 1)
s = s.replace(
    '    ap.add_argument("--gguf")',
    '    ap.add_argument("--gguf")\n    ap.add_argument("--safetensors")',
    1,
)

old = '''        W = GGUFWeights(a.gguf, gate_first=bool(a.gate_first))
        wp, params = W, W.param
        layers = a.layers'''
new = '''        if a.safetensors:
            W = SafeTensorConvRotWeights(a.safetensors, gate_first=bool(a.gate_first))
        else:
            W = GGUFWeights(a.gguf, gate_first=bool(a.gate_first))
        wp, params = W, W.param
        layers = a.layers'''
if old not in s:
    raise SystemExit("weight provider selection target missing")
s = s.replace(old, new, 1)
p.write_text(s)
print("patched", p)
