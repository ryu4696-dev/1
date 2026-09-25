package jp.co.kobayashi.cardboardquote

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.graphics.*
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.widget.*
import java.text.NumberFormat
import java.util.Locale
import kotlin.math.*
import kotlin.random.Random

class MainActivity : Activity() {
    private var selectedFlute = Flute.AF
    private var selectedMaterial = MaterialMaster.materials.first()
    private val fluteButtons = mutableMapOf<Flute, TextView>()

    private lateinit var materialButton: TextView
    private lateinit var lengthEdit: EditText
    private lateinit var widthEdit: EditText
    private lateinit var depthEdit: EditText
    private lateinit var processEdit: EditText
    private lateinit var unitText: TextView

    private var latestInput: QuoteInput? = null
    private var latestResult: QuoteResult? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = GREEN_DARK

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(28))
            setBackgroundColor(BG)
        }
        setContentView(ScrollView(this).apply {
            isFillViewport = true
            addView(root)
        })

        root.addView(sectionLabel("フルート"))
        val fluteRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
        }
        listOf(Flute.AF, Flute.BF, Flute.WF).forEachIndexed { index, flute ->
            val b = TextView(this).apply {
                text = flute.label
                textSize = 18f
                gravity = Gravity.CENTER
                setTypeface(typeface, Typeface.BOLD)
                setOnClickListener {
                    selectedFlute = flute
                    refreshFluteButtons()
                    invalidatePrice()
                }
            }
            fluteButtons[flute] = b
            fluteRow.addView(b, LinearLayout.LayoutParams(0, dp(58), 1f).apply {
                if (index > 0) leftMargin = dp(7)
            })
        }
        root.addView(fluteRow)
        refreshFluteButtons()

        root.addView(sectionLabel("寸法（mm）"), lp(mt = 16))
        val dims = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        lengthEdit = numEdit("長")
        widthEdit = numEdit("巾")
        depthEdit = numEdit("深")
        listOf(lengthEdit, widthEdit, depthEdit).forEachIndexed { index, edit ->
            dims.addView(edit, LinearLayout.LayoutParams(0, dp(60), 1f).apply {
                if (index > 0) leftMargin = dp(8)
            })
        }
        root.addView(dims)

        root.addView(sectionLabel("材質"), lp(mt = 16))
        materialButton = TextView(this).apply {
            text = "${displayMaterial(selectedMaterial.name)}   ▼"
            textSize = 17f
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(16), 0, dp(16), 0)
            setTextColor(TEXT)
            background = fieldBackground()
            setOnClickListener { showMaterialDialog() }
        }
        root.addView(materialButton, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(60)))

        root.addView(sectionLabel("加工賃（円 / ㎡）"), lp(mt = 16))
        processEdit = numEdit("加工賃", decimal = true).apply { setText("10") }
        root.addView(processEdit, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(60)))

        val priceCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(16), dp(18), dp(16))
            background = roundedBg(Color.WHITE, radius = 16f)
        }
        priceCard.addView(label("見積単価", 15, true))
        unitText = label("— 円 / 個", 36, true, GREEN_DARK)
        priceCard.addView(unitText)
        root.addView(priceCard, lp(mt = 20))

        val calc = actionButton("計算する", primary = true)
        root.addView(calc, lp(mt = 14, h = 58))
        val show = actionButton("金額を見せる", primary = false)
        root.addView(show, lp(mt = 9, h = 58))

        calc.setOnClickListener { calculate() }
        show.setOnClickListener { if (calculate()) showQuote() }
    }

    private fun refreshFluteButtons() {
        fluteButtons.forEach { (flute, view) ->
            val selected = flute == selectedFlute
            view.setTextColor(if (selected) Color.WHITE else GREEN_DARK)
            view.background = roundedBg(
                if (selected) GREEN_DARK else Color.WHITE,
                strokeColor = if (selected) GREEN_DARK else BORDER,
                strokeWidth = if (selected) 0 else 1,
                radius = 14f
            )
        }
    }

    private fun showMaterialDialog() {
        val shell = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(8), dp(16), dp(8))
        }
        val search = EditText(this).apply {
            hint = "材質を検索"
            textSize = 16f
            setSingleLine(true)
            setPadding(dp(14), 0, dp(14), 0)
            background = fieldBackground()
        }
        val list = ListView(this).apply {
            dividerHeight = 1
            setPadding(0, dp(8), 0, 0)
        }
        shell.addView(search, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)))
        shell.addView(list, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(430)))

        var visible = MaterialMaster.materials.toList()
        fun bind() {
            list.adapter = object : ArrayAdapter<Material>(this, android.R.layout.simple_list_item_1, visible) {
                override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
                    val tv = super.getView(position, convertView, parent) as TextView
                    tv.text = displayMaterial(getItem(position)?.name.orEmpty())
                    tv.textSize = 17f
                    tv.setTextColor(TEXT)
                    tv.setPadding(dp(14), dp(10), dp(14), dp(10))
                    tv.minHeight = dp(52)
                    return tv
                }
            }
        }
        bind()

        val dialog = AlertDialog.Builder(this)
            .setTitle("材質を選択")
            .setView(shell)
            .setNegativeButton("閉じる", null)
            .create()

        list.setOnItemClickListener { _, _, position, _ ->
            selectedMaterial = visible[position]
            materialButton.text = "${displayMaterial(selectedMaterial.name)}   ▼"
            invalidatePrice()
            dialog.dismiss()
        }

        search.addTextChangedListener(SimpleTextWatcher { text ->
            val q = text.trim().uppercase(Locale.ROOT)
            visible = if (q.isEmpty()) MaterialMaster.materials else MaterialMaster.materials.filter { it.name.uppercase(Locale.ROOT).contains(q) }
            bind()
        })
        dialog.show()
    }

    private fun invalidatePrice() {
        latestInput = null
        latestResult = null
        if (::unitText.isInitialized) unitText.text = "— 円 / 個"
    }

    private fun calculate(): Boolean = try {
        val input = QuoteInput(
            flute = selectedFlute,
            length = lengthEdit.text.toString().toInt(),
            width = widthEdit.text.toString().toInt(),
            depth = depthEdit.text.toString().toInt(),
            material = selectedMaterial,
            processRate = processEdit.text.toString().toDoubleOrNull() ?: 0.0
        )
        val result = Calculator.calculate(input)
        latestInput = input
        latestResult = result
        unitText.text = "${nf(result.unitPrice)} 円 / 個"
        true
    } catch (e: Exception) {
        Toast.makeText(this, e.message ?: "入力を確認してください", Toast.LENGTH_SHORT).show()
        false
    }

    private fun showQuote() {
        val i = latestInput ?: return
        val r = latestResult ?: return
        startActivity(Intent(this, QuoteActivity::class.java).apply {
            putExtra("flute", i.flute.label)
            putExtra("l", i.length)
            putExtra("w", i.width)
            putExtra("d", i.depth)
            putExtra("material", i.material.name)
            putExtra("unit", r.unitPrice)
        })
    }

    private fun numEdit(hint: String, decimal: Boolean = false) = EditText(this).apply {
        this.hint = hint
        textSize = 17f
        gravity = Gravity.CENTER_VERTICAL
        setPadding(dp(14), 0, dp(14), 0)
        setTextColor(TEXT)
        setHintTextColor(TEXT_SUB)
        background = fieldBackground()
        inputType = if (decimal) InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL else InputType.TYPE_CLASS_NUMBER
        setOnFocusChangeListener { _, _ -> invalidatePrice() }
    }

    private fun actionButton(text: String, primary: Boolean) = TextView(this).apply {
        this.text = text
        textSize = 18f
        gravity = Gravity.CENTER
        setTypeface(typeface, Typeface.BOLD)
        setTextColor(if (primary) Color.WHITE else GREEN_DARK)
        background = roundedBg(
            if (primary) GREEN_DARK else Color.WHITE,
            strokeColor = if (primary) GREEN_DARK else GREEN_DARK,
            strokeWidth = if (primary) 0 else 1,
            radius = 15f
        )
    }

    private fun sectionLabel(t: String) = label(t, 15, true)
    private fun label(t: String, size: Int, bold: Boolean, color: Int = TEXT) = TextView(this).apply {
        text = t
        textSize = size.toFloat()
        setTextColor(color)
        if (bold) setTypeface(typeface, Typeface.BOLD)
    }
    private fun fieldBackground() = roundedBg(Color.WHITE, BORDER, 1, 12f)
    private fun roundedBg(fill: Int, strokeColor: Int = Color.TRANSPARENT, strokeWidth: Int = 0, radius: Float = 12f) = GradientDrawable().apply {
        setColor(fill)
        cornerRadius = dp(radius.toInt()).toFloat()
        if (strokeWidth > 0) setStroke(dp(strokeWidth), strokeColor)
    }
    private fun lp(mt: Int = 0, mb: Int = 0, h: Int = ViewGroup.LayoutParams.WRAP_CONTENT) = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, if (h > 0) dp(h) else h).apply {
        topMargin = dp(mt)
        bottomMargin = dp(mb)
    }
    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    private fun nf(v: Number) = NumberFormat.getNumberInstance(Locale.JAPAN).format(v)

    companion object {
        val BG = Color.rgb(247, 243, 234)
        val TEXT = Color.rgb(31, 37, 33)
        val TEXT_SUB = Color.rgb(103, 109, 105)
        val BORDER = Color.rgb(207, 211, 206)
        val GREEN_DARK = Color.rgb(40, 101, 73)
    }
}

class QuoteActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = MainActivity.GREEN_DARK

        val l = intent.getIntExtra("l", 0)
        val w = intent.getIntExtra("w", 0)
        val d = intent.getIntExtra("d", 0)
        val unit = intent.getIntExtra("unit", 0)
        val flute = intent.getStringExtra("flute").orEmpty()
        val material = displayMaterial(intent.getStringExtra("material").orEmpty())

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(24), dp(20), dp(24))
            setBackgroundColor(MainActivity.BG)
        }
        setContentView(root)

        root.addView(CardboardBoxView(this).apply {
            lengthMm = l
            widthMm = w
            depthMm = d
        }, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(385)))

        val materialLine = text("$material  $flute", 19, true, Gravity.CENTER)
        materialLine.setPadding(0, dp(8), 0, dp(4))
        root.addView(materialLine)

        val dimensionLine = text("$l × $w × $d mm", 18, false, Gravity.CENTER)
        dimensionLine.setPadding(0, 0, 0, dp(14))
        root.addView(dimensionLine)

        root.addView(text("${nf(unit)} 円 / 個", 42, true, Gravity.CENTER, MainActivity.GREEN_DARK))
        root.addView(TextView(this).apply {
            text = "戻る"
            textSize = 17f
            gravity = Gravity.CENTER
            setTypeface(typeface, Typeface.BOLD)
            setTextColor(MainActivity.TEXT)
            background = GradientDrawable().apply {
                setColor(Color.rgb(222, 224, 221))
                cornerRadius = dp(12).toFloat()
            }
            setOnClickListener { finish() }
        }, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(58)).apply { topMargin = dp(28) })
    }

    private fun text(t: String, size: Int, bold: Boolean, gravityValue: Int, color: Int = MainActivity.TEXT) = TextView(this).apply {
        text = t
        textSize = size.toFloat()
        gravity = gravityValue
        setTextColor(color)
        if (bold) setTypeface(typeface, Typeface.BOLD)
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    private fun nf(v: Number) = NumberFormat.getNumberInstance(Locale.JAPAN).format(v)
}

