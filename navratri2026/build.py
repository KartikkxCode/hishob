"""नवरात्र उत्सव २०२६ - जमा-खर्च हिशोब PDF साठी HTML तयार करते."""
from collections import OrderedDict
from html import escape
import json

from data import VARGANI, BIG_DONORS, BASE_DATE, BASE_INCOME, BASE_TRANSFER, BASE_NOTE, AFTER_INCOME, RANJEET_INCOME, EXPENSES, DUES, KARTIK_ACTUAL, R

MODE = {"cash": "रोख", "gpay": "ऑनलाइन", "yene": "येणे"}


def r(n):
    if n is None:
        return "—"
    if isinstance(n, float) and not n.is_integer():
        s = f"{n:,.2f}"
    else:
        s = f"{int(round(n)):,}"
    return s


def rs(n):
    return "₹ " + r(n)


# ---------- वर्गणी गणित ----------
pages = []
for p in VARGANI:
    rows = []
    t = dict(total=0, cash=0, gpay=0, yene_orig=0, later_cash=0, later_gpay=0, pending=0, blank=0)
    for e in p["entries"]:
        amt = e["amount"] or 0
        if e["amount"] is None:
            t["blank"] += 1
        t["total"] += amt
        rc = rg = 0
        if e["mode"] == "cash":
            t["cash"] += amt; rc = amt
        elif e["mode"] == "gpay":
            t["gpay"] += amt; rg = amt
        else:
            t["yene_orig"] += amt
            for (_, m, a) in e["later"]:
                if m == "cash":
                    t["later_cash"] += a; rc += a
                else:
                    t["later_gpay"] += a; rg += a
        pend = amt - rc - rg if e["mode"] == "yene" else 0
        t["pending"] += pend
        rows.append(dict(e, rc=rc, rg=rg, pend=pend))
    pages.append(dict(p, rows=rows, t=t))

V = {k: sum(pg["t"][k] for pg in pages) for k in pages[0]["t"]}
V_written = {k: sum(pg["written"][k] for pg in pages) for k in ("total", "cash", "gpay", "yene")}

def tot(items, **kw):
    return sum(e[1] for e in items if all(e[{"mode": 2, "who": 5, "when": 6}[k]] == v for k, v in kw.items()))

big_cash = sum(a for _, a, m in BIG_DONORS if m == "cash")
big_gpay = sum(a for _, a, m in BIG_DONORS if m == "gpay")

# 12/10 पाया
b_in_cash = sum(a for _, a, m in BASE_INCOME if m == "cash")
b_in_gpay = sum(a for _, a, m in BASE_INCOME if m == "gpay")
b_exp_cash = tot(EXPENSES, when="B", mode="cash")
b_exp_gpay = tot(EXPENSES, when="B", mode="gpay")
b_bal_cash = b_in_cash + BASE_TRANSFER - b_exp_cash
b_bal_gpay = b_in_gpay - BASE_TRANSFER - b_exp_gpay
b_bal = b_bal_cash + b_bal_gpay

# 12/10 नंतर
a_in_cash = sum(a for _, a, m, _, _ in AFTER_INCOME if m == "cash")
a_in_gpay = sum(a for _, a, m, _, _ in AFTER_INCOME if m == "gpay")
a_exp_cash = tot(EXPENSES, when="A", mode="cash")
a_exp_gpay = tot(EXPENSES, when="A", mode="gpay")
c_cash = b_bal_cash + a_in_cash - a_exp_cash
c_gpay = b_bal_gpay + a_in_gpay - a_exp_gpay
withdraw = -c_cash if c_cash < 0 else 0
c_cash += withdraw; c_gpay -= withdraw
k_bal = c_cash + c_gpay

k_act_cash, k_act_gpay = KARTIK_ACTUAL["cash"], KARTIK_ACTUAL["gpay"]
k_act = k_act_cash + k_act_gpay
extra = k_act - k_bal   # + = नोंद न झालेली जमा

k_in = b_in_cash + b_in_gpay + a_in_cash + a_in_gpay
k_exp = b_exp_cash + b_exp_gpay + a_exp_cash + a_exp_gpay

