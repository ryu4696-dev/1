package jp.co.kobayashi.cardboardquote

import android.app.Activity
import android.content.Intent
import android.graphics.*
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.widget.*
import java.text.NumberFormat
import java.util.Locale
import kotlin.math.ceil
import kotlin.math.max

class MainActivity : Activity() {
    private lateinit var fluteSpinner: Spinner
    private lateinit var materialSpinner: Spinner
    private lateinit var waterSpinner: Spinner
    private lateinit var lengthEdit: EditText
    private lateinit var widthEdit: EditText
    private lateinit var depthEdit: EditText
    private lateinit var processEdit: EditText
    private lateinit var lotEdit: EditText
    private lateinit var unitText: TextView
    private var latestInput: QuoteInput? = null
    private var latestResult: QuoteResult? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(44,94,69)
        val root = LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(dp(18),dp(18),dp(18),dp(28)); setBackgroundColor(Color.rgb(245,241,232)) }
        val scroll=ScrollView(this).apply { isFillViewport=true; addView(root) }
        setContentView(scroll)
        root.addView(label("段ボール簡易見積",26,true))
        root.addView(label("1品だけ、必要項目だけ入力",14,false,Color.rgb(100,105,101)), lp(mb=18))

        root.addView(label("フルート",15,true)); fluteSpinner=spinner(Flute.entries.map{it.label}); root.addView(fluteSpinner)
        root.addView(label("寸法（mm）",15,true),lp(mt=12))
        val dims=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL}
        lengthEdit=numEdit("長"); widthEdit=numEdit("巾"); depthEdit=numEdit("深")
        dims.addView(lengthEdit, LinearLayout.LayoutParams(0,dp(56),1f)); dims.addView(space()); dims.addView(widthEdit,LinearLayout.LayoutParams(0,dp(56),1f)); dims.addView(space()); dims.addView(depthEdit,LinearLayout.LayoutParams(0,dp(56),1f)); root.addView(dims)

        root.addView(label("材質",15,true),lp(mt=12)); materialSpinner=spinner(MaterialMaster.materials.map{it.name}); root.addView(materialSpinner)
        root.addView(label("撥水",15,true),lp(mt=10)); waterSpinner=spinner(MaterialMaster.water.keys.toList()); root.addView(waterSpinner)
        root.addView(label("加工賃（円 / ㎡）",15,true),lp(mt=12)); processEdit=numEdit("10",decimal=true).apply{setText("10")}; root.addView(processEdit,LinearLayout.LayoutParams(-1,dp(56)))
        root.addView(label("ロット（個）",15,true),lp(mt=12)); lotEdit=numEdit("1000").apply{setText("1000")}; root.addView(lotEdit,LinearLayout.LayoutParams(-1,dp(56)))

        val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL; setPadding(dp(18),dp(16),dp(18),dp(16)); setBackgroundColor(Color.WHITE)}
        card.addView(label("見積単価",15,true)); unitText=label("— 円 / 個",34,true,Color.rgb(44,94,69)); card.addView(unitText); root.addView(card,lp(mt=18))
        val calc=button("計算する",false); root.addView(calc,lp(mt=14,h=56)); val show=button("金額を見せる",true); root.addView(show,lp(mt=8,h=56))
        calc.setOnClickListener{ calculate() }
        show.setOnClickListener{ if(calculate()) showQuote() }
    }

    private fun calculate():Boolean = try {
        val input=QuoteInput(
            Flute.entries[fluteSpinner.selectedItemPosition],
            lengthEdit.text.toString().toInt(), widthEdit.text.toString().toInt(), depthEdit.text.toString().toInt(),
            MaterialMaster.materials[materialSpinner.selectedItemPosition],
            MaterialMaster.water[waterSpinner.selectedItem.toString()] ?: 0f,
            processEdit.text.toString().toFloatOrNull() ?: 0f,
            lotEdit.text.toString().toInt()
        )
        val r=Calculator.calculate(input); latestInput=input; latestResult=r
        unitText.text="${nf(r.unitPrice)} 円 / 個"; true
    } catch(e:Exception) { Toast.makeText(this,e.message ?: "入力を確認してください",Toast.LENGTH_SHORT).show(); false }

    private fun showQuote() {
        val i=latestInput?:return; val r=latestResult?:return
        startActivity(Intent(this,QuoteActivity::class.java).apply{
            putExtra("flute",i.flute.label); putExtra("l",i.length); putExtra("w",i.width); putExtra("d",i.depth); putExtra("material",i.material.name)
            putExtra("water",waterSpinner.selectedItem.toString()); putExtra("lot",i.lot); putExtra("unit",r.unitPrice); putExtra("total",r.totalPrice)
        })
    }

    private fun spinner(items:List<String>)=Spinner(this).apply{ adapter=ArrayAdapter(this@MainActivity,android.R.layout.simple_spinner_dropdown_item,items); minimumHeight=dp(50) }
    private fun numEdit(hint:String, decimal:Boolean=false)=EditText(this).apply{ this.hint=hint; setPadding(dp(12),0,dp(12),0); setBackgroundColor(Color.WHITE); inputType=if(decimal) InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL else InputType.TYPE_CLASS_NUMBER }
    private fun button(text:String,outline:Boolean)=Button(this).apply{ this.text=text; textSize=17f; if(outline) setTextColor(Color.rgb(44,94,69)) else {setTextColor(Color.WHITE); setBackgroundColor(Color.rgb(44,94,69))} }
    private fun label(t:String,size:Int,bold:Boolean,color:Int=Color.rgb(31,37,33))=TextView(this).apply{text=t;textSize=size.toFloat();setTextColor(color);if(bold)setTypeface(typeface,1)}
    private fun lp(mt:Int=0,mb:Int=0,h:Int=-2)=LinearLayout.LayoutParams(-1,if(h>0)dp(h) else h).apply{topMargin=dp(mt);bottomMargin=dp(mb)}
    private fun space()=Space(this).apply{layoutParams=LinearLayout.LayoutParams(dp(8),1)}
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
    private fun nf(v:Number)=NumberFormat.getNumberInstance(Locale.JAPAN).format(v)
}

class QuoteActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState); window.statusBarColor=Color.rgb(44,94,69)
        val l=intent.getIntExtra("l",0); val w=intent.getIntExtra("w",0); val d=intent.getIntExtra("d",0); val lot=intent.getIntExtra("lot",0); val unit=intent.getIntExtra("unit",0); val total=intent.getLongExtra("total",0)
        val flute=intent.getStringExtra("flute").orEmpty(); val material=intent.getStringExtra("material").orEmpty(); val water=intent.getStringExtra("water").orEmpty()
        val root=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(20),dp(18),dp(20),dp(24));setBackgroundColor(Color.rgb(245,241,232))}
        setContentView(root); root.addView(text("概算金額",23,true,Gravity.CENTER))
        root.addView(CardboardBoxView(this).apply{lengthMm=l;widthMm=w;depthMm=d},LinearLayout.LayoutParams(-1,dp(310)))
        val spec=text("$flute   $l × $w × $d mm\n$material   $water\n${nf(lot)} 個",17,false,Gravity.CENTER); spec.setPadding(0,dp(12),0,dp(8)); root.addView(spec)
        root.addView(text("${nf(unit)} 円 / 個",40,true,Gravity.CENTER,Color.rgb(44,94,69)))
        root.addView(text("合計  ${nf(total)} 円",24,true,Gravity.CENTER),LinearLayout.LayoutParams(-1,dp(64)))
        root.addView(Button(this).apply{text="戻る";setOnClickListener{finish()}},LinearLayout.LayoutParams(-1,dp(54)))
    }
    private fun text(t:String,s:Int,b:Boolean,g:Int,c:Int=Color.rgb(31,37,33))=TextView(this).apply{text=t;textSize=s.toFloat();gravity=g;setTextColor(c);if(b)setTypeface(typeface,1)}
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt(); private fun nf(v:Number)=NumberFormat.getNumberInstance(Locale.JAPAN).format(v)
}

class CardboardBoxView(context: android.content.Context): View(context) {
    var lengthMm=400; set(v){field=v;invalidate()}; var widthMm=300; set(v){field=v;invalidate()}; var depthMm=250; set(v){field=v;invalidate()}
    private val front=Paint(1).apply{color=Color.rgb(201,154,98)}; private val side=Paint(1).apply{color=Color.rgb(164,116,71)}; private val top=Paint(1).apply{color=Color.rgb(224,187,137)}
    private val line=Paint(1).apply{color=Color.rgb(92,64,38);style=Paint.Style.STROKE;strokeWidth=3f}; private val txt=Paint(1).apply{color=Color.DKGRAY;textSize=27f;textAlign=Paint.Align.CENTER}
    override fun onDraw(c:Canvas){ super.onDraw(c); val ww=width.toFloat(); val hh=height.toFloat(); if(ww<=0||hh<=0)return; val md=max(lengthMm,max(widthMm,depthMm)).toFloat().coerceAtLeast(1f)
        val bw=(ww*.58f*(lengthMm/md)).coerceIn(ww*.30f,ww*.58f); val bh=(hh*.44f*(depthMm/md)).coerceIn(hh*.20f,hh*.44f); val sk=(ww*.18f*(widthMm/md)).coerceIn(ww*.09f,ww*.18f); val cx=ww*.48f; val cy=hh*.56f; val l=cx-bw/2;val r=cx+bw/2;val t=cy-bh/2;val b=cy+bh/2
        fun p(vararg a:Float)=Path().apply{moveTo(a[0],a[1]);var i=2;while(i<a.size){lineTo(a[i],a[i+1]);i+=2};close()}
        val pt=p(l,t,l+sk,t-sk*.55f,r+sk,t-sk*.55f,r,t); val ps=p(r,t,r+sk,t-sk*.55f,r+sk,b-sk*.55f,r,b); val pf=p(l,t,r,t,r,b,l,b)
        c.drawPath(pt,top);c.drawPath(ps,side);c.drawPath(pf,front);c.drawPath(pt,line);c.drawPath(ps,line);c.drawPath(pf,line);c.drawText("$lengthMm mm",cx,b+44,txt);c.save();c.rotate(-90f,l-34,cy);c.drawText("$depthMm mm",l-34,cy,txt);c.restore();c.drawText("$widthMm mm",r+sk*.55f,t-sk*.60f-10,txt)
    }
}