/**
 * 軽量なインタラクティブ3D箱表示。
 * X=長（正面横）、Z=巾（奥行き）、Y=深（高さ）として描画する。
 */
class CardboardBoxView(context: Context) : View(context) {
    var lengthMm = 400; set(v) { field = max(v, 1); invalidate() }
    var widthMm = 300; set(v) { field = max(v, 1); invalidate() }
    var depthMm = 250; set(v) { field = max(v, 1); invalidate() }

    private var yaw = Math.toRadians(32.0).toFloat()
    private var pitch = Math.toRadians(-22.0).toFloat()
    private var lastX = 0f
    private var lastY = 0f

    private val texture = makeCardboardTexture(256)
    private val texturePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        shader = BitmapShader(texture, Shader.TileMode.REPEAT, Shader.TileMode.REPEAT)
        isFilterBitmap = true
    }
    private val shadePaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val edgePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(94, 64, 38)
        style = Paint.Style.STROKE
        strokeWidth = dpF(1.7f)
        strokeJoin = Paint.Join.ROUND
    }
    private val creasePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.argb(145, 91, 61, 34)
        style = Paint.Style.STROKE
        strokeWidth = dpF(1.1f)
    }
    private val cutPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.argb(180, 81, 52, 31)
        style = Paint.Style.STROKE
        strokeWidth = dpF(1.35f)
    }

    private data class V3(val x: Float, val y: Float, val z: Float)
    private data class P2(val x: Float, val y: Float, val z: Float)
    private data class Face(val id: String, val indices: IntArray, val normal: V3)

    private val faces = listOf(
        Face("front", intArrayOf(0, 1, 2, 3), V3(0f, 0f, -1f)),
        Face("back", intArrayOf(5, 4, 7, 6), V3(0f, 0f, 1f)),
        Face("left", intArrayOf(4, 0, 3, 7), V3(-1f, 0f, 0f)),
        Face("right", intArrayOf(1, 5, 6, 2), V3(1f, 0f, 0f)),
        Face("top", intArrayOf(3, 2, 6, 7), V3(0f, 1f, 0f)),
        Face("bottom", intArrayOf(4, 5, 1, 0), V3(0f, -1f, 0f))
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                parent?.requestDisallowInterceptTouchEvent(true)
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY
                yaw += dx * 0.012f
                pitch = (pitch + dy * 0.009f).coerceIn(
                    Math.toRadians(-68.0).toFloat(),
                    Math.toRadians(68.0).toFloat()
                )
                lastX = event.x
                lastY = event.y
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (width <= 0 || height <= 0) return

        val maxDim = max(lengthMm, max(widthMm, depthMm)).toFloat().coerceAtLeast(1f)
        val xHalf = max(lengthMm / maxDim, 0.035f) / 2f
        val zHalf = max(widthMm / maxDim, 0.035f) / 2f
        val yHalf = max(depthMm / maxDim, 0.035f) / 2f

        val vertices = arrayOf(
            V3(-xHalf, -yHalf, -zHalf), V3(xHalf, -yHalf, -zHalf),
            V3(xHalf, yHalf, -zHalf), V3(-xHalf, yHalf, -zHalf),
            V3(-xHalf, -yHalf, zHalf), V3(xHalf, -yHalf, zHalf),
            V3(xHalf, yHalf, zHalf), V3(-xHalf, yHalf, zHalf)
        )

        val rotated = vertices.map { rotate(it) }
        val marginX = dpF(22f)
        val marginY = dpF(18f)
        val availW = width - marginX * 2
        val availH = height - marginY * 2
        val minX = rotated.minOf { it.x }
        val maxX = rotated.maxOf { it.x }
        val minY = rotated.minOf { it.y }
        val maxY = rotated.maxOf { it.y }
        val scale = min(
            availW / (maxX - minX).coerceAtLeast(0.01f),
            availH / (maxY - minY).coerceAtLeast(0.01f)
        ) * 0.84f
        val cx = width / 2f - (minX + maxX) / 2f * scale
        val cy = height / 2f + (minY + maxY) / 2f * scale
        val pts = rotated.map { P2(cx + it.x * scale, cy - it.y * scale, it.z) }

        val light = normalize(V3(-0.40f, 0.90f, -0.55f))
        val ordered = faces.map { face ->
            face to face.indices.map { pts[it].z }.average().toFloat()
        }.sortedByDescending { it.second }

        ordered.forEach { (face, _) ->
            val poly = face.indices.map { pts[it] }
            val path = poly.toPath()
            canvas.drawPath(path, texturePaint)

            val n = rotate(face.normal)
            val ndotl = (n.x * light.x + n.y * light.y + n.z * light.z).coerceIn(-1f, 1f)
            val shadeAlpha = when {
                ndotl > 0.45f -> 10
                ndotl > 0.05f -> 26
                ndotl > -0.35f -> 46
                else -> 70
            }
            shadePaint.color = Color.argb(shadeAlpha, 67, 43, 20)
            canvas.drawPath(path, shadePaint)
            canvas.drawPath(path, edgePaint)

            when (face.id) {
                "top" -> drawTopFlaps(canvas, poly)
                "front", "back" -> drawVerticalJoint(canvas, poly)
                "right", "left" -> drawSideFold(canvas, poly)
            }
        }
    }

    private fun drawTopFlaps(canvas: Canvas, p: List<P2>) {
        val nearMid = midpoint(p[0], p[1])
        val farMid = midpoint(p[3], p[2])
        canvas.drawLine(nearMid.x, nearMid.y, farMid.x, farMid.y, creasePaint)

        listOf(0.22f, 0.78f).forEach { t ->
            val near = lerp(p[0], p[1], t)
            val far = lerp(p[3], p[2], t)
            val mid = midpoint(near, far)
            canvas.drawLine(near.x, near.y, mid.x, mid.y, cutPaint)
            canvas.drawLine(far.x, far.y, mid.x, mid.y, cutPaint)
        }
    }

    private fun drawVerticalJoint(canvas: Canvas, p: List<P2>) {
        val top = midpoint(p[2], p[3])
        val bottom = midpoint(p[0], p[1])
        val paint = Paint(creasePaint).apply { alpha = 65 }
        canvas.drawLine(top.x, top.y, bottom.x, bottom.y, paint)
    }

    private fun drawSideFold(canvas: Canvas, p: List<P2>) {
        val top = midpoint(p[2], p[3])
        val bottom = midpoint(p[0], p[1])
        val paint = Paint(creasePaint).apply { alpha = 48 }
        canvas.drawLine(top.x, top.y, bottom.x, bottom.y, paint)
    }

    private fun rotate(v: V3): V3 {
        val cy = cos(yaw); val sy = sin(yaw)
        val x1 = v.x * cy + v.z * sy
        val z1 = -v.x * sy + v.z * cy
        val cp = cos(pitch); val sp = sin(pitch)
        val y2 = v.y * cp - z1 * sp
        val z2 = v.y * sp + z1 * cp
        return V3(x1, y2, z2)
    }

    private fun normalize(v: V3): V3 {
        val len = sqrt(v.x * v.x + v.y * v.y + v.z * v.z).coerceAtLeast(0.0001f)
        return V3(v.x / len, v.y / len, v.z / len)
    }

    private fun midpoint(a: P2, b: P2) =
        P2((a.x + b.x) / 2f, (a.y + b.y) / 2f, (a.z + b.z) / 2f)

    private fun lerp(a: P2, b: P2, t: Float) =
        P2(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t)

    private fun List<P2>.toPath() = Path().apply {
        moveTo(this@toPath[0].x, this@toPath[0].y)
        for (i in 1 until this@toPath.size) lineTo(this@toPath[i].x, this@toPath[i].y)
        close()
    }

    private fun makeCardboardTexture(size: Int): Bitmap {
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.rgb(197, 153, 99))
        val random = Random(34192)

        val fleck = Paint(Paint.ANTI_ALIAS_FLAG)
        repeat(size * 10) {
            val delta = random.nextInt(-20, 21)
            fleck.color = Color.rgb(
                (197 + delta).coerceIn(150, 226),
                (153 + delta).coerceIn(112, 198),
                (99 + delta / 2).coerceIn(65, 142)
            )
            fleck.alpha = random.nextInt(10, 34)
            val x = random.nextFloat() * size
            val y = random.nextFloat() * size
            canvas.drawCircle(x, y, random.nextFloat() * 1.25f + 0.15f, fleck)
        }

        val fiber = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            strokeWidth = 0.72f
            color = Color.rgb(125, 88, 54)
        }
        repeat(size * 2) {
            fiber.alpha = random.nextInt(7, 25)
            val x = random.nextFloat() * size
            val y = random.nextFloat() * size
            val len = random.nextFloat() * 11f + 2f
            val slope = random.nextFloat() * 0.22f - 0.11f
            canvas.drawLine(x, y, x + len, y + len * slope, fiber)
        }

        val pulp = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.rgb(232, 205, 166) }
        repeat(size / 2) {
            pulp.alpha = random.nextInt(5, 18)
            val x = random.nextFloat() * size
            val y = random.nextFloat() * size
            canvas.drawOval(
                x, y,
                x + random.nextFloat() * 5f + 1f,
                y + random.nextFloat() * 1.4f + 0.3f,
                pulp
            )
        }
        return bitmap
    }

    private fun dpF(v: Float) = v * resources.displayMetrics.density
}

