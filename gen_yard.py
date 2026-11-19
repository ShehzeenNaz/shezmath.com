#!/usr/bin/env python3
"""Generate Phase 2 yard-home/ hub for shezmath.com. Run from ~/workspace/shezmath-site."""
import os, json, html

BASE = os.path.expanduser("~/workspace/shezmath-site")
OUT = os.path.join(BASE, "yard-home")
os.makedirs(OUT, exist_ok=True)

COMMON_JS = r"""
var UNIT = 'imp';
function f(kind){ return {'ft':0.3048,'in':2.54,'sqft':0.092903,'yd3':0.764555,'ton':0.907185,'lb':0.453592,'gal':3.78541}[kind] || 1; }
function v(id, kind){ var x = parseFloat(document.getElementById(id).value); if(isNaN(x)) return NaN; return UNIT === 'met' ? x / f(kind) : x; }
function raw(id){ return parseFloat(document.getElementById(id).value); }
function fmtVol(y){ return UNIT === 'met' ? (y*0.764555).toFixed(2) + ' m\u00b3' : y.toFixed(2) + ' cubic yards'; }
function fmtWt(t){ return UNIT === 'met' ? (t*0.907185).toFixed(2) + ' tonnes' : t.toFixed(2) + ' tons'; }
function fmtArea(a){ return UNIT === 'met' ? (a*0.092903).toFixed(2) + ' m\u00b2' : a.toFixed(0) + ' sq ft'; }
function fmtLenFt(x){ return UNIT === 'met' ? (x*0.3048).toFixed(2) + ' m' : x.toFixed(2) + ' ft'; }
function fmtLenIn(x){ return UNIT === 'met' ? (x*2.54).toFixed(1) + ' cm' : x.toFixed(2) + ' in'; }
function fmtLb(x){ return UNIT === 'met' ? (x*0.453592).toFixed(1) + ' kg' : x.toFixed(1) + ' lb'; }
function fmtGal(x){ return UNIT === 'met' ? (x*3.78541).toFixed(2) + ' litres' : x.toFixed(2) + ' gallons'; }
function fmtCuFt(x){ return UNIT === 'met' ? (x*0.0283168).toFixed(2) + ' m\u00b3' : x.toFixed(2) + ' cubic feet'; }
function setUnit(u){
  if(u === UNIT) return;
  document.querySelectorAll('[data-kind]').forEach(function(el){
    var val = parseFloat(el.value); if(isNaN(val)) return;
    el.value = (u === 'met' ? val * f(el.dataset.kind) : val / f(el.dataset.kind)).toFixed(2);
  });
  UNIT = u;
  document.querySelectorAll('.ulabel').forEach(function(s){ s.textContent = u === 'met' ? s.dataset.met : s.dataset.imp; });
  document.getElementById('unit-imp').className = u === 'imp' ? 'btn' : 'btn secondary';
  document.getElementById('unit-met').className = u === 'met' ? 'btn' : 'btn secondary';
  calculate();
}
function resetCalc(){
  UNIT = 'imp';
  document.querySelectorAll('.ulabel').forEach(function(s){ s.textContent = s.dataset.imp; });
  document.getElementById('unit-imp').className = 'btn';
  document.getElementById('unit-met').className = 'btn secondary';
  document.getElementById('calc-form').reset();
  calculate();
}
document.querySelectorAll('#calc-form input, #calc-form select').forEach(function(el){
  el.addEventListener('input', calculate);
  el.addEventListener('change', calculate);
});
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ | ShezMath</title>
<meta name="description" content="__META__">
<link rel="stylesheet" href="../style.css">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [__FAQJSON__]
}
</script>
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="logo" href="../index.html">ShezMath</a>
    <nav class="main">
      <a href="../index.html">Home</a>
      <a href="index.html">Yard &amp; Home</a>
      <a href="../index.html#gpa">GPA</a>
      <a href="../about.html">About</a>
    </nav>
  </div>
</header>
<main class="wrap">

<h1>__TITLE__</h1>
<p class="lede">__LEDE__</p>

<div class="calc">
  <p><button class="btn" type="button" id="unit-imp" onclick="setUnit('imp')">Imperial (ft / in)</button>
  <button class="btn secondary" type="button" id="unit-met" onclick="setUnit('met')">Metric (m / cm)</button></p>
  <form id="calc-form" onsubmit="return false;">
__INPUTS__
    <button class="btn" type="button" onclick="calculate()">Calculate</button>
    <button class="btn secondary" type="button" onclick="resetCalc()">Reset</button>
  </form>
  <div class="result" id="result"></div>
</div>
<p class="note">Your numbers never leave your device. All calculations happen in your browser.</p>

<h2>How It Works</h2>
<p><strong>Formula:</strong> __FORMULA__</p>
<p><strong>Worked example:</strong> __EXAMPLE__</p>

<h2>Quick Reference</h2>
__TABLE__

<h2>Related Calculators</h2>
<div class="grid">
__RELATED__
</div>

<h2>Frequently Asked Questions</h2>
<div class="faq">
__FAQHTML__
</div>

</main>
<footer class="site">
  <div class="wrap">
    <a href="../about.html">About</a>
    <a href="../contact.html">Contact</a>
    <a href="../privacy-policy.html">Privacy Policy</a>
    <a href="../terms.html">Terms</a>
    <a href="../methodology.html">Methodology</a>
    <p>ShezMath — free home, yard and construction calculators. Calculations run in your browser.</p>
  </div>
</footer>
<script>
__COMMONJS__
function calculate() {
  var r = document.getElementById('result');
__CALC__
}
calculate();
</script>
</body>
</html>
"""

def inp(id_, label, imp, met, kind, value, step="0.5", minv="0"):
    return ('    <label for="%s">%s (<span class="ulabel" data-imp="%s" data-met="%s">%s</span>)</label>\n'
            '    <input type="number" id="%s" data-kind="%s" value="%s" min="%s" step="%s">\n'
            % (id_, label, imp, met, imp, id_, kind, value, minv, step))

def inp_plain(id_, label, value, step="1", minv="0"):
    return ('    <label for="%s">%s</label>\n'
            '    <input type="number" id="%s" value="%s" min="%s" step="%s">\n'
            % (id_, label, id_, value, minv, step))

def sel(id_, label, options):
    # options: list of (value, text, selected?)
    opts = "".join('<option value="%s"%s>%s</option>' % (v, ' selected' if s else '', t)
                   for v, t, s in options)
    return '    <label for="%s">%s</label>\n    <select id="%s">%s</select>\n' % (id_, label, id_, opts)

def price_input(label_imp, label_met):
    return ('    <label for="price">Price (<span class="ulabel" data-imp="%s" data-met="%s">%s</span>) — optional, leave blank to skip cost</label>\n'
            '    <input type="number" id="price" value="" min="0" step="0.01" placeholder="e.g. 45">\n'
            % (label_imp, label_met, label_imp))

def cost_js(qty_imp_expr, qty_met_expr, unit_imp, unit_met):
    return ("  var price = raw('price');\n"
            "  var costTxt = '';\n"
            "  if(price > 0){ var q = UNIT === 'met' ? (%s) : (%s); costTxt = '<br>Estimated cost: <b>$' + (q * price).toFixed(2) + '</b> at $' + price + ' ' + (UNIT === 'met' ? '%s' : '%s') + '.'; }\n"
            % (qty_met_expr, qty_imp_expr, unit_met, unit_imp))

def table(headers, rows):
    th = "".join("<th>%s</th>" % h for h in headers)
    tr = "".join("<tr>" + "".join("<td>%s</td>" % c for c in row) + "</tr>" for row in rows)
    return "<table><tr>%s</tr>%s</table>" % (th, tr)

def faq_json(faqs):
    return ",\n    ".join(json.dumps({"@type": "Question", "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": a}}) for q, a in faqs)

def faq_html(faqs):
    return "".join("  <h3>%s</h3>\n  <p>%s</p>\n" % (q, a) for q, a in faqs)

TOOLS = []
def T(slug, title, meta, lede, inputs, calc, formula, example, tbl, faqs, related, keywords):
    TOOLS.append(dict(slug=slug, title=title, meta=meta, lede=lede, inputs=inputs,
                      calc=calc, formula=formula, example=example, table=tbl, faqs=faqs,
                      related=related, keywords=keywords))

# 1 Gravel Driveway
T("gravel-driveway-calculator", "Gravel Driveway Calculator",
  "Work out how much gravel your driveway needs in cubic yards and tons. Enter length, width and depth to get exact amounts fast. Free to use.",
  "Find how many tons and cubic yards of gravel your driveway needs before you order. Built for homeowners planning a new or topped-up driveway.",
  inp("length","Driveway length","ft","m","ft","40") + inp("width","Driveway width","ft","m","ft","12") + inp("depth","Gravel depth","in","cm","in","4",step="0.5") + inp_plain("waste","Extra for waste and settling (%)","10",step="1") + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in'), waste = raw('waste');
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var yd3w = yd3 * (1 + (isNaN(waste) ? 0 : waste) / 100);
  var tons = yd3w * 1.4;
""" + cost_js("yd3w", "yd3w*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3w) + '</b> of gravel (<b>' + fmtWt(tons) + '</b>).<br>That is ' + fmtVol(yd3) + ' before waste, plus ' + (isNaN(waste)?0:waste) + '% extra.' + costTxt;
  r.classList.add('show');""",
  "Cubic yards = length (ft) &times; width (ft) &times; depth (in) &divide; 12 &divide; 27. Tons = cubic yards &times; 1.4, because one cubic yard of gravel weighs about 1.4 tons.",
  "A driveway 40 ft long, 12 ft wide and 4 in deep: 40 &times; 12 &times; 4 &divide; 12 = 160 cubic feet. 160 &divide; 27 = 5.93 cubic yards. Add 10% waste: 5.93 &times; 1.1 = 6.52 cubic yards. 6.52 &times; 1.4 = 9.13 tons of gravel.",
  table(["Depth","Cubic yards per 100 sq ft","Tons per 100 sq ft"],
        [["2 in","0.62","0.86"],["3 in","0.93","1.30"],["4 in","1.23","1.73"],["6 in","1.85","2.59"]]),
  [("How deep should a gravel driveway be?", "Four inches of gravel over a compacted base works for most cars. Use six inches if heavy trucks use the driveway."),
   ("How many tons of gravel do I need?", "Multiply your cubic yards by 1.4. A typical two-car driveway 40 ft by 12 ft at 4 inches deep needs about 9 tons."),
   ("Should I add extra for waste?", "Yes, add 10% for settling, spreading unevenly and edges. This calculator adds it for you."),
   ("What size gravel is best for a driveway?", "A 3/4 inch crushed stone locks together well and drains. Pea gravel looks nice but shifts under tyres.")],
  ["crushed-stone-calculator","sand-calculator","paver-base-calculator","gravel-cost-estimator"],
  ["gravel driveway calculator","how much gravel do I need","gravel tons calculator","driveway gravel cubic yards","gravel cost estimator"])