r_in = sum(a for _, a, _, _ in RANJEET_INCOME)
r_exp = tot(EXPENSES, when="R")
r_own = r_exp - r_in

dues_total = sum(a for _, a in DUES)
dues_r = sum(a for n, a in DUES if n.startswith("रणजीत"))
dues_vendor = dues_total - dues_r

inc_total = k_in + r_in
exp_total = k_exp + r_exp
cost_total = exp_total + dues_vendor
final = k_act - dues_total
final_after = final + V["pending"]

groups = OrderedDict()
for e in EXPENSES:
    groups.setdefault(e[3], []).append(e)
# ---------- HTML ----------
H = []
w = H.append

def table(head, rows, cls="", foot=None, widths=None):
    out = [f'<table class="{cls}">']
    if widths:
        out.append("<colgroup>" + "".join(f'<col style="width:{x}">' for x in widths) + "</colgroup>")
    out.append("<thead><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
    out.append("</tbody>")
    if foot:
        out.append("<tfoot><tr>" + "".join(f"<td>{c}</td>" for c in foot) + "</tr></tfoot>")
    out.append("</table>")
    return "".join(out)

def badge(mode):
    return f'<span class="b b-{mode}">{MODE[mode]}</span>'

BOX = '<span class="chk"></span>'

def sign(n):
    return ("शिल्लक " if n >= 0 else "तूट ") + rs(abs(n))

w(f"""
<header class="top">
  <div class="shri">॥ श्री ॥</div>
  <h1>नवरात्र उत्सव २०२६</h1>
  <div class="sub">जमा-खर्च हिशोब · वर्गणी दि. 03/10/2026 पासून</div>
  <div class="meta">अहवाल तयार केल्याचा दिनांक: 19/10/2026 · पाया: {BASE_DATE} चा ताळमेळ झालेला हिशोब · त्यानंतरची जमा व खर्च यादी · देणे दारी यादी</div>
</header>

<section class="cards">
  <div class="card"><div class="k">एकूण जमा (मिळालेले)</div><div class="v pos">{rs(inc_total)}</div><div class="s">कार्तिक/शुभम {rs(k_in)} · रणजीत {rs(r_in)}</div></div>
  <div class="card"><div class="k">कार्तिक कडे प्रत्यक्ष शिल्लक</div><div class="v pos">{rs(k_act)}</div><div class="s">ऑनलाइन {rs(k_act_gpay)} · रोख {rs(k_act_cash)}</div></div>
  <div class="card"><div class="k">देणे दारी (अजून द्यायचे)</div><div class="v neg">{rs(dues_total)}</div><div class="s">रणजीत {rs(dues_r)} + इतर {rs(dues_vendor)}</div></div>
  <div class="card"><div class="k">अजून येणे बाकी (वर्गणी)</div><div class="v warn">{rs(V['pending'])}</div><div class="s">+ {V['blank']} नावे रक्कम न लिहिलेली</div></div>
</section>
<div class="note"><b>महत्त्वाचे:</b> प्रत्येक जमा रक्कम (रोख व ऑनलाइन) कार्तिक यांच्याकडून पडताळून घ्यायची आहे. “तपासणी” चौकटीत प्रत्येक नोंद तपासून ✓ करा.</div>
""")

w('<h2>१. कार्तिक यांच्याकडील हिशोब</h2>')
w(table(["तपशील", "रोख", "ऑनलाइन", "एकूण"], [
    [f"<b>{BASE_DATE} च्या हिशोबानुसार शिल्लक</b> (भाग २)", r(b_bal_cash), r(b_bal_gpay), r(b_bal)],
    [f"{BASE_DATE} नंतर आलेली जमा (भाग ३)", f"+{r(a_in_cash)}", f"+{r(a_in_gpay)}", f"+{r(a_in_cash + a_in_gpay)}"],
    [f"{BASE_DATE} नंतरचा खर्च (भाग ४)", f"−{r(a_exp_cash)}", f"−{r(a_exp_gpay)}", f"−{r(a_exp_cash + a_exp_gpay)}"],
    ["ऑनलाइन मधून रोख काढून वापरलेले (अंदाजे)", f"+{r(withdraw)}", f"−{r(withdraw)}", "0"],
    ["<b>हिशोबाप्रमाणे शिल्लक असायला हवी</b>", f"<b>{r(c_cash)}</b>", f"<b>{r(c_gpay)}</b>", f"<b>{r(k_bal)}</b>"],
    ["<b>प्रत्यक्ष शिल्लक (कार्तिक यांच्याकडे)</b>", f"<b>{r(k_act_cash)}</b>", f"<b>{r(k_act_gpay)}</b>", f"<b>{r(k_act)}</b>"],
], cls="sum", foot=["फरक: प्रत्यक्ष − हिशोब", r(k_act_cash - c_cash), r(k_act_gpay - c_gpay), ("+" if extra >= 0 else "") + r(extra)]))
w(f"""<div class="note"><b>या आकड्यांचा अर्थ:</b><ul>
<li>{BASE_DATE} चा हिशोब आधीच जुळला होता: जमा {rs(b_in_cash + b_in_gpay)}, खर्च {rs(b_exp_cash + b_exp_gpay)}, शिल्लक {rs(b_bal)} (रोख {r(b_bal_cash)} + ऑनलाइन {r(b_bal_gpay)}).</li>
<li>त्यानंतर {rs(a_in_cash + a_in_gpay)} जमा आले आणि {rs(a_exp_cash + a_exp_gpay)} खर्च झाले. रोख खर्च रोख जमेपेक्षा जास्त असल्याने सुमारे {rs(withdraw)} ऑनलाइन मधून रोख काढले असे धरले आहे.</li>
<li>हिशोबाप्रमाणे कार्तिक यांच्याकडे {rs(k_bal)} असायला हवेत, पण प्रत्यक्षात {rs(k_act)} आहेत. म्हणजे <b>{rs(abs(extra))} {'जास्त' if extra >= 0 else 'कमी'}</b> आहेत. {'याचा अर्थ 12/10 नंतर आलेली काही जमा (वर्गणी) अजून यादीत लिहिलेली नाही. ती नावे शोधून नोंदवा.' if extra >= 0 else 'याचा अर्थ काही खर्च यादीत लिहायचा राहिला आहे.'}</li>
</ul></div>""")

w('<h3>१.१ रणजीत यांच्याकडील हिशोब</h3>')
w(table(["तपशील", "रक्कम"], [
    ["जमा: अजित करंजकर 22,000 + स्वीकार देशपांडे 10,000", r(r_in)],
    ["खर्च (मंडप, डेकोरेशन आगाऊ, हलगी आगाऊ, मिरवणूक आगाऊ, ट्रॉली, हार)", r(r_exp)],
], cls="sum", foot=["रणजीत यांनी स्वतःच्या खिशातून घातलेले", r(r_own)]))
w(f'<p class="small">देणे दारी यादीत रणजीत यांना {rs(dues_r)} परत द्यायचे लिहिले आहे, पण हिशोबाने {rs(r_own)} होतात. <b>{rs(r_own - dues_r)} चा फरक</b> रणजीत यांच्याशी बोलून तपासा.</p>')

w('<h3>१.२ संपूर्ण उत्सवाचा हिशोब</h3>')
w(table(["तपशील", "रक्कम"], [
    ["एकूण जमा (कार्तिक/शुभम + रणजीत)", r(inc_total)],
    ["एकूण दिलेला खर्च", r(exp_total)],
    ["अजून द्यायचे - विक्रेते / कामे (देणे दारी)", r(dues_vendor)],
    ["<b>उत्सवाचा एकूण खर्च (दिलेला + द्यायचा)</b>", f"<b>{r(cost_total)}</b>"],
    ["अजून द्यायचे - रणजीत यांना परत", r(dues_r)],
], cls="sum", foot=["कार्तिक कडील शिल्लक − सर्व देणे", r(final)]))

# 12/10 पाया
w(f'<h2 class="pb">२. {BASE_DATE} चा हिशोब (पाया)</h2>')
w('<h3>२.१ जमा</h3>')
w(table(["#", "तपशील", "प्रकार", "रक्कम", "तपासणी"], [[i + 1, escape(n), badge(m), r(a), BOX] for i, (n, a, m) in enumerate(BASE_INCOME)],
        cls="num exp", foot=["", "एकूण जमा", "", r(b_in_cash + b_in_gpay), ""]))
for lbl, md in (("२.२ खर्च - ऑनलाइन", "gpay"), ("२.३ खर्च - रोख", "cash")):
    items = [e for e in EXPENSES if e[6] == "B" and e[2] == md]
    w(f'<h3>{lbl}</h3>')
    w(table(["#", "तपशील", "कोणी", "रक्कम"], [[i + 1, escape(e[0]), e[5], r(e[1])] for i, e in enumerate(items)],
            cls="num", foot=["", "एकूण", "", r(sum(e[1] for e in items))]))
w(f'<p class="small">टीप: {BASE_NOTE}.</p>')
w(table(["ताळमेळ", "रोख", "ऑनलाइन"], [
    ["जमा", r(b_in_cash), r(b_in_gpay)],
    ["ऑनलाइन मधून रोख वळवले", f"+{r(BASE_TRANSFER)}", f"−{r(BASE_TRANSFER)}"],
    ["खर्च", f"−{r(b_exp_cash)}", f"−{r(b_exp_gpay)}"],
], cls="sum", foot=[f"{BASE_DATE} ला शिल्लक", r(b_bal_cash), r(b_bal_gpay)]))

# नंतर जमा
w(f'<h2>३. {BASE_DATE} नंतर कार्तिक यांच्याकडे आलेली जमा</h2>')
w(table(["#", "नाव", "प्रकार", "दिनांक", "रक्कम", "तपासणी"], [[i + 1, escape(n), badge(m), d, r(a), BOX] for i, (n, a, m, d, _) in enumerate(AFTER_INCOME)],
        cls="num exp", foot=["", "एकूण", f"रोख {r(a_in_cash)} · ऑनलाइन {r(a_in_gpay)}", "", r(a_in_cash + a_in_gpay), ""]))
w('<h3>रणजीत यांच्याकडे आलेली जमा</h3>')
w(table(["#", "नाव", "तपशील", "रक्कम"], [[i + 1, escape(n), g, r(a)] for i, (n, a, m, g) in enumerate(RANJEET_INCOME)],
        cls="num", foot=["", "एकूण", "", r(r_in)]))

# नंतर खर्च + रणजीत
for title, when in ((f"४. {BASE_DATE} नंतरचा खर्च (कार्तिक)", "A"), ("४.१ रणजीत यांनी केलेला खर्च", "R")):
    items = [e for e in EXPENSES if e[6] == when]
    w(f'<h2>{title}</h2>' if when == "A" else f'<h3>{title}</h3>')
    w(table(["#", "तपशील", "दिनांक", "प्रकार", "रक्कम"], [[i + 1, escape(e[0]), e[4] or "—", badge(e[2]), r(e[1])] for i, e in enumerate(items)],
            cls="num exp", foot=["", "एकूण", "", f"रोख {r(sum(e[1] for e in items if e[2] == 'cash'))} · ऑनलाइन {r(sum(e[1] for e in items if e[2] == 'gpay'))}", r(sum(e[1] for e in items))],
            widths=["6%", "46%", "12%", "20%", "16%"]))

# गटानुसार
w('<h3>४.२ संपूर्ण खर्च - गटानुसार</h3>')
grows = []
for g, items in groups.items():
    a_ = sum(e[1] for e in items)
    grows.append([g, r(sum(e[1] for e in items if e[5] != R)), r(sum(e[1] for e in items if e[5] == R)), r(a_), f"{a_ * 100 / exp_total:.1f}%"])
w(table(["खर्चाचा गट", "कार्तिक/शुभम", "रणजीत", "एकूण", "टक्के"], grows, cls="num",
        foot=["एकूण दिलेला खर्च", r(k_exp), r(r_exp), r(exp_total), "100%"]))
w('<p class="small">दिलेला + द्यायचा मिळून: डेकोरेशन 70,000 (रणजीत 40,000 + कार्तिक 15,000 + बाकी 15,000). मंडप समीर कोळेकर 75,000 (40,000 + बाकी 35,000). हलगी 17,000 (7,000 + 10,000). ट्रॉली ट्रॅक्टर 16,000 (कार्तिक 5,000 + रणजीत 1,000 + बाकी 10,000).</p>')

# देणे दारी
w('<h2>५. देणे दारी (अजून द्यायचे पैसे)</h2>')
w(table(["#", "कोणाला / कशासाठी", "रक्कम"], [[i + 1, escape(n_), r(a)] for i, (n_, a) in enumerate(DUES)],
        cls="num", foot=["", "एकूण देणे", r(dues_total)]))
# दिवसवार सारांश
w('<h2 class="pb">६. वर्गणी वही - दिवसानुसार सारांश (संदर्भासाठी)</h2>')
rows = []
for pg in pages:
    t = pg["t"]; wr = pg["written"]
    rows.append([pg["date"] + (f"<br><small>{pg['title']}</small>" if pg.get("title") else ""), len(pg["rows"]), r(t["total"]), r(t["cash"]), r(t["gpay"]),
                 r(t["later_cash"] + t["later_gpay"]), r(t["pending"]), r(wr["total"])])
w(table(["दिनांक", "नावे", "ठरलेली वर्गणी", "रोख मिळाले", "ऑनलाइन मिळाले", "नंतर जमा", "अजून येणे", "वहीतील एकूण"], rows,
        cls="num", foot=["एकूण", sum(len(p["rows"]) for p in pages), r(V["total"]), r(V["cash"]), r(V["gpay"]),
                          r(V["later_cash"] + V["later_gpay"]), r(V["pending"]), r(V_written["total"])]))
w('<p class="small">“ठरलेली वर्गणी” = नावांसमोर लिहिलेल्या रकमांची बेरीज. “वहीतील एकूण” = प्रत्येक पानाच्या खाली हाताने लिहिलेली बेरीज. दोन्हीतील फरक भाग ९ मध्ये स्पष्ट केला आहे.</p>')

w('<h3>६.१ मोठ्या देणग्या (वहीतील वेगळे पान, संदर्भासाठी)</h3>')
w(table(["#", "नाव", "रक्कम", "प्रकार", "तपासणी"], [[i + 1, escape(n), r(a), badge(m), BOX] for i, (n, a, m) in enumerate(BIG_DONORS)],
        cls="num", foot=["", "एकूण", r(big_cash + big_gpay), f"रोख {r(big_cash)} · ऑनलाइन {r(big_gpay)}", ""]))
w(f'<p class="small">दैनंदिन वही व मोठ्या देणग्या यांची रक्कम {BASE_DATE} च्या हिशोबात (शुभम 17,000 रोख, कार्तिक 19,555 रोख व 11,935 ऑनलाइन) आधीच आली आहे. म्हणून भाग ६ ते ८ फक्त संदर्भ व वसुलीसाठी आहेत; त्यांची रक्कम पुन्हा बेरजेत धरलेली नाही.</p>')
# येणे यादी
w('<h2 class="pb">७. अजून येणे बाकी असलेली वर्गणी (वसुली यादी)</h2>')
rr = []; k = 0
for pg in pages:
    for e in pg["rows"]:
        if e["mode"] == "yene" and (e["pend"] > 0 or e["amount"] is None):
            k += 1
            rr.append([k, escape(e["name"]), pg["date"][:5], r(e["amount"]),
                       r(e["rc"] + e["rg"]) if e["rc"] + e["rg"] else "—",
                       "रक्कम ठरलेली नाही" if e["amount"] is None else r(e["pend"]), escape(e["note"])])
w(table(["#", "नाव", "दिनांक", "ठरलेली", "जमा", "बाकी", "पत्ता / टीप"], rr, cls="num due",
        foot=["", "एकूण बाकी", "", "", "", r(V["pending"]), ""], widths=["5%", "27%", "9%", "10%", "9%", "13%", "27%"]))

# पूर्ण यादी
w('<h2 class="pb">८. दिवसानुसार संपूर्ण वर्गणी यादी</h2>')
w('<p class="small">ज्या नावांवर <span class="q">?</span> आहे, ती नावे किंवा रक्कम हस्ताक्षरामुळे नीट वाचता आली नाही. ती वहीशी पडताळून पहा.</p>')
for pg in pages:
    t = pg["t"]
    w(f'<h3>दिनांक {pg["date"]}{" — " + pg["title"] if pg.get("title") else ""}</h3>')
    rr = []
    for i, e in enumerate(pg["rows"]):
        st = badge(e["mode"])
        later = "; ".join(f'{d} {MODE[m]} {r(a)}' for d, m, a in e["later"])
        if e["mode"] == "yene":
            st = badge("yene") + (f' <span class="lt">→ जमा {later}</span>' if later else "")
        nm = escape(e["name"]) + (' <span class="q">?</span>' if e["unsure"] else "")
        rr.append([i + 1, nm, r(e["amount"]), st, escape(e["note"])])
    w(table(["#", "नाव", "रक्कम", "स्थिती", "टीप"], rr, cls="num list",
            foot=["", "एकूण", r(t["total"]), f'रोख {r(t["cash"] + t["later_cash"])} · ऑनलाइन {r(t["gpay"] + t["later_gpay"])} · बाकी {r(t["pending"])}', ""],
            widths=["5%", "30%", "10%", "30%", "25%"]))

# फरक व गृहीतके
w('<h2 class="pb">९. वहीशी न जुळणाऱ्या बेरजा व घेतलेले निर्णय</h2>')
diff_rows = []
for pg in pages:
    t = pg["t"]; wr = pg["written"]
    parts = wr["cash"] + wr["gpay"] + wr["yene"]
    diff_rows.append([pg["date"], r(wr["total"]), r(parts), r(t["total"]), r(t["total"] - wr["total"])])
w(table(["दिनांक", "वहीत लिहिलेली एकूण", "वहीतील (रोख+ऑनलाइन+येणे)", "नावांची बेरीज", "फरक"], diff_rows, cls="num"))
w("""<div class="note"><ul>
<li><b>03/10:</b> रोख (3,262) व ऑनलाइन (1,709) पूर्ण जुळतात. नावांनुसार येणे 5,316 होते, पण वहीत 5,065 लिहिले आहे (251 कमी). मयुर जगताप (251) किंवा भुवन शेटे (251) यांच्यापैकी एक नाव बेरजेत सुटले असावे. हिशोबात नावांनुसार रक्कम धरली आहे.</li>
<li><b>04/10:</b> रोख, ऑनलाइन व येणे तिन्ही वहीशी पूर्ण जुळतात. प्रफुल्ल देसाई काका (351) सुरुवातीला ‘येणे’ होते, नंतर साईराज कडून ‘Paid’ झाले. ही रक्कम रोख जमा धरली आहे.</li>
<li><b>05/10:</b> पंधारे यांची रक्कम 101 धरली (तुमच्या सांगण्यानुसार). बंटी मोरे यांची वर्गणी 1,001 वरून 500 केली आणि ती 14/10 रोजी रोख जमा झाली. त्यामुळे पानाची बेरीज 501 ने कमी झाली.</li>
<li><b>07/10:</b> क्र. 15 (नाव नाही) = 101 आणि जाधव = 100 धरले. यामुळे रोख 1,511 जुळते. वहीत एकूण 3,974 आणि येणे 1,307 लिहिले आहे, पण नावांनुसार येणे 1,508 आणि एकूण 4,075 होते. वहीत आधी लिहिलेले आणि खोडलेले 4,074 हेच बरोबर दिसते.</li>
<li><b>08/10 (दुकानदार):</b> तुमच्या सांगण्यानुसार पानाच्या एकूणाऐवजी नावांची बेरीज घेतली आहे. जान्हवी फिश 1,001, राजेश कलेक्शन 601 आणि सावरिया भेळ 601 असे वाचले आहे (? चिन्ह). सत्यम कलेक्शन व भवानी मेडिकल यांची रक्कम लिहिलेली नाही.</li>
<li><b>09/10:</b> मधुरा नेर्लेकर = 101 धरले. यामुळे पहिली बेरीज 5,067 बरोबर ठरते.</li>
<li>वहीतील ‘कार्तिक’ व ‘KD’ GPay हे एकच खाते (कार्तिक दहाळे) धरले आहे.</li>
<li>वहीतील 19,555 रोख, 3,205 ऑनलाइन आणि 25,000 + 32,000 हे आकडे त्या वेळचे ताळमेळ (हातातील शिल्लक) दिसतात. ते जमा म्हणून वेगळे धरलेले नाहीत.</li>
<li><b>ऑनलाइन पडताळणी:</b> वहीतील रक्कम प्रथम धरली आहे. काही ‘येणे’ नंतर ऑनलाइन आले, पण वहीत जमा म्हणून लिहिले गेले नव्हते. ते आता जमा केले आहेत: तुंगे काकू 700 (16/10), प्रसाद दादा 301 (16/10), आशिष बारे 251 (11/10). शौर्य दिघे (201) व गवळी काकू (301) यांचे पैसे 10/10 रोजी ऑनलाइन आले.</li>
<li><b>वहीपेक्षा कमी दिलेले:</b> प्रसन्न साळुंके 1,000 (वहीत 1,001; 501 बाकी), तुंगे काकू 700 (वहीत 701), गवळी काकू 301 (वहीत 351).</li>
<li><b>03/10 ऑनलाइन:</b> वहीत 1,709 GPay लिहिले आहे, पण GPay वर 1,205 च आलेले दिसतात. संजूकाका जाधव (501) यांचे पैसे दिसत नाहीत आणि दोघांनी 201 ऐवजी 200 दिले. हिशोबात वहीची रक्कम धरली आहे; संजूकाका यांच्याकडे खात्री करा.</li>
<li>योगेश दादा (1,001) व मोरे काकू (1,001) यांनी रोख दिले (तुमच्या सांगण्यानुसार). सूरज लोखंडे (4,000) व आपटे कॉलनी असोसिएशन (5,000) यांचे पैसे रोख धरले.</li>
</ul></div>""")

w(f"""<h2>१०. अंतिम ताळेबंद</h2>
<table class="final"><tbody>
<tr><td>{BASE_DATE} ला शिल्लक</td><td>{rs(b_bal)}</td></tr>
<tr><td>नंतर आलेली जमा</td><td>{rs(a_in_cash + a_in_gpay)}</td></tr>
<tr><td>नंतरचा खर्च</td><td>{rs(a_exp_cash + a_exp_gpay)}</td></tr>
<tr><td>हिशोबाप्रमाणे शिल्लक</td><td>{rs(k_bal)}</td></tr>
<tr class="hl"><td>कार्तिक यांच्याकडे प्रत्यक्ष शिल्लक</td><td>{rs(k_act)}</td></tr>
<tr><td>नोंद न झालेली जमा (शोधायची)</td><td>{rs(extra)}</td></tr>
<tr><td>देणे दारी (रणजीत {r(dues_r)} + इतर {r(dues_vendor)})</td><td>{rs(dues_total)}</td></tr>
<tr class="hl"><td>देणे दिल्यानंतर</td><td>{sign(final)}</td></tr>
<tr><td>अजून वसूल करायची वर्गणी</td><td>{rs(V['pending'])}</td></tr>
<tr class="hl"><td>सर्व येणे वसूल झाल्यावर</td><td>{sign(final_after)}</td></tr>
</tbody></table>
<div class="sign"><div>हिशोब तपासणारे<br><br>__________________</div><div>खजिनदार<br><br>__________________</div><div>अध्यक्ष<br><br>__________________</div></div>
""")

CSS = open("style.css", encoding="utf-8").read()
html = f"""<!doctype html><html lang="mr"><head><meta charset="utf-8"><title>नवरात्र उत्सव २०२६ - हिशोब</title><style>{CSS}</style></head><body>{''.join(H)}</body></html>"""
open("hishob.html", "w", encoding="utf-8").write(html)

print(json.dumps(dict(b_bal_cash=b_bal_cash, b_bal_gpay=b_bal_gpay, a_in=a_in_cash + a_in_gpay, a_exp=a_exp_cash + a_exp_gpay,
                      withdraw=withdraw, c_cash=c_cash, c_gpay=c_gpay, k_bal=k_bal, extra=extra, r_own=r_own,
                      inc_total=inc_total, exp_total=exp_total, final=final, pending=V["pending"], final_after=final_after), ensure_ascii=False, indent=1))