private class SimpleTextWatcher(private val after: (String) -> Unit) : android.text.TextWatcher {
    override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
    override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) = Unit
    override fun afterTextChanged(s: android.text.Editable?) = after(s?.toString().orEmpty())
}

data class Material(val name: String, val abc: Double, val wf: Double) {
    override fun toString(): String = name
}

object MaterialMaster {
    val materials = listOf(
        Material("C5XC5", 65.0, 98.0),
        Material("C5XS160XC5", 69.0, 102.0),
        Material("C5XS180XC5", 72.5, 105.5),
        Material("C5XSKS180XC5", 77.0, 110.0),
        Material("C5XSKS200XC5", 80.0, 113.0),
        Material("OPC5XC5", 70.0, 103.0),
        Material("OPC5XS160XC5", 74.0, 107.0),
        Material("OPC5XS180XC5", 77.5, 110.5),
        Material("OPC5XSKS180XC5", 82.0, 115.0),
        Material("OPC5XOPC5", 75.0, 108.0),
        Material("OPC5XS160XOPC5", 79.0, 112.0),
        Material("OPC5XSKS180XOPC5", 87.0, 120.0),
        Material("K5XK5", 70.0, 103.0),
        Material("K5XS160XK5", 74.0, 107.0),
        Material("K5XS180XK5", 77.5, 110.5),
        Material("K5XSKS180XK5", 82.0, 115.0),
        Material("K5XSKS200XK5", 85.0, 118.0),
        Material("K6XK6", 76.0, 109.0),
        Material("K6XS160XK6", 80.0, 113.0),
        Material("K6XS180XK6", 83.5, 116.5),
        Material("K6XSKS180XK6", 88.0, 121.0),
        Material("K6XSKS200XK6", 91.0, 124.0),
        Material("OPB6XK6", 81.0, 114.0),
        Material("OPB6XS160XK6", 85.0, 118.0),
        Material("OPB6XS180XK6", 88.5, 121.5),
        Material("OPB6XSKS180XK6", 93.0, 126.0),
        Material("OPB6XSKS200XK6", 96.0, 129.0),
        Material("OPB6XOPB6", 86.0, 119.0),
        Material("OPB6XS160XOPB6", 90.0, 123.0),
        Material("OPB6XS180XOPB6", 93.5, 126.5),
        Material("OPB6XSKS180XOPB6", 98.0, 131.0),
        Material("OPB6XSKS200XOPB6", 101.0, 134.0),
        Material("K7XK7", 87.0, 120.0),
        Material("K7XS160XK7", 91.0, 124.0),
        Material("K7XS180XK7", 94.5, 127.5),
        Material("K7XSKS180XK7", 99.0, 132.0),
        Material("K7XSKS200XK7", 102.0, 135.0)
    )
}