# 2 Crushed Stone
T("crushed-stone-calculator", "Crushed Stone Calculator",
  "Calculate crushed stone in cubic yards and tons by stone type. Pick granite, limestone or pea gravel and get exact order amounts. Free to use.",
  "Work out how much crushed stone to order for paths, bases and drainage. Pick your stone type, because each one weighs a different amount.",
  inp("length","Area length","ft","m","ft","20") + inp("width","Area width","ft","m","ft","10") + inp("depth","Stone depth","in","cm","in","3",step="0.5") + sel("stone","Stone type",[("1.35","Crushed granite — 1.35 tons per cubic yard",True),("1.5","Crushed limestone — 1.5 tons per cubic yard",False),("1.25","Pea gravel — 1.25 tons per cubic yard",False),("1.4","River rock — 1.4 tons per cubic yard",False)]) + price_input("per ton","per tonne"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in');
  var density = parseFloat(document.getElementById('stone').value);
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var tons = yd3 * density;
""" + cost_js("tons", "tons*0.907185", "per ton", "per tonne") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of crushed stone (<b>' + fmtWt(tons) + '</b>).' + costTxt;
  r.classList.add('show');""",
  "Cubic yards = length (ft) &times; width (ft) &times; depth (in) &divide; 12 &divide; 27. Tons = cubic yards &times; the stone density in tons per cubic yard.",
  "An area 20 ft by 10 ft at 3 in deep with granite: 20 &times; 10 &times; 3 &divide; 12 = 50 cubic feet. 50 &divide; 27 = 1.85 cubic yards. 1.85 &times; 1.35 = 2.50 tons of granite.",
  table(["Stone type","Tons per cubic yard","Best for"],
        [["Crushed granite","1.35","Driveways, paths"],["Crushed limestone","1.50","Bases, drainage"],["Pea gravel","1.25","Garden beds, paths"],["River rock","1.40","Borders, decoration"]]),
  [("How much does a cubic yard of crushed stone weigh?", "It depends on the stone. Granite is about 1.35 tons, limestone about 1.5 tons and pea gravel about 1.25 tons per cubic yard."),
   ("How deep should crushed stone be?", "Use 2 to 3 inches for garden paths and 4 inches for driveways and areas with foot traffic."),
   ("Is crushed stone sold by the ton or the yard?", "Both. Bulk suppliers often sell by the ton, while bagged stone is sold by weight. This calculator gives you both numbers."),
   ("Do I need landscape fabric under stone?", "Yes for garden beds and paths. It stops weeds and keeps the stone from sinking into the soil.")],
  ["gravel-driveway-calculator","sand-calculator","mulch-calculator","paver-base-calculator"],
  ["crushed stone calculator","how much crushed stone do I need","stone tons per cubic yard","crushed granite calculator","pea gravel calculator"])

# 3 Mulch
T("mulch-calculator", "Mulch Calculator",
  "Find how much mulch you need in cubic yards and bags. Enter your bed size and depth to stop guessing at the garden centre. No sign-up needed.",
  "Work out mulch for flower beds and garden borders in cubic yards and bags. A 3 inch layer keeps weeds down and holds moisture in the soil.",
  inp("length","Bed length","ft","m","ft","30") + inp("width","Bed width","ft","m","ft","4") + inp("depth","Mulch depth","in","cm","in","3",step="0.5") + sel("bag","Bag size",[("2","2 cubic foot bag",True),("3","3 cubic foot bag",False),("1.5","1.5 cubic foot bag",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in');
  var bag = parseFloat(document.getElementById('bag').value);
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var bags = Math.ceil(yd3 * 27 / bag);
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of mulch, about <b>' + bags + ' bags</b> (' + bag + ' cu ft each).' + costTxt;
  r.classList.add('show');""",
  "Cubic yards = length (ft) &times; width (ft) &times; depth (in) &divide; 12 &divide; 27. Bags = cubic yards &times; 27 &divide; cubic feet per bag.",
  "A bed 30 ft by 4 ft at 3 in deep: 30 &times; 4 &times; 3 &divide; 12 = 30 cubic feet. 30 &divide; 27 = 1.11 cubic yards. With 2 cubic foot bags: 30 &divide; 2 = 15 bags.",
  table(["Depth","Cubic yards per 100 sq ft","2 cu ft bags per 100 sq ft"],
        [["2 in","0.62","9"],["3 in","0.93","13"],["4 in","1.23","17"],["6 in","1.85","25"]]),
  [("How deep should mulch be?", "Three inches is right for most beds. Less than two inches lets weeds through, and more than four inches can suffocate plant roots."),
   ("How many bags of mulch make a cubic yard?", "A cubic yard is 27 cubic feet, so it takes about 14 two-cubic-foot bags or 9 three-cubic-foot bags."),
   ("Is bulk mulch cheaper than bags?", "Yes, bulk mulch by the cubic yard is usually much cheaper than bags once you need more than about 2 cubic yards."),
   ("How often should I replace mulch?", "Top it up once a year in spring. Mulch breaks down and thins out over the season.")],
  ["topsoil-calculator","compost-calculator","grass-seed-calculator","sod-calculator"],
  ["mulch calculator","how much mulch do I need","mulch cubic yards calculator","mulch bags calculator","garden mulch coverage"])

# 4 Topsoil
T("topsoil-calculator", "Topsoil Calculator",
  "Calculate topsoil in cubic yards and bags for lawns and garden beds. Enter length, width and depth to get the right order amount. Free to use.",
  "Work out how much topsoil you need to level a lawn or fill a raised bed. Enter the area and depth and get cubic yards and bag counts.",
  inp("length","Area length","ft","m","ft","20") + inp("width","Area width","ft","m","ft","15") + inp("depth","Topsoil depth","in","cm","in","6",step="0.5") + sel("bag","Bag size",[("0.75","40 lb bag — 0.75 cubic feet",True),("1","1 cubic foot bag",False),("2","2 cubic foot bag",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in');
  var bag = parseFloat(document.getElementById('bag').value);
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var bags = Math.ceil(yd3 * 27 / bag);
  var tons = yd3 * 1.1;
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of topsoil (<b>' + fmtWt(tons) + '</b>), about <b>' + bags + ' bags</b>.' + costTxt;
  r.classList.add('show');""",
  "Cubic yards = length (ft) &times; width (ft) &times; depth (in) &divide; 12 &divide; 27. One cubic yard of topsoil weighs about 1.1 tons.",
  "An area 20 ft by 15 ft at 6 in deep: 20 &times; 15 &times; 6 &divide; 12 = 150 cubic feet. 150 &divide; 27 = 5.56 cubic yards. With 0.75 cubic foot bags: 150 &divide; 0.75 = 200 bags.",
  table(["Depth","Cubic yards per 100 sq ft","Bags (0.75 cu ft) per 100 sq ft"],
        [["2 in","0.62","23"],["4 in","1.23","45"],["6 in","1.85","67"],["12 in","3.70","134"]]),
  [("How deep should topsoil be for a lawn?", "Four to six inches of topsoil over the subsoil gives grass roots room to grow. Less than that dries out fast."),
   ("How much does a cubic yard of topsoil weigh?", "About 1.1 tons, or roughly 2,200 lb. Wet topsoil weighs more, so order by volume, not weight."),
   ("Bags or bulk topsoil?", "Bags suit small patches. For anything over 2 cubic yards, bulk delivery is far cheaper."),
   ("Can I use topsoil to level a lawn?", "Yes, spread it in thin layers of half an inch at a time and let the grass grow through between layers.")],
  ["mulch-calculator","compost-calculator","sod-calculator","grass-seed-calculator"],
  ["topsoil calculator","how much topsoil do I need","topsoil cubic yards","topsoil bags calculator","lawn topsoil depth"])

# 5 Compost
T("compost-calculator", "Compost Calculator",
  "Work out how much compost you need in cubic yards, bags and weight. Enter your bed size and depth for an exact garden amount. Free to use.",
  "Find the right amount of compost to enrich garden beds and improve soil. Enter the area and depth and get cubic yards, bags and weight.",
  inp("length","Bed length","ft","m","ft","20") + inp("width","Bed width","ft","m","ft","8") + inp("depth","Compost depth","in","cm","in","2",step="0.5") + sel("bag","Bag size",[("1","1 cubic foot bag",True),("2","2 cubic foot bag",False),("0.75","0.75 cubic foot bag",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in');
  var bag = parseFloat(document.getElementById('bag').value);
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var bags = Math.ceil(yd3 * 27 / bag);
  var tons = yd3 * 0.5;
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of compost (<b>' + fmtWt(tons) + '</b>), about <b>' + bags + ' bags</b>.' + costTxt;
  r.classList.add('show');""",
  "Cubic yards = length (ft) &times; width (ft) &times; depth (in) &divide; 12 &divide; 27. One cubic yard of compost weighs about 0.5 tons.",
  "A bed 20 ft by 8 ft at 2 in deep: 20 &times; 8 &times; 2 &divide; 12 = 26.67 cubic feet. 26.67 &divide; 27 = 0.99 cubic yards. With 1 cubic foot bags: 26.67 &divide; 1 = 27 bags.",
  table(["Depth","Cubic yards per 100 sq ft","1 cu ft bags per 100 sq ft"],
        [["1 in","0.31","9"],["2 in","0.62","17"],["3 in","0.93","25"],["4 in","1.23","34"]]),
  [("How deep should compost be?", "Spread 2 to 3 inches over a bed and mix it into the top few inches of soil. One inch works as a yearly top dressing."),
   ("How much does a cubic yard of compost weigh?", "About half a ton, or 1,000 lb. It is much lighter than topsoil or gravel."),
   ("Can I use too much compost?", "Yes. More than 3 to 4 inches mixed in can hold too much water and unbalance nutrients. Stick to the depth above."),
   ("Compost or topsoil for a new bed?", "Use topsoil to build up height and compost to feed the soil. Mix compost into the top layer of topsoil.")],
  ["topsoil-calculator","mulch-calculator","grass-seed-calculator","sod-calculator"],
  ["compost calculator","how much compost do I need","compost cubic yards","compost bags calculator","garden compost amount"])

# 6 Concrete Slab
T("concrete-slab-calculator", "Concrete Slab Calculator",
  "Calculate concrete for a slab in cubic yards and bags. Enter length, width and thickness to get exact amounts for your pour. Try it free now.",
  "Work out how much concrete a patio slab, shed base or garage floor needs. Get cubic yards for a truck order or bag counts for mixing by hand.",
  inp("length","Slab length","ft","m","ft","12") + inp("width","Slab width","ft","m","ft","10") + inp("thickness","Slab thickness","in","cm","in","4",step="0.5") + sel("bag","Bag size",[("0.6","80 lb bag — 0.60 cubic feet",True),("0.45","60 lb bag — 0.45 cubic feet",False),("0.3","40 lb bag — 0.30 cubic feet",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), T = v('thickness','in');
  var yield_ = parseFloat(document.getElementById('bag').value);
  if([L,W,T].some(isNaN) || L <= 0 || W <= 0 || T <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and thickness.'; r.classList.add('show'); return; }
  var cuft = L * W * T / 12;
  var yd3 = cuft / 27;
  var bags = Math.ceil(cuft / yield_);
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of concrete (' + fmtCuFt(cuft) + '), about <b>' + bags + ' bags</b>.' + costTxt;
  r.classList.add('show');""",
  "Volume in cubic feet = length (ft) &times; width (ft) &times; thickness (in) &divide; 12. Cubic yards = cubic feet &divide; 27. Bags = cubic feet &divide; yield per bag.",
  "A slab 12 ft by 10 ft at 4 in thick: 12 &times; 10 &times; 4 &divide; 12 = 40 cubic feet. 40 &divide; 27 = 1.48 cubic yards. With 80 lb bags at 0.60 cubic feet each: 40 &divide; 0.60 = 67 bags.",
  table(["Bag size","Yield per bag","Bags per cubic yard"],
        [["40 lb","0.30 cu ft","90"],["60 lb","0.45 cu ft","60"],["80 lb","0.60 cu ft","45"]]),
  [("How thick should a concrete slab be?", "Four inches is standard for patios and shed bases. Use five to six inches for driveways and garage floors."),
   ("Should I order ready-mix or bags?", "Bags suit jobs under about 1 cubic yard. Above that, a ready-mix truck is cheaper and gives a better finish."),
   ("How many 80 lb bags make a cubic yard?", "Forty-five 80 lb bags make one cubic yard. Sixty 60 lb bags or ninety 40 lb bags do the same."),
   ("Do I need to add extra concrete?", "Yes, add about 10% for spillage and uneven ground. Order a little more rather than running short mid-pour.")],
  ["concrete-footing-calculator","walkway-concrete-calculator","post-hole-concrete-calculator","paver-patio-calculator"],
  ["concrete slab calculator","how much concrete do I need","concrete bags calculator","slab concrete cubic yards","concrete volume calculator"])

# 7 Concrete Footing
T("concrete-footing-calculator", "Concrete Footing Calculator",
  "Calculate concrete for footings in cubic yards and bags. Enter footing length, width and depth for decks, walls and posts. No sign-up needed.",
  "Work out concrete for strip footings under walls, decks and extensions. Enter the footing size and get cubic yards and bag counts.",
  inp("length","Footing length","ft","m","ft","30") + inp("width","Footing width","in","cm","in","12",step="1") + inp("depth","Footing depth","in","cm","in","12",step="1") + sel("bag","Bag size",[("0.6","80 lb bag — 0.60 cubic feet",True),("0.45","60 lb bag — 0.45 cubic feet",False),("0.3","40 lb bag — 0.30 cubic feet",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','in'), D = v('depth','in');
  var yield_ = parseFloat(document.getElementById('bag').value);
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var cuft = L * (W / 12) * (D / 12);
  var yd3 = cuft / 27;
  var bags = Math.ceil(cuft / yield_);
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of concrete (' + fmtCuFt(cuft) + '), about <b>' + bags + ' bags</b>.' + costTxt;
  r.classList.add('show');""",
  "Volume in cubic feet = length (ft) &times; width (in) &divide; 12 &times; depth (in) &divide; 12. Cubic yards = cubic feet &divide; 27. Bags = cubic feet &divide; yield per bag.",
  "A footing 30 ft long, 12 in wide and 12 in deep: 30 &times; 1 &times; 1 = 30 cubic feet. 30 &divide; 27 = 1.11 cubic yards. With 80 lb bags: 30 &divide; 0.60 = 50 bags.",
  table(["Footing size","Cubic feet per 10 ft run","80 lb bags per 10 ft run"],
        [["8 in wide, 8 in deep","4.44","8"],["12 in wide, 12 in deep","10.00","17"],["16 in wide, 12 in deep","13.33","23"],["24 in wide, 12 in deep","20.00","34"]]),
  [("How deep should a footing be?", "Footings usually sit 12 inches deep and below the frost line in cold areas. Check local building rules for your area."),
   ("How wide should a footing be?", "At least twice the width of the wall it carries, and never less than 12 inches wide for a house wall."),
   ("Can I pour footings with bagged concrete?", "Yes for small runs. For long footings over a cubic yard, ready-mix is faster and more consistent."),
   ("How long before I can build on a footing?", "Wait at least 7 days for the concrete to cure enough to carry a load, and 28 days for full strength.")],
  ["concrete-slab-calculator","post-hole-concrete-calculator","walkway-concrete-calculator","retaining-wall-block-calculator"],
  ["concrete footing calculator","footing concrete volume","how much concrete for footing","strip footing calculator","deck footing concrete"])

# 8 Post Hole Concrete
T("post-hole-concrete-calculator", "Post Hole Concrete Bags Calculator",
  "Find how many concrete bags each post hole needs. Enter hole size and count to get total bags and cubic feet for fence posts. Free to use.",
  "Work out concrete for fence and deck post holes. Enter the hole diameter, depth and number of holes to get the total bag count.",
  inp_plain("holes","Number of post holes","6",step="1",minv="1") + inp("diameter","Hole diameter","in","cm","in","12",step="1") + inp("depth","Hole depth","in","cm","in","24",step="1") + sel("bag","Bag size",[("0.6","80 lb bag — 0.60 cubic feet",True),("0.45","60 lb bag — 0.45 cubic feet",False),("0.3","40 lb bag — 0.30 cubic feet",False)]) + price_input("per bag","per bag"),
  """  var holes = raw('holes'), D = v('diameter','in'), Dep = v('depth','in');
  var yield_ = parseFloat(document.getElementById('bag').value);
  if([holes,D,Dep].some(isNaN) || holes <= 0 || D <= 0 || Dep <= 0){ r.innerHTML = 'Please enter positive numbers for holes, diameter and depth.'; r.classList.add('show'); return; }
  var perHole = Math.PI * Math.pow(D / 2 / 12, 2) * (Dep / 12);
  var total = perHole * holes;
  var bagsPerHole = Math.ceil(perHole / yield_);
  var bags = bagsPerHole * holes;
""" + cost_js("bags", "bags", "per bag", "per bag") + """
  r.innerHTML = 'Each hole needs <b>' + fmtCuFt(perHole) + '</b> — about <b>' + bagsPerHole + ' bags</b> per hole.<br>Total for ' + holes + ' holes: <b>' + bags + ' bags</b> (' + fmtCuFt(total) + ').' + costTxt;
  r.classList.add('show');""",
  "Volume per hole = &pi; &times; (diameter &divide; 2)&#178; &times; depth, all in feet. Bags per hole = volume per hole &divide; yield per bag, rounded up.",
  "One hole 12 in wide and 24 in deep: radius is 6 in, or 0.5 ft. 3.1416 &times; 0.5&#178; &times; 2 = 1.57 cubic feet. With 80 lb bags at 0.60 cubic feet: 1.57 &divide; 0.60 = 2.62, so 3 bags per hole.",
  table(["Hole size","Cubic feet per hole","80 lb bags per hole"],
        [["8 in wide, 24 in deep","0.70","2"],["10 in wide, 24 in deep","1.09","2"],["12 in wide, 24 in deep","1.57","3"],["12 in wide, 36 in deep","2.36","4"]]),
  [("How deep should a fence post hole be?", "Dig one third of the post length, and at least 24 inches deep. In cold areas go below the frost line."),
   ("How many bags of concrete per post hole?", "A standard 12 inch wide, 24 inch deep hole takes about 3 bags of 80 lb concrete. Wider or deeper holes take more."),
   ("Should concrete fill the whole hole?", "Fill to about 3 inches below ground level and slope the top away from the post so water runs off."),
   ("Can I use dry concrete mix in a post hole?", "Yes, pour dry mix around the post, add water and let it set. It works well for fence posts.")],
  ["fence-post-calculator","concrete-slab-calculator","concrete-footing-calculator","fence-boards-calculator"],
  ["post hole concrete calculator","concrete bags per post hole","fence post concrete bags","how many bags concrete per post","deck post concrete"])

# 9 Paver Base
T("paver-base-calculator", "Paver Base Calculator",
  "Calculate gravel base for pavers in cubic yards and tons. Enter patio or path size and base depth to get the right amount. No sign-up needed.",
  "Work out the crushed stone base under pavers for patios, paths and driveways. Get cubic yards, tons and the sand bedding amount too.",
  inp("length","Area length","ft","m","ft","15") + inp("width","Area width","ft","m","ft","12") + inp("depth","Base depth","in","cm","in","4",step="0.5") + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in');
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var tons = yd3 * 1.4;
  var sandYd3 = L * W * 1 / 12 / 27;
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of base gravel (<b>' + fmtWt(tons) + '</b>).<br>Plus about <b>' + fmtVol(sandYd3) + '</b> of bedding sand (1 inch layer).' + costTxt;
  r.classList.add('show');""",
  "Base cubic yards = length (ft) &times; width (ft) &times; base depth (in) &divide; 12 &divide; 27. Tons = cubic yards &times; 1.4. Bedding sand uses a 1 inch layer.",
  "A patio 15 ft by 12 ft with a 4 in base: 15 &times; 12 &times; 4 &divide; 12 = 60 cubic feet. 60 &divide; 27 = 2.22 cubic yards. 2.22 &times; 1.4 = 3.11 tons. Bedding sand: 15 &times; 12 &times; 1 &divide; 12 &divide; 27 = 0.56 cubic yards.",
  table(["Use","Base depth","Gravel per 100 sq ft"],
        [["Garden path","4 in","1.23 cubic yards"],["Patio","4 to 6 in","1.23 to 1.85 cubic yards"],["Driveway","6 to 8 in","1.85 to 2.47 cubic yards"]]),
  [("How deep should a paver base be?", "Four inches for patios and paths, and six to eight inches for driveways that carry cars."),
   ("What gravel goes under pavers?", "Crushed stone, often called road base or crusher run, compacts hard and drains well. Do not use pea gravel."),
   ("Do I need sand under pavers?", "Yes, a one inch layer of coarse bedding sand sits on the compacted base and lets you level the pavers."),
   ("Should I compact the base?", "Yes, compact it in layers of two inches at a time with a plate compactor, or the pavers will sink.")],
  ["paver-patio-calculator","paver-sand-calculator","gravel-driveway-calculator","crushed-stone-calculator"],
  ["paver base calculator","how much gravel under pavers","paver base depth","patio base gravel tons","crusher run calculator"])

# 10 Paver Sand
T("paver-sand-calculator", "Paver Sand Calculator",
  "Calculate sand for pavers in cubic yards and bags. Get bedding sand and joint sand amounts for patios, paths and driveways. Try it free now.",
  "Work out both kinds of paver sand: bedding sand under the pavers and joint sand swept between them. Enter your patio size to get both.",
  inp("length","Area length","ft","m","ft","15") + inp("width","Area width","ft","m","ft","12") + inp("bedding","Bedding sand depth","in","cm","in","1",step="0.25") + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), B = v('bedding','in');
  if([L,W,B].some(isNaN) || L <= 0 || W <= 0 || B <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and bedding depth.'; r.classList.add('show'); return; }
  var area = L * W;
  var bedYd3 = area * B / 12 / 27;
  var jointBags = Math.ceil(area / 80);
  var jointLb = jointBags * 50;
""" + cost_js("bedYd3", "bedYd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'Bedding sand: <b>' + fmtVol(bedYd3) + '</b>.<br>Joint sand: about <b>' + jointBags + ' bags</b> of 50 lb polymeric sand (' + fmtLb(jointLb) + ').' + costTxt;
  r.classList.add('show');""",
  "Bedding sand in cubic yards = area (sq ft) &times; bedding depth (in) &divide; 12 &divide; 27. Joint sand bags = area &divide; 80, because one 50 lb bag fills joints over about 80 sq ft.",
  "A patio 15 ft by 12 ft with 1 in of bedding sand: area is 180 sq ft. Bedding sand is 180 &times; 1 &divide; 12 &divide; 27 = 0.56 cubic yards. Joint sand is 180 &divide; 80 = 2.25, so 3 bags of 50 lb polymeric sand.",
  table(["Area","Bedding sand (1 in)","Joint sand (50 lb bags)"],
        [["100 sq ft","0.31 cubic yards","2 bags"],["200 sq ft","0.62 cubic yards","3 bags"],["400 sq ft","1.23 cubic yards","5 bags"],["600 sq ft","1.85 cubic yards","8 bags"]]),
  [("What is the difference between bedding sand and joint sand?", "Bedding sand is coarse sand under the pavers for levelling. Joint sand is fine polymeric sand swept into the gaps to lock pavers together."),
   ("How much joint sand do I need?", "One 50 lb bag of polymeric sand covers about 80 square feet of standard pavers. Wider joints need more."),
   ("Can I use regular sand for paver joints?", "It works for a while, but weeds grow through it and rain washes it out. Polymeric sand hardens and lasts far longer."),
   ("How deep should bedding sand be?", "One inch, screeded level. More than that lets pavers shift and sink underfoot.")],
  ["paver-base-calculator","paver-patio-calculator","sand-calculator","brick-calculator"],
  ["paver sand calculator","how much sand for pavers","polymeric sand calculator","paver joint sand bags","bedding sand calculator"])

# 11 Brick
T("brick-calculator", "Brick Calculator",
  "Calculate bricks for a wall or paver area, plus mortar bags. Enter wall size and get brick counts with waste included. Free and easy to use.",
  "Work out how many bricks a wall, planter or paver area needs. Includes a 5% waste allowance and the mortar bags to lay them.",
  inp("length","Wall length","ft","m","ft","20") + inp("height","Wall height","ft","m","ft","4") + sel("brick","Brick size",[("7","Standard brick — 7 bricks per sq ft",True),("4.5","Large brick — 4.5 bricks per sq ft",False),("10","Thin brick — 10 bricks per sq ft",False)]) + price_input("per brick","per brick"),
  """  var L = v('length','ft'), H = v('height','ft');
  var perSqft = parseFloat(document.getElementById('brick').value);
  if([L,H].some(isNaN) || L <= 0 || H <= 0){ r.innerHTML = 'Please enter positive numbers for length and height.'; r.classList.add('show'); return; }
  var area = L * H;
  var bricks = Math.ceil(area * perSqft * 1.05);
  var mortar = Math.ceil(bricks / 40);
""" + cost_js("bricks", "bricks", "per brick", "per brick") + """
  r.innerHTML = 'Wall area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + bricks + ' bricks</b> (with 5% waste) and about <b>' + mortar + ' bags</b> of 60 lb mortar.' + costTxt;
  r.classList.add('show');""",
  "Bricks = wall area (sq ft) &times; bricks per square foot &times; 1.05 for waste. Mortar bags = bricks &divide; 40, because one 60 lb bag lays about 40 bricks.",
  "A wall 20 ft long and 4 ft high with standard bricks: area is 80 sq ft. 80 &times; 7 = 560 bricks. With 5% waste: 560 &times; 1.05 = 588 bricks. Mortar: 588 &divide; 40 = 14.7, so 15 bags.",
  table(["Brick type","Bricks per sq ft","Mortar per 100 bricks"],
        [["Standard brick","7","2.5 bags"],["Large brick","4.5","2 bags"],["Thin brick","10","2 bags"]]),
  [("How many bricks are in a square foot?", "About 7 standard bricks with mortar joints. Large bricks need about 4.5 and thin bricks about 10 per square foot."),
   ("How much mortar do I need?", "One 60 lb bag of mortar lays about 40 standard bricks. Divide your brick count by 40 to get the bags."),
   ("Should I add waste bricks?", "Yes, add 5% for cuts and breakage, and 10% if the wall has lots of corners or curves."),
   ("How many bricks are on a pallet?", "A standard pallet holds about 500 bricks. Check with your supplier, as counts vary by brick size.")],
  ["retaining-wall-block-calculator","paver-patio-calculator","concrete-footing-calculator","grout-calculator"],
  ["brick calculator","how many bricks do I need","bricks per square foot","brick wall calculator","mortar bags calculator"])

# 12 Sod
T("sod-calculator", "Sod Calculator",
  "Calculate sod rolls and pallets for a new lawn. Enter lawn size to get coverage, rolls and pallets with waste included. Free and easy to use.",
  "Work out how much sod your lawn needs in square feet, rolls and pallets. Includes 5% extra for cuts and odd shapes.",
  inp("length","Lawn length","ft","m","ft","40") + inp("width","Lawn width","ft","m","ft","25") + inp_plain("waste","Extra for cuts and waste (%)","5",step="1") + price_input("per roll","per roll"),
  """  var L = v('length','ft'), W = v('width','ft'), waste = raw('waste');
  if([L,W].some(isNaN) || L <= 0 || W <= 0){ r.innerHTML = 'Please enter positive numbers for length and width.'; r.classList.add('show'); return; }
  var area = L * W * (1 + (isNaN(waste) ? 0 : waste) / 100);
  var rolls = Math.ceil(area / 10);
  var pallets = Math.ceil(area / 500);
""" + cost_js("rolls", "rolls", "per roll", "per roll") + """
  r.innerHTML = 'Lawn area with waste: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + rolls + ' rolls</b> of sod (10 sq ft each), about <b>' + pallets + ' pallets</b>.' + costTxt;
  r.classList.add('show');""",
  "Area = length (ft) &times; width (ft) &times; 1.05 for waste. Rolls = area &divide; 10, because one sod roll covers 10 sq ft. Pallets = area &divide; 500.",
  "A lawn 40 ft by 25 ft: area is 1,000 sq ft. With 5% waste: 1,000 &times; 1.05 = 1,050 sq ft. Rolls: 1,050 &divide; 10 = 105 rolls. Pallets: 1,050 &divide; 500 = 2.1, so 3 pallets.",
  table(["Lawn size","Sod needed (with 5% waste)","Rolls"],
        [["500 sq ft","525 sq ft","53"],["1,000 sq ft","1,050 sq ft","105"],["2,000 sq ft","2,100 sq ft","210"],["5,000 sq ft","5,250 sq ft","525"]]),
  [("How big is a roll of sod?", "A standard roll is 2 ft by 5 ft, covering 10 square feet. Some suppliers sell slabs of 16 by 24 inches instead."),
   ("How much sod is on a pallet?", "A pallet usually covers about 500 square feet, or 50 rolls. Large pallets can cover 600 square feet."),
   ("How much waste should I allow for sod?", "Allow 5% for a square lawn and 10% for a lawn with curves, trees or beds to cut around."),
   ("How soon can I walk on new sod?", "Wait two to three weeks for the roots to take hold, and water it daily for the first two weeks.")],
  ["grass-seed-calculator","topsoil-calculator","fertilizer-calculator","mulch-calculator"],
  ["sod calculator","how much sod do I need","sod rolls calculator","sod pallets calculator","lawn sod coverage"])

# 13 Grass Seed
T("grass-seed-calculator", "Grass Seed Calculator",
  "Calculate grass seed in pounds and bags for new lawns and overseeding. Enter lawn size and seed rate to get the exact amount. Free to use.",
  "Work out how much grass seed to buy for a new lawn or to thicken an old one. New lawns need more seed than overseeding.",
  inp("length","Lawn length","ft","m","ft","40") + inp("width","Lawn width","ft","m","ft","25") + sel("rate","Seeding type",[("8","New lawn — 8 lb per 1,000 sq ft",True),("4","Overseeding — 4 lb per 1,000 sq ft",False),("6","Repairing bare patches — 6 lb per 1,000 sq ft",False)]) + price_input("per pound","per kilogram"),
  """  var L = v('length','ft'), W = v('width','ft');
  var rate = parseFloat(document.getElementById('rate').value);
  if([L,W].some(isNaN) || L <= 0 || W <= 0){ r.innerHTML = 'Please enter positive numbers for length and width.'; r.classList.add('show'); return; }
  var area = L * W;
  var lb = area / 1000 * rate;
  var bags = Math.ceil(lb / 5);
""" + cost_js("lb", "lb*0.453592", "per pound", "per kilogram") + """
  r.innerHTML = 'Lawn area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + fmtLb(lb) + '</b> of grass seed, about <b>' + bags + ' bags</b> of 5 lb.' + costTxt;
  r.classList.add('show');""",
  "Seed in pounds = lawn area (sq ft) &divide; 1,000 &times; seed rate in pounds per 1,000 sq ft. New lawns use 8 lb, overseeding uses 4 lb.",
  "A lawn 40 ft by 25 ft as a new lawn: area is 1,000 sq ft. 1,000 &divide; 1,000 &times; 8 = 8 lb of seed. That is 8 &divide; 5 = 1.6, so 2 bags of 5 lb.",
  table(["Job","Seed per 1,000 sq ft","Seed for 1,000 sq ft lawn"],
        [["New lawn","8 lb","8 lb"],["Overseeding","4 lb","4 lb"],["Bare patch repair","6 lb","6 lb"]]),
  [("How much grass seed do I need?", "A new lawn needs about 8 lb per 1,000 square feet. Overseeding an existing lawn needs about 4 lb per 1,000 square feet."),
   ("What happens if I sow too much seed?", "Seedlings crowd each other, stay weak and die off. More seed does not make a thicker lawn."),
   ("When is the best time to sow grass seed?", "Early autumn or spring, when the soil is warm and rain is regular. Avoid hot dry summer weeks."),
   ("How long until grass seed grows?", "Most seed germinates in 7 to 14 days. Keep the soil damp every day until the new grass is about 3 inches tall.")],
  ["sod-calculator","fertilizer-calculator","topsoil-calculator","compost-calculator"],
  ["grass seed calculator","how much grass seed do I need","grass seed per square foot","lawn seed coverage","overseeding calculator"])

# 14 Fertilizer
T("fertilizer-calculator", "Fertilizer Coverage Calculator",
  "Calculate fertilizer bags for your lawn size. Enter the area and bag coverage to get bags and total weight fast. Get instant results free.",
  "Work out how many bags of fertilizer your lawn needs. Enter the lawn area and the coverage printed on the bag.",
  inp("length","Lawn length","ft","m","ft","40") + inp("width","Lawn width","ft","m","ft","25") + inp_plain("coverage","One bag covers (sq ft)","5000",step="100",minv="1") + sel("bagwt","Bag weight",[("20","20 lb bag",True),("15","15 lb bag",False),("25","25 lb bag",False)]) + price_input("per bag","per bag"),
  """  var L = v('length','ft'), W = v('width','ft'), cov = raw('coverage');
  var bagwt = parseFloat(document.getElementById('bagwt').value);
  if([L,W,cov].some(isNaN) || L <= 0 || W <= 0 || cov <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and bag coverage.'; r.classList.add('show'); return; }
  var area = L * W;
  var bags = Math.ceil(area / cov);
  var totalLb = bags * bagwt;
""" + cost_js("bags", "bags", "per bag", "per bag") + """
  r.innerHTML = 'Lawn area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + bags + ' bags</b> of fertilizer (' + fmtLb(totalLb) + ' total).' + costTxt;
  r.classList.add('show');""",
  "Bags = lawn area (sq ft) &divide; coverage per bag (sq ft), rounded up. Total weight = bags &times; weight per bag.",
  "A lawn 40 ft by 25 ft with bags covering 5,000 sq ft: area is 1,000 sq ft. 1,000 &divide; 5,000 = 0.2, so 1 bag. With 20 lb bags, that is 20 lb of fertilizer.",
  table(["Lawn size","Bags at 5,000 sq ft coverage","Bags at 10,000 sq ft coverage"],
        [["1,000 sq ft","1","1"],["5,000 sq ft","1","1"],["10,000 sq ft","2","1"],["20,000 sq ft","4","2"]]),
  [("How do I know a bag's coverage?", "It is printed on the bag label as square feet covered. Most lawn fertilizer bags cover 5,000 to 15,000 square feet."),
   ("How often should I fertilize my lawn?", "Three to four times a year in spring, early summer, late summer and autumn. Follow the label for your grass type."),
   ("Can too much fertilizer burn the lawn?", "Yes. Over-applying burns grass and leaves brown patches. Measure your lawn and stick to the bag rate."),
   ("Should I water after fertilizing?", "Yes, water lightly after spreading granular fertilizer so it reaches the soil and starts working.")],
  ["grass-seed-calculator","sod-calculator","topsoil-calculator","mulch-calculator"],
  ["fertilizer calculator","how much fertilizer do I need","lawn fertilizer coverage","fertilizer bags calculator","lawn feed calculator"])

# 15 Board Foot
T("board-foot-calculator", "Board Foot Calculator",
  "Calculate board feet for lumber. Enter thickness, width, length and pieces to get total board feet for pricing and ordering. Try it free now.",
  "Work out board feet, the standard way lumber is measured and priced. Enter the board size and count to get the total.",
  inp("thickness","Board thickness","in","cm","in","2",step="0.25") + inp("width","Board width","in","cm","in","6",step="0.25") + inp("length","Board length","ft","m","ft","8",step="0.5") + inp_plain("pieces","Number of boards","10",step="1",minv="1") + price_input("per board foot","per board foot"),
  """  var T = v('thickness','in'), W = v('width','in'), L = v('length','ft'), n = raw('pieces');
  if([T,W,L,n].some(isNaN) || T <= 0 || W <= 0 || L <= 0 || n <= 0){ r.innerHTML = 'Please enter positive numbers for all values.'; r.classList.add('show'); return; }
  var perBoard = T * W * L / 12;
  var total = perBoard * n;
""" + cost_js("total", "total", "per board foot", "per board foot") + """
  r.innerHTML = 'Each board is <b>' + perBoard.toFixed(2) + ' board feet</b>.<br>Total for ' + n + ' boards: <b>' + total.toFixed(2) + ' board feet</b>.' + costTxt;
  r.classList.add('show');""",
  "Board feet per board = thickness (in) &times; width (in) &times; length (ft) &divide; 12. Total = board feet per board &times; number of boards.",
  "A 2 in by 6 in board, 8 ft long: 2 &times; 6 &times; 8 &divide; 12 = 8 board feet per board. Ten boards: 8 &times; 10 = 80 board feet.",
  table(["Board size","Length","Board feet per board"],
        [["1 in x 6 in","8 ft","4"],["2 in x 4 in","8 ft","5.33"],["2 in x 6 in","8 ft","8"],["2 in x 10 in","10 ft","16.67"]]),
  [("What is a board foot?", "A board foot is a volume of wood 12 inches by 12 inches by 1 inch thick. It is how hardwood lumber is measured and sold."),
   ("How do I price lumber by board foot?", "Multiply total board feet by the price per board foot. A $5 per board foot price on 80 board feet is $400."),
   ("Is a 2x4 really 2 inches by 4 inches?", "No. A 2x4 is actually 1.5 inches by 3.5 inches after drying and planing. Use the real size in this calculator."),
   ("Do I need to add waste for board feet?", "Yes, add 10% to 15% for cuts, defects and mistakes when ordering lumber for a project.")],
  ["lumber-calculator","decking-calculator","fence-boards-calculator","stair-stringer-calculator"],
  ["board foot calculator","how to calculate board feet","lumber board feet","board feet formula","hardwood board feet calculator"])

# 16 Lumber
T("lumber-calculator", "Lumber Calculator",
  "Calculate how many lumber boards a project needs. Enter total length and board size to get board counts with waste included. Try it free now.",
  "Work out how many boards to buy for framing, shelving or a fence run. Enter the total length you need and the board length.",
  inp("total","Total length needed","ft","m","ft","120") + sel("boardlen","Board length",[("8","8 ft boards",False),("10","10 ft boards",True),("12","12 ft boards",False),("16","16 ft boards",False)]) + inp_plain("waste","Extra for waste and cuts (%)","10",step="1") + price_input("per board","per board"),
  """  var total = v('total','ft');
  var blen = parseFloat(document.getElementById('boardlen').value);
  var waste = raw('waste');
  if([total,blen].some(isNaN) || total <= 0 || blen <= 0){ r.innerHTML = 'Please enter a positive total length.'; r.classList.add('show'); return; }
  var withWaste = total * (1 + (isNaN(waste) ? 0 : waste) / 100);
  var boards = Math.ceil(withWaste / blen);
""" + cost_js("boards", "boards", "per board", "per board") + """
  r.innerHTML = 'Length with waste: <b>' + fmtLenFt(withWaste) + '</b>.<br>You need <b>' + boards + ' boards</b> of ' + blen + ' ft each.' + costTxt;
  r.classList.add('show');""",
  "Length with waste = total length &times; (1 + waste %). Boards = length with waste &divide; board length, rounded up.",
  "You need 120 ft of lumber with 10 ft boards and 10% waste: 120 &times; 1.1 = 132 ft. 132 &divide; 10 = 13.2, so 14 boards.",
  table(["Total length","8 ft boards (10% waste)","12 ft boards (10% waste)"],
        [["50 ft","7","5"],["100 ft","14","10"],["200 ft","28","19"],["500 ft","69","46"]]),
  [("How much extra lumber should I buy?", "Buy 10% extra for straight runs and 15% for jobs with many cuts, angles or short pieces."),
   ("What length boards should I buy?", "Buy the longest boards your project allows. Fewer joints mean a stronger and neater result."),
   ("What is the difference between nominal and actual size?", "A 2x4 is sold as 2 by 4 inches but actually measures 1.5 by 3.5 inches. Plan cuts with the real size."),
   ("Can I mix board lengths?", "Yes, if your design allows joints in different places. It can cut waste on jobs with varied spans.")],
  ["board-foot-calculator","decking-calculator","fence-boards-calculator","stair-stringer-calculator"],
  ["lumber calculator","how many boards do I need","lumber quantity calculator","framing lumber calculator","board count calculator"])

# 17 Stair Stringer
T("stair-stringer-calculator", "Stair Stringer Calculator",
  "Calculate stair steps, riser height and stringer length. Enter total rise and tread depth to get a safe, even staircase. No sign-up needed.",
  "Work out the steps, riser height, total run and stringer length for a staircase. Keeps every step the same height, as building rules require.",
  inp("rise","Total rise (floor to floor)","in","cm","in","36",step="0.5") + inp("riser","Target riser height","in","cm","in","7",step="0.25") + inp("tread","Tread depth","in","cm","in","11",step="0.25"),
  """  var rise = v('rise','in'), target = v('riser','in'), tread = v('tread','in');
  if([rise,target,tread].some(isNaN) || rise <= 0 || target <= 0 || tread <= 0){ r.innerHTML = 'Please enter positive numbers for rise, riser and tread.'; r.classList.add('show'); return; }
  var steps = Math.max(1, Math.round(rise / target));
  var actualRiser = rise / steps;
  var run = steps * tread;
  var stringer = Math.sqrt(rise * rise + run * run);
  r.innerHTML = 'You need <b>' + steps + ' risers</b> at <b>' + fmtLenIn(actualRiser) + '</b> each.<br>Total run: <b>' + fmtLenIn(run) + '</b> (' + steps + ' treads).<br>Stringer length: <b>' + fmtLenIn(stringer) + '</b>.';
  r.classList.add('show');""",
  "Steps = total rise &divide; target riser height, rounded to a whole number. Actual riser = total rise &divide; steps. Total run = steps &times; tread depth. Stringer length = &radic;(rise&#178; + run&#178;).",
  "A total rise of 36 in with a 7 in target riser: 36 &divide; 7 = 5.14, so 5 risers. Actual riser is 36 &divide; 5 = 7.2 in. With 11 in treads, the run is 5 &times; 11 = 55 in. Stringer length is &radic;(36&#178; + 55&#178;) = 65.7 in.",
  table(["Total rise","Steps at 7 in riser","Total run at 11 in tread"],
        [["24 in","3 to 4","33 to 44 in"],["36 in","5","55 in"],["48 in","7","77 in"],["60 in","9","99 in"]]),
  [("What is a good riser height?", "Between 7 and 7.5 inches is comfortable for most people. Building rules usually cap risers at 7.75 inches."),
   ("How deep should stair treads be?", "At least 10 inches, and 11 inches feels best. Shallower treads make stairs feel steep and unsafe."),
   ("Why must all risers be the same height?", "Uneven risers cause trips. Every riser in one flight must match within a small tolerance, usually 3/8 inch."),
   ("How many stringers do I need?", "Use two stringers for stairs up to 36 inches wide and three for wider stairs, so the treads do not flex.")],
  ["decking-calculator","lumber-calculator","board-foot-calculator","drywall-sheet-calculator"],
  ["stair stringer calculator","how many stair steps do I need","stair riser calculator","staircase calculator","stringer length calculator"])

# 18 Decking
T("decking-calculator", "Decking Calculator",
  "Calculate deck boards, fasteners and area for a new deck. Enter deck size and board width to get exact board counts. Free online calculator.",
  "Work out how many deck boards your deck needs, including the gap between boards. Get board counts and total linear feet.",
  inp("length","Deck length","ft","m","ft","16") + inp("width","Deck width","ft","m","ft","12") + inp("boardw","Board width","in","cm","in","5.5",step="0.25") + inp("gap","Gap between boards","in","cm","in","0.25",step="0.125") + sel("boardlen","Board length",[("12","12 ft boards",True),("16","16 ft boards",False),("8","8 ft boards",False)]) + price_input("per board","per board"),
  """  var L = v('length','ft'), W = v('width','ft'), bw = v('boardw','in'), gap = v('gap','in');
  var blen = parseFloat(document.getElementById('boardlen').value);
  if([L,W,bw,gap,blen].some(isNaN) || L <= 0 || W <= 0 || bw <= 0 || blen <= 0){ r.innerHTML = 'Please enter positive numbers for deck size and board width.'; r.classList.add('show'); return; }
  var rows = Math.ceil(W * 12 / (bw + gap));
  var linearFt = rows * L;
  var boards = Math.ceil(linearFt / blen);
  var screws = rows * Math.ceil(L / 1.33) * 2;
""" + cost_js("boards", "boards", "per board", "per board") + """
  r.innerHTML = 'Deck area: <b>' + fmtArea(L * W) + '</b>.<br>You need <b>' + rows + ' rows</b> of boards — <b>' + boards + ' boards</b> of ' + blen + ' ft (' + linearFt.toFixed(0) + ' linear feet), plus about ' + screws + ' screws.' + costTxt;
  r.classList.add('show');""",
  "Rows of boards = deck width in inches &divide; (board width + gap). Total linear feet = rows &times; deck length. Boards = linear feet &divide; board length, rounded up.",
  "A deck 16 ft by 12 ft with 5.5 in boards and a 0.25 in gap: width is 144 in. 144 &divide; 5.75 = 25.04, so 26 rows. Linear feet: 26 &times; 16 = 416 ft. With 12 ft boards: 416 &divide; 12 = 34.7, so 35 boards.",
  table(["Deck size","5.5 in boards (12 ft)","Boards needed"],
        [["10 ft x 10 ft","21 rows","18"],["12 ft x 12 ft","26 rows","26"],["16 ft x 12 ft","26 rows","35"],["20 ft x 16 ft","34 rows","57"]]),
  [("What gap should I leave between deck boards?", "Leave 1/8 to 1/4 inch between boards so water drains and the wood can expand. Wider gaps suit wet climates."),
   ("How many screws per deck board?", "Two screws at every joist. With joists 16 inches apart, a 12 ft board needs about 18 screws."),
   ("Should deck boards run long or short?", "Run boards along the shorter deck dimension when you can, so you use fewer boards and have fewer joints."),
   ("How much extra decking should I buy?", "Buy 10% extra for cuts and bad boards, and 15% if the deck has angles or a picture-frame border.")],
  ["lumber-calculator","board-foot-calculator","stair-stringer-calculator","fence-boards-calculator"],
  ["decking calculator","how many deck boards do I need","deck boards calculator","deck material calculator","deck square feet calculator"])

# 19 Fence Boards
T("fence-boards-calculator", "Fence Boards Calculator",
  "Calculate fence pickets for any fence run. Enter fence length and board width to get picket counts with spacing included. No sign-up needed.",
  "Work out how many fence boards or pickets a fence needs. Enter the run length, board width and any gap between boards.",
  inp("length","Fence length","ft","m","ft","100") + inp("boardw","Board width","in","cm","in","6",step="0.5") + inp("gap","Gap between boards","in","cm","in","0",step="0.25") + inp_plain("waste","Extra for waste (%)","5",step="1") + price_input("per board","per board"),
  """  var L = v('length','ft'), bw = v('boardw','in'), gap = v('gap','in'), waste = raw('waste');
  if([L,bw].some(isNaN) || L <= 0 || bw <= 0 || gap < 0){ r.innerHTML = 'Please enter positive numbers for fence length and board width.'; r.classList.add('show'); return; }
  var boards = Math.ceil(L * 12 / (bw + gap) * (1 + (isNaN(waste) ? 0 : waste) / 100));
  var rails = Math.ceil(L / 8) * 2;
""" + cost_js("boards", "boards", "per board", "per board") + """
  r.innerHTML = 'You need <b>' + boards + ' fence boards</b> (' + fmtLenIn(bw) + ' wide).<br>Plus about <b>' + rails + ' rails</b> (2 per 8 ft section).' + costTxt;
  r.classList.add('show');""",
  "Boards = fence length in inches &divide; (board width + gap) &times; (1 + waste %). Rails = fence length &divide; 8 ft &times; 2 rails per section.",
  "A 100 ft fence with 6 in boards and no gap: 100 &times; 12 = 1,200 in. 1,200 &divide; 6 = 200 boards. With 5% waste: 200 &times; 1.05 = 210 boards. Rails: 100 &divide; 8 = 12.5 sections, so about 26 rails.",
  table(["Fence length","6 in boards, no gap","6 in boards, 1 in gap"],
        [["50 ft","100","86"],["100 ft","200","172"],["150 ft","300","258"],["200 ft","400","343"]]),
  [("How many fence boards do I need?", "Divide the fence length in inches by the board width plus any gap. A 100 ft fence needs about 200 six-inch boards."),
   ("Should fence boards touch or have a gap?", "Privacy fences use no gap. Picket fences use a gap of 1 to 3 inches between boards for a classic look."),
   ("How tall should a fence be?", "Six feet is standard for privacy. Front yard fences are often 3 to 4 feet tall. Check local rules before building."),
   ("How many rails does a fence need?", "Two rails per section for fences up to 5 feet tall, and three rails for 6 foot fences.")],
  ["fence-post-calculator","lumber-calculator","decking-calculator","post-hole-concrete-calculator"],
  ["fence boards calculator","how many fence pickets do I need","fence picket calculator","privacy fence boards","fence material calculator"])

# 20 Fence Post
T("fence-post-calculator", "Fence Post Calculator",
  "Calculate fence posts, spacing and concrete bags. Enter fence length and post spacing to get post counts fast. Get instant results free.",
  "Work out how many fence posts your fence needs and how far apart to set them. Includes concrete bags per post.",
  inp("length","Fence length","ft","m","ft","100") + inp("spacing","Post spacing","ft","m","ft","8",step="0.5") + inp_plain("bagsper","Concrete bags per post (60 lb)","1",step="1",minv="0") + price_input("per post","per post"),
  """  var L = v('length','ft'), S = v('spacing','ft'), bpp = raw('bagsper');
  if([L,S].some(isNaN) || L <= 0 || S <= 0){ r.innerHTML = 'Please enter positive numbers for fence length and spacing.'; r.classList.add('show'); return; }
  var sections = Math.ceil(L / S);
  var posts = sections + 1;
  var bags = posts * (isNaN(bpp) ? 0 : bpp);
""" + cost_js("posts", "posts", "per post", "per post") + """
  r.innerHTML = 'You need <b>' + posts + ' posts</b> (' + sections + ' sections at ' + fmtLenFt(S) + ' spacing).<br>Concrete: about <b>' + bags + ' bags</b> of 60 lb mix.' + costTxt;
  r.classList.add('show');""",
  "Sections = fence length &divide; post spacing, rounded up. Posts = sections + 1. Concrete bags = posts &times; bags per post.",
  "A 100 ft fence with 8 ft spacing: 100 &divide; 8 = 12.5, so 13 sections. Posts: 13 + 1 = 14 posts. With 1 bag per post, that is 14 bags of concrete.",
  table(["Fence length","Posts at 8 ft spacing","Posts at 6 ft spacing"],
        [["50 ft","8","10"],["100 ft","14","18"],["150 ft","20","26"],["200 ft","26","35"]]),
  [("How far apart should fence posts be?", "Six to eight feet apart is standard. Use six feet for tall or heavy fences and windy spots."),
   ("How many posts do I need?", "Divide the fence length by the spacing and add one. A 100 ft fence at 8 ft spacing needs 14 posts."),
   ("How deep should fence posts go?", "One third of the post length, and at least 24 inches deep. Deeper in soft soil or cold areas."),
   ("Do corners need extra posts?", "Each corner and gate needs its own post. Add one post for every corner and two for a gate opening.")],
  ["fence-boards-calculator","post-hole-concrete-calculator","lumber-calculator","concrete-footing-calculator"],
  ["fence post calculator","how many fence posts do I need","fence post spacing calculator","fence posts per foot","fence layout calculator"])

# 21 Paint
T("paint-calculator", "Paint Calculator",
  "Calculate paint in gallons and litres for walls and rooms. Enter wall size and coats to get exact paint amounts. Get instant results free.",
  "Work out how much paint a room or wall needs. Enter the wall area and coats, and get gallons, litres and cans.",
  inp("length","Wall length","ft","m","ft","12") + inp("width","Wall height","ft","m","ft","8") + inp_plain("coats","Number of coats","2",step="1",minv="1") + inp_plain("coverage","Coverage per gallon (sq ft)","350",step="10",minv="1") + price_input("per gallon","per litre"),
  """  var L = v('length','ft'), W = v('width','ft'), coats = raw('coats'), cov = raw('coverage');
  if([L,W,coats,cov].some(isNaN) || L <= 0 || W <= 0 || coats <= 0 || cov <= 0){ r.innerHTML = 'Please enter positive numbers for wall size, coats and coverage.'; r.classList.add('show'); return; }
  var area = L * W;
  var galExact = area * coats / cov;
  var gal = Math.ceil(galExact);
  var buyTxt = UNIT === 'met' ? Math.ceil(galExact * 3.78541) + ' litres' : gal + ' gallon' + (gal > 1 ? 's' : '');
""" + cost_js("gal", "galExact*3.78541", "per gallon", "per litre") + """
  r.innerHTML = 'Wall area: <b>' + fmtArea(area) + '</b> (' + coats + ' coats).<br>You need <b>' + fmtGal(galExact) + '</b> — buy <b>' + buyTxt + '</b>.' + costTxt;
  r.classList.add('show');""",
  "Gallons = wall area (sq ft) &times; coats &divide; coverage per gallon. One gallon of paint covers about 350 sq ft.",
  "A wall 12 ft by 8 ft with 2 coats: area is 96 sq ft. 96 &times; 2 = 192 sq ft to paint. 192 &divide; 350 = 0.55 gallons. Buy 1 gallon.",
  table(["Area to paint","1 coat (350 sq ft/gal)","2 coats (350 sq ft/gal)"],
        [["100 sq ft","0.29 gallons","0.57 gallons"],["200 sq ft","0.57 gallons","1.14 gallons"],["400 sq ft","1.14 gallons","2.29 gallons"],["800 sq ft","2.29 gallons","4.57 gallons"]]),
  [("How much paint do I need per room?", "Measure each wall, add the areas and divide by 350 for one coat. Double it for two coats. A 12 by 12 ft room needs about 2 gallons for two coats."),
   ("Does primer count as a coat?", "No. Primer is a separate coat that seals the surface. Count it apart from your two finish coats."),
   ("How much does a gallon of paint cover?", "About 350 square feet on a smooth wall. Rough or porous walls use more, so coverage drops to about 250 square feet."),
   ("Should I buy extra paint?", "Yes, buy one extra quart for touch-ups later. Paint colours vary slightly between batches.")],
  ["wallpaper-roll-calculator","flooring-tile-calculator","drywall-sheet-calculator","btu-ac-size-calculator"],
  ["paint calculator","how much paint do I need","paint gallons calculator","wall paint coverage","room paint calculator"])

# 22 Wallpaper
T("wallpaper-roll-calculator", "Wallpaper Roll Calculator",
  "Calculate wallpaper rolls for a wall or room. Enter wall size and roll coverage to get roll counts with waste included. Free and easy to use.",
  "Work out how many wallpaper rolls your wall or room needs. Includes 10% extra for pattern matching and cuts.",
  inp("length","Wall length","ft","m","ft","12") + inp("width","Wall height","ft","m","ft","8") + inp_plain("coverage","One roll covers (sq ft)","56",step="1",minv="1") + price_input("per roll","per roll"),
  """  var L = v('length','ft'), W = v('width','ft'), cov = raw('coverage');
  if([L,W,cov].some(isNaN) || L <= 0 || W <= 0 || cov <= 0){ r.innerHTML = 'Please enter positive numbers for wall size and roll coverage.'; r.classList.add('show'); return; }
  var area = L * W;
  var rolls = Math.ceil(area * 1.1 / cov);
""" + cost_js("rolls", "rolls", "per roll", "per roll") + """
  r.innerHTML = 'Wall area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + rolls + ' rolls</b> (with 10% extra for pattern matching).' + costTxt;
  r.classList.add('show');""",
  "Rolls = wall area (sq ft) &times; 1.1 for waste &divide; coverage per roll (sq ft). A standard roll covers about 56 sq ft.",
  "A wall 12 ft by 8 ft with standard rolls: area is 96 sq ft. With 10% waste: 96 &times; 1.1 = 105.6 sq ft. 105.6 &divide; 56 = 1.89, so 2 rolls.",
  table(["Wall area","Rolls at 56 sq ft per roll","Rolls at 35 sq ft per roll"],
        [["100 sq ft","2","4"],["200 sq ft","4","7"],["400 sq ft","8","13"],["800 sq ft","16","26"]]),
  [("How much wallpaper is in a roll?", "A standard US roll is 20.5 inches wide by 33 feet long and covers about 56 square feet. European rolls are often smaller."),
   ("Why add 10% extra wallpaper?", "Pattern matching wastes paper at every join. Large patterns can waste up to 20%, so add more for bold prints."),
   ("Do I need to match the pattern?", "Yes, unless the paper is plain or random. Check the pattern repeat on the label before you buy."),
   ("Can I wallpaper over old wallpaper?", "It is not ideal. Old paper can peel and show through. Strip it first for the best result.")],
  ["paint-calculator","flooring-tile-calculator","drywall-sheet-calculator","btu-ac-size-calculator"],
  ["wallpaper calculator","how many wallpaper rolls do I need","wallpaper rolls per wall","wallpaper coverage calculator","room wallpaper calculator"])

# 23 Flooring / Tile
T("flooring-tile-calculator", "Flooring and Tile Calculator",
  "Calculate floor tiles and boxes for any room. Enter room size and tile size to get tile counts with waste included. Free, fast and accurate.",
  "Work out how many floor tiles a room needs, plus boxes. Enter the room size and tile size, and get counts with 10% waste.",
  inp("length","Room length","ft","m","ft","12") + inp("width","Room width","ft","m","ft","10") + sel("tile","Tile size",[("1","12 x 12 in — 1 sq ft per tile",True),("2.25","18 x 18 in — 2.25 sq ft per tile",False),("4","24 x 24 in — 4 sq ft per tile",False),("0.25","6 x 6 in — 0.25 sq ft per tile",False)]) + inp_plain("perbox","Tiles per box","10",step="1",minv="1") + price_input("per box","per box"),
  """  var L = v('length','ft'), W = v('width','ft');
  var tileArea = parseFloat(document.getElementById('tile').value);
  var perBox = raw('perbox');
  if([L,W,tileArea,perBox].some(isNaN) || L <= 0 || W <= 0 || tileArea <= 0 || perBox <= 0){ r.innerHTML = 'Please enter positive numbers for room size and tiles per box.'; r.classList.add('show'); return; }
  var area = L * W;
  var tiles = Math.ceil(area / tileArea * 1.1);
  var boxes = Math.ceil(tiles / perBox);
""" + cost_js("boxes", "boxes", "per box", "per box") + """
  r.innerHTML = 'Room area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + tiles + ' tiles</b> (with 10% waste), about <b>' + boxes + ' boxes</b>.' + costTxt;
  r.classList.add('show');""",
  "Tiles = room area (sq ft) &divide; area per tile (sq ft) &times; 1.1 for waste. Boxes = tiles &divide; tiles per box, rounded up.",
  "A room 12 ft by 10 ft with 12 by 12 in tiles: area is 120 sq ft. 120 &divide; 1 = 120 tiles. With 10% waste: 120 &times; 1.1 = 132 tiles. At 10 tiles per box: 132 &divide; 10 = 13.2, so 14 boxes.",
  table(["Tile size","Tiles per 100 sq ft (with waste)","Boxes per 100 sq ft (10 per box)"],
        [["6 x 6 in","440","44"],["12 x 12 in","110","11"],["18 x 18 in","49","5"],["24 x 24 in","28","3"]]),
  [("How much extra tile should I buy?", "Buy 10% extra for a straight layout and 15% for a diagonal layout or a room with many corners."),
   ("What size tile is best for a small bathroom?", "Twelve by twelve inch tiles suit most bathrooms. Larger tiles make a small room look bigger but need more cuts."),
   ("Do I count the area under cabinets?", "No, skip the area under fixed cabinets and baths. Measure only the floor you will see and walk on."),
   ("How many tiles are in a box?", "It varies by tile size, often 8 to 12 tiles. Check the box label and enter that number in the calculator.")],
  ["grout-calculator","paint-calculator","drywall-sheet-calculator","paver-patio-calculator"],
  ["tile calculator","how many tiles do I need","floor tile calculator","tiles per square foot","flooring calculator"])

# 24 Grout
T("grout-calculator", "Grout Calculator",
  "Calculate grout bags for tiled floors and walls. Enter tile area, tile size and joint width to get the grout you need. Free and easy to use.",
  "Work out how much grout your tiling job needs. Enter the area, tile size and joint width to get 25 lb bag counts.",
  inp("length","Tiled length","ft","m","ft","12") + inp("width","Tiled width","ft","m","ft","10") + inp("tile","Tile size","in","cm","in","12",step="1") + inp("joint","Grout joint width","in","cm","in","0.125",step="0.0625") + price_input("per 25 lb bag","per 25 lb bag"),
  """  var L = v('length','ft'), W = v('width','ft'), tile = v('tile','in'), joint = v('joint','in');
  if([L,W,tile,joint].some(isNaN) || L <= 0 || W <= 0 || tile <= 0 || joint <= 0){ r.innerHTML = 'Please enter positive numbers for all values.'; r.classList.add('show'); return; }
  var area = L * W;
  var coverage = 150 * (tile / 12) * (0.125 / joint);
  var bags = Math.ceil(area / coverage);
  var lb = bags * 25;
""" + cost_js("bags", "bags", "per 25 lb bag", "per 25 lb bag") + """
  r.innerHTML = 'Tiled area: <b>' + fmtArea(area) + '</b>.<br>One 25 lb bag covers about ' + coverage.toFixed(0) + ' sq ft here.<br>You need <b>' + bags + ' bags</b> of grout (' + fmtLb(lb) + ').' + costTxt;
  r.classList.add('show');""",
  "Coverage per 25 lb bag = 150 sq ft &times; (tile size &divide; 12) &times; (0.125 &divide; joint width). Bags = area &divide; coverage, rounded up.",
  "A floor 12 ft by 10 ft with 12 in tiles and 1/8 in joints: area is 120 sq ft. Coverage is 150 &times; 1 &times; 1 = 150 sq ft per bag. 120 &divide; 150 = 0.8, so 1 bag of 25 lb grout.",
  table(["Tile size","Joint width","Coverage per 25 lb bag"],
        [["6 in","1/8 in","75 sq ft"],["12 in","1/8 in","150 sq ft"],["12 in","1/4 in","75 sq ft"],["24 in","1/8 in","300 sq ft"]]),
  [("How much grout do I need?", "One 25 lb bag covers about 150 square feet of 12 inch tile with 1/8 inch joints. Smaller tiles and wider joints use more grout."),
   ("Sanded or unsanded grout?", "Use sanded grout for joints wider than 1/8 inch. Use unsanded grout for narrow joints and polished stone that scratches easily."),
   ("How much grout for a bathroom floor?", "A typical 50 square foot bathroom floor with 12 inch tiles needs one 25 lb bag of grout."),
   ("Can I mix grout colours?", "Do not mix different colours or brands. Buy all your grout from one batch so the colour matches.")],
  ["flooring-tile-calculator","brick-calculator","paver-sand-calculator","paint-calculator"],
  ["grout calculator","how much grout do I need","grout coverage calculator","tile grout bags","grout per square foot"])

# 25 Drywall
T("drywall-sheet-calculator", "Drywall Sheet Calculator",
  "Calculate drywall sheets, screws and tape for walls and ceilings. Enter wall size and sheet size to get exact counts. Free, instant results.",
  "Work out how many drywall sheets a room needs, plus screws and joint tape. Enter the wall area and sheet size.",
  inp("length","Wall length","ft","m","ft","12") + inp("height","Wall height","ft","m","ft","8") + sel("sheet","Sheet size",[("32","4 x 8 ft — 32 sq ft per sheet",True),("48","4 x 12 ft — 48 sq ft per sheet",False),("40","4 x 10 ft — 40 sq ft per sheet",False)]) + price_input("per sheet","per sheet"),
  """  var L = v('length','ft'), H = v('height','ft');
  var sheetArea = parseFloat(document.getElementById('sheet').value);
  if([L,H,sheetArea].some(isNaN) || L <= 0 || H <= 0 || sheetArea <= 0){ r.innerHTML = 'Please enter positive numbers for wall size.'; r.classList.add('show'); return; }
  var area = L * H;
  var sheets = Math.ceil(area / sheetArea * 1.05);
  var screws = sheets * 32;
  var tape = Math.ceil(area / 250);
""" + cost_js("sheets", "sheets", "per sheet", "per sheet") + """
  r.innerHTML = 'Wall area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + sheets + ' sheets</b> of drywall, about <b>' + screws + ' screws</b> and <b>' + tape + ' roll' + (tape > 1 ? 's' : '') + '</b> of joint tape.' + costTxt;
  r.classList.add('show');""",
  "Sheets = wall area (sq ft) &divide; area per sheet (sq ft) &times; 1.05 for waste. Screws = sheets &times; 32. Tape rolls = area &divide; 250 sq ft per roll.",
  "A wall 12 ft by 8 ft with 4 by 8 ft sheets: area is 96 sq ft. 96 &divide; 32 = 3 sheets. With 5% waste: 3 &times; 1.05 = 3.15, so 4 sheets. Screws: 4 &times; 32 = 128. Tape: 96 &divide; 250 = 0.38, so 1 roll.",
  table(["Sheet size","Area per sheet","Sheets per 100 sq ft"],
        [["4 x 8 ft","32 sq ft","4"],["4 x 10 ft","40 sq ft","3"],["4 x 12 ft","48 sq ft","3"]]),
  [("How many drywall sheets do I need?", "Divide the wall area by the sheet area and add 5% waste. A 12 by 8 ft wall needs 4 sheets of 4 by 8 ft drywall."),
   ("What size drywall sheet should I use?", "Four by eight foot sheets suit most rooms. Twelve foot sheets mean fewer joints on long walls but need two people to lift."),
   ("How many screws per drywall sheet?", "About 32 screws per 4 by 8 ft sheet when studs are 16 inches apart. Use more on ceilings."),
   ("How much joint tape do I need?", "One 250 foot roll of tape covers about 250 square feet of wall. Buy one roll per room for most jobs.")],
  ["paint-calculator","wallpaper-roll-calculator","flooring-tile-calculator","lumber-calculator"],
  ["drywall calculator","how many drywall sheets do I need","drywall sheets calculator","drywall screws calculator","sheetrock calculator"])

# 26 BTU AC
T("btu-ac-size-calculator", "BTU AC Size Calculator",
  "Calculate the right air conditioner size in BTU for any room. Enter room size, sun and people to get the correct cooling power. Free to use.",
  "Work out the BTU rating your room needs so the AC cools well without wasting power. Too small struggles, too big wastes money.",
  inp("length","Room length","ft","m","ft","15") + inp("width","Room width","ft","m","ft","12") + inp("ceiling","Ceiling height","ft","m","ft","8",step="0.5") + sel("sun","Sun exposure",[("1","Normal sun",True),("1.1","Very sunny room",False),("0.9","Shaded room",False)]) + inp_plain("people","People in the room","2",step="1",minv="1") + price_input("per unit","per unit"),
  """  var L = v('length','ft'), W = v('width','ft'), H = v('ceiling','ft');
  var sun = parseFloat(document.getElementById('sun').value);
  var people = raw('people');
  if([L,W,H,sun,people].some(isNaN) || L <= 0 || W <= 0 || H <= 0 || people <= 0){ r.innerHTML = 'Please enter positive numbers for room size and people.'; r.classList.add('show'); return; }
  var area = L * W;
  var btu = area * 20 * (H / 8) * sun;
  if(people > 2) btu += (people - 2) * 600;
  var tons = btu / 12000;
  r.innerHTML = 'Room area: <b>' + fmtArea(area) + '</b>.<br>You need about <b>' + Math.round(btu).toLocaleString() + ' BTU</b> (' + tons.toFixed(1) + ' tons of cooling).<br>Buy the nearest standard size at or above this, such as ' + (Math.ceil(btu / 6000) * 6000).toLocaleString() + ' BTU.';
  r.classList.add('show');""",
  "BTU = room area (sq ft) &times; 20 &times; (ceiling height &divide; 8) &times; sun factor. Add 600 BTU for each person above two. One ton of cooling = 12,000 BTU.",
  "A room 15 ft by 12 ft with 8 ft ceilings and normal sun: area is 180 sq ft. 180 &times; 20 = 3,600 BTU. With 2 people, no extra is added. That is 3,600 &divide; 12,000 = 0.3 tons, so buy a 6,000 BTU unit.",
  table(["Room size","BTU needed","AC size to buy"],
        [["100 sq ft","2,000","6,000 BTU"],["150 sq ft","3,000","6,000 BTU"],["300 sq ft","6,000","6,000 to 9,000 BTU"],["500 sq ft","10,000","12,000 BTU"],["700 sq ft","14,000","15,000 BTU"]]),
  [("What BTU do I need for my room?", "Multiply the room area in square feet by 20. A 300 square foot room needs about 6,000 BTU."),
   ("What happens if my AC is too big?", "It cools fast but shuts off before removing humidity, leaving the room cold and clammy. It also wastes power."),
   ("What happens if my AC is too small?", "It runs all day, never reaches the set temperature and wears out faster. Size it right with this calculator."),
   ("Do sunny rooms need a bigger AC?", "Yes, add 10% for very sunny rooms. Shaded rooms need 10% less. Kitchens add about 4,000 BTU for cooking heat.")],
  ["paint-calculator","drywall-sheet-calculator","flooring-tile-calculator","wallpaper-roll-calculator"],
  ["BTU calculator","AC size calculator","air conditioner BTU calculator","what size AC do I need","room BTU calculator"])

# 27 Retaining Wall
T("retaining-wall-block-calculator", "Retaining Wall Block Calculator",
  "Calculate retaining wall blocks, cap blocks and gravel backfill. Enter wall length and height to get exact block counts. No sign-up needed.",
  "Work out how many blocks a retaining wall needs, plus cap blocks and drainage gravel. Enter the wall length and height.",
  inp("length","Wall length","ft","m","ft","20") + inp("height","Wall height","ft","m","ft","3") + sel("block","Block size",[("16","16 in long, 8 in high block",True),("12","12 in long, 6 in high block",False),("18","18 in long, 8 in high block",False)]) + price_input("per block","per block"),
  """  var L = v('length','ft'), H = v('height','ft');
  var blockLen = parseFloat(document.getElementById('block').value);
  var blockH = blockLen === 12 ? 6 : 8;
  if([L,H].some(isNaN) || L <= 0 || H <= 0){ r.innerHTML = 'Please enter positive numbers for wall length and height.'; r.classList.add('show'); return; }
  var perRow = Math.ceil(L * 12 / blockLen);
  var rows = Math.ceil(H * 12 / blockH);
  var blocks = Math.ceil(perRow * rows * 1.05);
  var gravelYd3 = L * H * 1 / 12 / 27 * 0.5;
""" + cost_js("blocks", "blocks", "per block", "per block") + """
  r.innerHTML = 'You need <b>' + blocks + ' blocks</b> (' + rows + ' rows of ' + perRow + ' blocks), plus <b>' + perRow + ' cap blocks</b>.<br>Drainage gravel behind the wall: about <b>' + fmtVol(gravelYd3) + '</b>.' + costTxt;
  r.classList.add('show');""",
  "Blocks per row = wall length in inches &divide; block length. Rows = wall height in inches &divide; block height. Total blocks = per row &times; rows &times; 1.05 for waste.",
  "A wall 20 ft long and 3 ft high with 16 in blocks: blocks per row are 240 &divide; 16 = 15. Rows are 36 &divide; 8 = 4.5, so 5 rows. Total is 15 &times; 5 = 75 blocks. With 5% waste: 75 &times; 1.05 = 78.75, so 79 blocks, plus 15 cap blocks.",
  table(["Wall height","Rows (8 in blocks)","Blocks per 10 ft run (16 in blocks)"],
        [["2 ft","3","24"],["3 ft","5","38"],["4 ft","6","45"],["6 ft","9","68"]]),
  [("How high can I build a retaining wall?", "Most areas allow up to 4 feet without an engineer. Taller walls need engineering and permits, so check local rules."),
   ("Do I need drainage behind a retaining wall?", "Yes. Put 12 inches of gravel behind the wall and a drain pipe at the base, or water pressure will push the wall over."),
   ("Should the first row of blocks be buried?", "Yes, bury the first row about 6 inches deep so the wall sits solid and does not slide forward."),
   ("What is the base for a retaining wall?", "A 6 inch layer of compacted gravel under the first row. Never set blocks straight on soil.")],
  ["brick-calculator","concrete-footing-calculator","gravel-driveway-calculator","paver-base-calculator"],
  ["retaining wall calculator","how many retaining wall blocks do I need","retaining wall block calculator","block wall calculator","garden wall blocks"])

# 28 Paver Patio
T("paver-patio-calculator", "Paver Patio Calculator",
  "Calculate pavers for a patio in pavers, base gravel and sand. Enter patio size and paver size to get the full material list. Try it free now.",
  "Work out everything a paver patio needs: pavers, base gravel and joint sand. Enter the patio size and paver size.",
  inp("length","Patio length","ft","m","ft","15") + inp("width","Patio width","ft","m","ft","12") + sel("paver","Paver size",[("1","12 x 12 in — 1 sq ft per paver",True),("0.25","6 x 6 in — 0.25 sq ft per paver",False),("0.5","6 x 12 in — 0.5 sq ft per paver",False),("2.25","18 x 18 in — 2.25 sq ft per paver",False)]) + price_input("per paver","per paver"),
  """  var L = v('length','ft'), W = v('width','ft');
  var paverArea = parseFloat(document.getElementById('paver').value);
  if([L,W,paverArea].some(isNaN) || L <= 0 || W <= 0 || paverArea <= 0){ r.innerHTML = 'Please enter positive numbers for patio size.'; r.classList.add('show'); return; }
  var area = L * W;
  var pavers = Math.ceil(area / paverArea * 1.05);
  var baseYd3 = area * 4 / 12 / 27;
  var jointBags = Math.ceil(area / 80);
""" + cost_js("pavers", "pavers", "per paver", "per paver") + """
  r.innerHTML = 'Patio area: <b>' + fmtArea(area) + '</b>.<br>You need <b>' + pavers + ' pavers</b> (with 5% waste), <b>' + fmtVol(baseYd3) + '</b> of base gravel and <b>' + jointBags + ' bags</b> of joint sand.' + costTxt;
  r.classList.add('show');""",
  "Pavers = patio area (sq ft) &divide; area per paver (sq ft) &times; 1.05 for waste. Base gravel = area &times; 4 in depth &divide; 12 &divide; 27. Joint sand bags = area &divide; 80.",
  "A patio 15 ft by 12 ft with 12 by 12 in pavers: area is 180 sq ft. 180 &divide; 1 = 180 pavers. With 5% waste: 180 &times; 1.05 = 189 pavers. Base gravel: 180 &times; 4 &divide; 12 &divide; 27 = 2.22 cubic yards. Joint sand: 180 &divide; 80 = 2.25, so 3 bags.",
  table(["Patio size","12 in pavers (with waste)","Base gravel (4 in)"],
        [["100 sq ft","105","1.23 cubic yards"],["180 sq ft","189","2.22 cubic yards"],["300 sq ft","315","3.70 cubic yards"],["500 sq ft","525","6.17 cubic yards"]]),
  [("How many pavers do I need?", "Divide the patio area by the area of one paver and add 5% waste. A 180 square foot patio needs 189 twelve-inch pavers."),
   ("How deep should the base be under a patio?", "Four inches of compacted gravel for a patio, and six inches if cars will drive on it."),
   ("What size pavers are best for a patio?", "Twelve by twelve inch pavers are the most popular. Larger pavers mean fewer joints and a faster lay."),
   ("Do I need edging for a paver patio?", "Yes. Edge restraints stop the outer pavers spreading over time. Install them before you lay the pavers.")],
  ["paver-base-calculator","paver-sand-calculator","brick-calculator","gravel-driveway-calculator"],
  ["paver patio calculator","how many pavers do I need","patio pavers calculator","paver patio cost estimator","backyard patio pavers"])

# 29 Walkway Concrete
T("walkway-concrete-calculator", "Walkway Concrete Calculator",
  "Calculate concrete for a walkway in cubic yards and bags. Enter path length, width and thickness for an exact pour amount. No sign-up needed.",
  "Work out concrete for garden paths, sidewalks and walkways. Get cubic yards for a truck or bag counts for mixing by hand.",
  inp("length","Walkway length","ft","m","ft","25") + inp("width","Walkway width","ft","m","ft","3") + inp("thickness","Concrete thickness","in","cm","in","4",step="0.5") + sel("bag","Bag size",[("0.6","80 lb bag — 0.60 cubic feet",True),("0.45","60 lb bag — 0.45 cubic feet",False),("0.3","40 lb bag — 0.30 cubic feet",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), T = v('thickness','in');
  var yield_ = parseFloat(document.getElementById('bag').value);
  if([L,W,T].some(isNaN) || L <= 0 || W <= 0 || T <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and thickness.'; r.classList.add('show'); return; }
  var cuft = L * W * T / 12;
  var yd3 = cuft / 27;
  var bags = Math.ceil(cuft / yield_);
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of concrete (' + fmtCuFt(cuft) + '), about <b>' + bags + ' bags</b>.' + costTxt;
  r.classList.add('show');""",
  "Volume in cubic feet = length (ft) &times; width (ft) &times; thickness (in) &divide; 12. Cubic yards = cubic feet &divide; 27. Bags = cubic feet &divide; yield per bag.",
  "A walkway 25 ft long, 3 ft wide and 4 in thick: 25 &times; 3 &times; 4 &divide; 12 = 25 cubic feet. 25 &divide; 27 = 0.93 cubic yards. With 80 lb bags: 25 &divide; 0.60 = 41.7, so 42 bags.",
  table(["Walkway size","Cubic feet","80 lb bags"],
        [["10 ft x 3 ft, 4 in","10","17"],["25 ft x 3 ft, 4 in","25","42"],["30 ft x 4 ft, 4 in","40","67"],["50 ft x 4 ft, 4 in","67","112"]]),
  [("How thick should a walkway be?", "Four inches is standard for a walkway. Use five inches if it will carry heavy loads or sits on soft ground."),
   ("How wide should a garden walkway be?", "Three feet is comfortable for one person and four feet lets two people walk side by side."),
   ("Should a walkway have control joints?", "Yes, cut joints every 4 to 5 feet so cracks form in the joints instead of across the middle of the path."),
   ("Bags or ready-mix for a walkway?", "Bags work for short paths under a cubic yard. Longer walkways are easier and cheaper with ready-mix.")],
  ["concrete-slab-calculator","concrete-footing-calculator","paver-patio-calculator","gravel-driveway-calculator"],
  ["walkway concrete calculator","how much concrete for a walkway","sidewalk concrete calculator","path concrete calculator","concrete path volume"])

# 30 Sand
T("sand-calculator", "Sand Calculator",
  "Calculate sand in cubic yards, tons and bags. Enter area and depth to get exact amounts for play areas, bedding and filling. Try it free now.",
  "Work out how much sand to order for a sandbox, paver bedding or levelling job. Get cubic yards, tons and bag counts.",
  inp("length","Area length","ft","m","ft","10") + inp("width","Area width","ft","m","ft","8") + inp("depth","Sand depth","in","cm","in","6",step="0.5") + sel("bag","Bag size",[("0.5","50 lb bag — 0.5 cubic feet",True),("1","100 lb bag — 1 cubic foot",False)]) + price_input("per cubic yard","per cubic metre"),
  """  var L = v('length','ft'), W = v('width','ft'), D = v('depth','in');
  var bag = parseFloat(document.getElementById('bag').value);
  if([L,W,D].some(isNaN) || L <= 0 || W <= 0 || D <= 0){ r.innerHTML = 'Please enter positive numbers for length, width and depth.'; r.classList.add('show'); return; }
  var yd3 = L * W * D / 12 / 27;
  var tons = yd3 * 1.3;
  var bags = Math.ceil(yd3 * 27 / bag);
""" + cost_js("yd3", "yd3*0.764555", "per cubic yard", "per cubic metre") + """
  r.innerHTML = 'You need <b>' + fmtVol(yd3) + '</b> of sand (<b>' + fmtWt(tons) + '</b>), about <b>' + bags + ' bags</b>.' + costTxt;
  r.classList.add('show');""",
  "Cubic yards = length (ft) &times; width (ft) &times; depth (in) &divide; 12 &divide; 27. Tons = cubic yards &times; 1.3, because one cubic yard of sand weighs about 1.3 tons.",
  "A sandbox 10 ft by 8 ft at 6 in deep: 10 &times; 8 &times; 6 &divide; 12 = 40 cubic feet. 40 &divide; 27 = 1.48 cubic yards. 1.48 &times; 1.3 = 1.93 tons. With 50 lb bags: 40 &divide; 0.5 = 80 bags.",
  table(["Depth","Cubic yards per 100 sq ft","Tons per 100 sq ft"],
        [["2 in","0.62","0.80"],["4 in","1.23","1.60"],["6 in","1.85","2.41"],["12 in","3.70","4.81"]]),
  [("How much does a cubic yard of sand weigh?", "About 1.3 tons, or 2,600 lb. Wet sand weighs more, so order by volume."),
   ("What kind of sand do I need?", "Play sand for sandboxes, coarse washed sand for paver bedding, and fill sand for levelling low spots."),
   ("How deep should sand be in a sandbox?", "Six inches is enough for play. Deeper sand wastes money and makes the box hard to cover."),
   ("Bags or bulk sand?", "Bags suit small jobs under half a cubic yard. For a sandbox or patio base, bulk delivery is far cheaper.")],
  ["paver-sand-calculator","gravel-driveway-calculator","crushed-stone-calculator","topsoil-calculator"],
  ["sand calculator","how much sand do I need","sand cubic yards calculator","sand tons calculator","sandbox sand calculator"])

# ---- fix: gravel-cost-estimator referenced in related lists but not a tool; replace with sand-calculator
for t in TOOLS:
    t["related"] = ["sand-calculator" if s == "gravel-cost-estimator" else s for s in t["related"]]

GROUPS = [
    ("Driveway &amp; Yard", ["gravel-driveway-calculator","crushed-stone-calculator","sand-calculator","mulch-calculator","topsoil-calculator","compost-calculator"]),
    ("Concrete", ["concrete-slab-calculator","concrete-footing-calculator","post-hole-concrete-calculator","walkway-concrete-calculator"]),
    ("Pavers &amp; Stone", ["paver-base-calculator","paver-sand-calculator","brick-calculator","paver-patio-calculator","retaining-wall-block-calculator","grout-calculator"]),
    ("Wood &amp; Fencing", ["board-foot-calculator","lumber-calculator","stair-stringer-calculator","decking-calculator","fence-boards-calculator","fence-post-calculator"]),
    ("Paint &amp; Flooring", ["paint-calculator","wallpaper-roll-calculator","flooring-tile-calculator","drywall-sheet-calculator"]),
    ("Home Comfort", ["btu-ac-size-calculator","grass-seed-calculator","fertilizer-calculator","sod-calculator"]),
]

def render_tool(t):
    slugs = {x["slug"] for x in TOOLS}
    assert len(t["related"]) == 4, t["slug"]
    for s in t["related"]:
        assert s in slugs and s != t["slug"], (t["slug"], s)
    assert 130 <= len(t["meta"]) <= 150, (t["slug"], len(t["meta"]), t["meta"])
    assert len(t["faqs"]) == 4
    rel = "".join('  <div class="card"><a href="%s.html">%s</a><p>%s</p></div>\n' % (
        s, next(x["title"] for x in TOOLS if x["slug"] == s),
        next(x["lede"] for x in TOOLS if x["slug"] == s).split(".")[0] + ".") for s in t["related"])
    page = PAGE.replace("__TITLE__", t["title"]).replace("__META__", t["meta"])
    page = page.replace("__LEDE__", t["lede"]).replace("__INPUTS__", t["inputs"])
    page = page.replace("__FORMULA__", t["formula"]).replace("__EXAMPLE__", t["example"])
    page = page.replace("__TABLE__", t["table"]).replace("__RELATED__", rel)
    page = page.replace("__FAQHTML__", faq_html(t["faqs"])).replace("__FAQJSON__", faq_json(t["faqs"]))
    page = page.replace("__COMMONJS__", COMMON_JS).replace("__CALC__", t["calc"])
    assert "[META" not in page and "[PAGE" not in page and "__" not in page.replace("__", "XX"), t["slug"]
    return page

for t in TOOLS:
    with open(os.path.join(OUT, t["slug"] + ".html"), "w") as fh:
        fh.write(render_tool(t))

# Landing page
by_slug = {t["slug"]: t for t in TOOLS}
cards = ""
for gname, slugs in GROUPS:
    assert len(slugs) > 0
    cards += "<h2>%s</h2>\n<div class=\"grid\">\n" % gname
    for s in slugs:
        tt = by_slug[s]
        cards += '  <div class="card"><a href="%s.html">%s</a><p>%s</p></div>\n' % (
            s, tt["title"], tt["lede"].split(".")[0] + ".")
    cards += "</div>\n"
assert sum(len(s) for _, s in GROUPS) == 30
assert len({s for _, ss in GROUPS for s in ss}) == 30

landing = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Home, Yard &amp; Construction Calculators | ShezMath</title>
<meta name="description" content="Free home, yard and construction calculators: gravel, concrete, pavers, lumber, paint, flooring and more. Instant answers, no sign-up needed.">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="logo" href="../index.html">ShezMath</a>
    <nav class="main">
      <a href="../index.html">Home</a>
      <a href="index.html">Yard &amp; Home</a>
      <a href="../index.html#gpa">GPA</a>
      <a href="../about.html">About</a>
    </nav>
  </div>
</header>
<main class="wrap">
<h1>Home, Yard &amp; Construction Calculators</h1>
<p class="lede">Thirty free calculators for driveways, concrete, pavers, lumber, paint, flooring and home comfort. Enter your measurements and get exact amounts in seconds.</p>
""" + cards + """
</main>
<footer class="site">
  <div class="wrap">
    <a href="../about.html">About</a>
    <a href="../contact.html">Contact</a>
    <a href="../privacy-policy.html">Privacy Policy</a>
    <a href="../terms.html">Terms</a>
    <a href="../methodology.html">Methodology</a>
    <p>ShezMath — free home, yard and construction calculators. Calculations run in your browser.</p>
  </div>
</footer>
</body>
</html>
"""
with open(os.path.join(OUT, "index.html"), "w") as fh:
    fh.write(landing)

print("Built %d tools + landing" % len(TOOLS))
for t in TOOLS:
    print(t["slug"], "|", t["title"], "|", len(t["meta"]))
