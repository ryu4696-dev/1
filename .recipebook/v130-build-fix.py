from pathlib import Path

p = Path("recipe-book/app/src/main/java/dev/ryu4696/recipebook/MainActivity.java")
s = p.read_text(encoding="utf-8")

old = """    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }
"""
new = """    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private float dp(float v) {
        return v * getResources().getDisplayMetrics().density;
    }
"""
if old not in s:
    raise SystemExit("dp helper not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