enum class Flute(val label: String, val glue: Int, val panelAdjust: Int, val flapAdjust: Int) {
    AF("AF", 32, -3, 4),
    BF("BF", 32, -3, 2),
    CF("CF", 32, -2, 3),
    WF("WF", 35, -3, 6)
}

data class QuoteInput(
    val flute: Flute,
    val length: Int,
    val width: Int,
    val depth: Int,
    val material: Material,
    val processRate: Double
)

data class QuoteResult(
    val paperWidth: Int,
    val up: Int,
    val areaPerPiece: Double,
    val unitPrice: Int
)

object Calculator {
    fun calculate(i: QuoteInput): QuoteResult {
        require(i.length > 0 && i.width > 0 && i.depth > 0) { "寸法を入力してください" }
        require(i.processRate >= 0) { "加工賃を確認してください" }

        val flow = i.flute.glue + i.length + i.width + i.length + (i.width + i.flute.panelAdjust) + 7
        val widthTotal = i.width + i.flute.flapAdjust + i.depth

        data class Candidate(val up: Int, val paper: Int, val loss: Int)
        val allCandidates = (1..6).map { up ->
            val required = widthTotal * up + 16
            val paper = ceil(required / 50.0).toInt() * 50
            val valid = paper in 950..2000
            Candidate(up, paper, if (valid) paper - required else 9999)
        }
        val minLoss = allCandidates.minOf { it.loss }
        require(minLoss < 9999) { "紙巾950〜2000mmで丁取りできません" }
        val best = allCandidates.first { it.loss == minLoss }

        fun roundUp3(v: Double): Double = ceil((v - 1e-12) * 1000.0) / 1000.0
        val totalArea = roundUp3(best.paper / 1000.0 * flow / 1000.0)
        val areaPerPiece = roundUp3(totalArea / best.up)
        val materialRate = if (i.flute == Flute.WF) i.material.wf else i.material.abc
        val unitPrice = ceil(areaPerPiece * (materialRate + i.processRate) - 1e-12).toInt()

        return QuoteResult(
            paperWidth = best.paper,
            up = best.up,
            areaPerPiece = areaPerPiece,
            unitPrice = unitPrice
        )
    }
}

private fun displayMaterial(name: String): String = name.replace('X', 'x')