data class Material(val name:String,val abc:Float,val wf:Float)
object MaterialMaster { val materials=listOf(
        Material("C5XC5", 65.0f, 98.0f),
        Material("C5XS160XC5", 69.0f, 102.0f),
        Material("C5XS180XC5", 72.5f, 105.5f),
        Material("C5XSKS180XC5", 77.0f, 110.0f),
        Material("C5XSKS200XC5", 80.0f, 113.0f),
        Material("OPC5XC5", 70.0f, 103.0f),
        Material("OPC5XS160XC5", 74.0f, 107.0f),
        Material("OPC5XS180XC5", 77.5f, 110.5f),
        Material("OPC5XSKS180XC5", 82.0f, 115.0f),
        Material("OPC5XOPC5", 75.0f, 108.0f),
        Material("OPC5XS160XOPC5", 79.0f, 112.0f),
        Material("OPC5XSKS180XOPC5", 87.0f, 120.0f),
        Material("K5XK5", 70.0f, 103.0f),
        Material("K5XS160XK5", 74.0f, 107.0f),
        Material("K5XS180XK5", 77.5f, 110.5f),
        Material("K5XSKS180XK5", 82.0f, 115.0f),
        Material("K5XSKS200XK5", 85.0f, 118.0f),
        Material("K6XK6", 76.0f, 109.0f),
        Material("K6XS160XK6", 80.0f, 113.0f),
        Material("K6XS180XK6", 83.5f, 116.5f),
        Material("K6XSKS180XK6", 88.0f, 121.0f),
        Material("K6XSKS200XK6", 91.0f, 124.0f),
        Material("OPB6XK6", 81.0f, 114.0f),
        Material("OPB6XS160XK6", 85.0f, 118.0f),
        Material("OPB6XS180XK6", 88.5f, 121.5f),
        Material("OPB6XSKS180XK6", 93.0f, 126.0f),
        Material("OPB6XSKS200XK6", 96.0f, 129.0f),
        Material("OPB6XOPB6", 86.0f, 119.0f),
        Material("OPB6XS160XOPB6", 90.0f, 123.0f),
        Material("OPB6XS180XOPB6", 93.5f, 126.5f),
        Material("OPB6XSKS180XOPB6", 98.0f, 131.0f),
        Material("OPB6XSKS200XOPB6", 101.0f, 134.0f),
        Material("K7XK7", 87.0f, 120.0f),
        Material("K7XS160XK7", 91.0f, 124.0f),
        Material("K7XS180XK7", 94.5f, 127.5f),
        Material("K7XSKS180XK7", 99.0f, 132.0f),
        Material("K7XSKS200XK7", 102.0f, 135.0f)
    ); val water=linkedMapOf("撥水なし" to 0f,"片面撥水" to 2f,"両面撥水" to 4f) }

enum class Flute(val label:String,val glue:Int,val panelAdjust:Int,val flapAdjust:Int){AF("AF",32,-3,4),BF("BF",32,-3,2),CF("CF",32,-2,3),WF("WF",35,-3,6)}
data class QuoteInput(val flute:Flute,val length:Int,val width:Int,val depth:Int,val material:Material,val waterAdd:Float,val processRate:Float,val lot:Int)
data class QuoteResult(val paperWidth:Int,val up:Int,val areaPerPiece:Double,val unitPrice:Int,val totalPrice:Long)
object Calculator {
    fun calculate(i:QuoteInput):QuoteResult {
        require(i.length>0&&i.width>0&&i.depth>0){"寸法を入力してください"};require(i.lot>0){"ロットを入力してください"};require(i.processRate>=0){"加工賃を確認してください"}
        val flow=i.flute.glue+i.length+i.width+i.length+(i.width+i.flute.panelAdjust)+7
        val flap=(i.width+i.flute.flapAdjust)/2.0; val widthTotal=ceil(flap+i.depth+flap).toInt()
        val candidates=(1..6).mapNotNull{up->val need=widthTotal*up+16;val paper=ceil(need/50.0).toInt()*50;if(paper<950||paper>2000)null else Triple(up,paper,paper-need)}
        require(candidates.isNotEmpty()){"紙巾950〜2000mmで丁取りできません"}
        val best=candidates.minWith(compareBy<Triple<Int,Int,Int>>{it.third}.thenBy{it.second}.thenByDescending{it.first})
        fun ru3(v:Double):Double {
            return ceil(v*1000.0)/1000.0
        }
        val totalArea=ru3(best.second/1000.0*flow/1000.0)
        val each=ru3(totalArea/best.first)
        val mat=(if(i.flute==Flute.WF)i.material.wf else i.material.abc)+i.waterAdd
        val unit=ceil(each*(mat+i.processRate)).toInt()
        return QuoteResult(best.second,best.first,each,unit,unit.toLong()*i.lot)
    }
}
