"""नवरात्र उत्सव २०२६ - जमा-खर्च हिशोब PDF साठी HTML तयार करते."""
from collections import OrderedDict
from html import escape
import json

from data import VARGANI, BIG_DONORS, OTHER_INCOME, RANJEET_INCOME, EXPENSES, DUES, KARTIK_ACTUAL

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

K, R = "कार्तिक", "रणजीत"
big_cash = sum(a for _, a, m in BIG_DONORS if m == "cash")
big_gpay = sum(a for _, a, m in BIG_DONORS if m == "gpay")
oth_cash = sum(a for _, a, m, _ in OTHER_INCOME if m == "cash")
oth_gpay = sum(a for _, a, m, _ in OTHER_INCOME if m == "gpay")

k_in_cash = V["cash"] + V["later_cash"] + big_cash + oth_cash
k_in_gpay = V["gpay"] + V["later_gpay"] + big_gpay + oth_gpay
k_in = k_in_cash + k_in_gpay
k_exp_cash = sum(e[1] for e in EXPENSES if e[5] == K and e[2] == "cash")
k_exp_gpay = sum(e[1] for e in EXPENSES if e[5] == K and e[2] == "gpay")
k_exp = k_exp_cash + k_exp_gpay
k_bal_cash = k_in_cash - k_exp_cash
k_bal_gpay = k_in_gpay - k_exp_gpay
k_bal = k_in - k_exp
k_act_cash, k_act_gpay = KARTIK_ACTUAL["cash"], KARTIK_ACTUAL["gpay"]
k_act = k_act_cash + k_act_gpay
miss_cash, miss_gpay = k_bal_cash - k_act_cash, k_bal_gpay - k_act_gpay
# रोख खर्च रोख जमेपेक्षा जास्त असेल तर तो फरक ऑनलाइन मधून रोख काढून भरला असे धरले
withdraw = 0
if miss_cash < 0 and miss_gpay > 0:
    withdraw = min(-miss_cash, miss_gpay)
    miss_cash += withdraw; miss_gpay -= withdraw
miss = miss_cash + miss_gpay

r_in = sum(a for _, a, _, _ in RANJEET_INCOME)
r_exp = sum(e[1] for e in EXPENSES if e[5] == R)
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

# मुखपृष्ठ + सारांश
w(f"""
<header class="top">
  <div class="shri">॥ श्री ॥</div>
  <h1>नवरात्र उत्सव २०२६</h1>
  <div class="sub">जमा-खर्च हिशोब · वर्गणी दि. 03/10/2026 पासून</div>
  <div class="meta">अहवाल तयार केल्याचा दिनांक: 19/10/2026 · स्रोत: वर्गणी वही (11 पाने), कार्तिक व रणजीत यांची खर्च यादी, देणे दारी यादी</div>
</header>

<section class="cards">
  <div class="card"><div class="k">एकूण जमा (मिळालेले)</div><div class="v pos">{rs(inc_total)}</div><div class="s">कार्तिक {rs(k_in)} · रणजीत {rs(r_in)}</div></div>
  <div class="card"><div class="k">कार्तिक कडे प्रत्यक्ष शिल्लक</div><div class="v pos">{rs(k_act)}</div><div class="s">ऑनलाइन {rs(k_act_gpay)} · रोख {rs(k_act_cash)}</div></div>
  <div class="card" style="display:none"><div class="k">एकूण दिलेला खर्च</div><div class="v neg">{rs(exp_total)}</div><div class="s">कार्तिक {rs(k_exp)} · रणजीत {rs(r_exp)}</div></div>
  <div class="card"><div class="k">देणे दारी (अजून द्यायचे)</div><div class="v neg">{rs(dues_total)}</div><div class="s">रणजीत {rs(dues_r)} + इतर {rs(dues_vendor)}</div></div>
  <div class="card"><div class="k">अजून येणे बाकी (वर्गणी)</div><div class="v warn">{rs(V['pending'])}</div><div class="s">+ {V['blank']} नावे रक्कम न लिहिलेली</div></div>
</section>
""")

w('<div class="note"><b>महत्त्वाचे:</b> प्रत्येक जमा रक्कम (रोख व ऑनलाइन) कार्तिक यांच्याकडून पडताळून घ्यायची आहे. भाग ३ व ७ मधील “तपासणी” चौकटीत प्रत्येक नोंद तपासून ✓ करा.</div>')
w('<h2>१. एकूण सारांश</h2>')
w('<h3>१.१ कार्तिक यांच्याकडील हिशोब (सर्व वर्गणी कार्तिक यांच्याकडे)</h3>')
w(table(["तपशील", "रोख", "ऑनलाइन", "एकूण"], [
    ["दैनंदिन वर्गणी - त्याच दिवशी मिळालेली", r(V['cash']), r(V['gpay']), r(V['cash'] + V['gpay'])],
    ["दैनंदिन वर्गणी - येणे पैकी नंतर जमा", r(V['later_cash']), r(V['later_gpay']), r(V['later_cash'] + V['later_gpay'])],
    ["मोठ्या देणग्या (वेगळे पान)", r(big_cash), r(big_gpay), r(big_cash + big_gpay)],
    ["सभासद वर्गणी व इतर वर्गणी", r(oth_cash), r(oth_gpay), r(oth_cash + oth_gpay)],
    ["<b>कार्तिक - एकूण जमा</b>", f"<b>{r(k_in_cash)}</b>", f"<b>{r(k_in_gpay)}</b>", f"<b>{r(k_in)}</b>"],
    ["<b>कार्तिक - एकूण खर्च</b>", f"<b>{r(k_exp_cash)}</b>", f"<b>{r(k_exp_gpay)}</b>", f"<b>{r(k_exp)}</b>"],
    ["हिशोबाप्रमाणे कार्तिक यांच्याकडे असायला हवे", r(k_bal_cash), r(k_bal_gpay), r(k_bal)],
    ["ऑनलाइन मधून रोख काढून वापरलेले (अंदाजे)", f"+{r(withdraw)}", f"−{r(withdraw)}", "0"],
    ["<b>न लिहिलेला खर्च (यादी अजून यायची आहे)</b>", f"<b>{r(miss_cash)}</b>", f"<b>{r(miss_gpay)}</b>", f"<b>{r(miss)}</b>"],
], cls="sum", foot=["कार्तिक यांच्याकडे प्रत्यक्ष शिल्लक", r(k_act_cash), r(k_act_gpay), r(k_act)]))

w('<h3>१.२ रणजीत यांच्याकडील हिशोब</h3>')
w(table(["तपशील", "रक्कम"], [
    ["जमा: अजित करंजकर 22,000 + स्वीकार देशपांडे 10,000", r(r_in)],
    ["खर्च (मंडप, सजावट आगाऊ, हलगी आगाऊ, मिरवणूक आगाऊ, हार)", r(r_exp)],
], cls="sum", foot=["रणजीत यांनी स्वतःच्या खिशातून घातलेले", r(r_own)]))

w('<h3>१.३ संपूर्ण उत्सवाचा हिशोब</h3>')
w(table(["तपशील", "रक्कम"], [
    ["एकूण जमा (कार्तिक + रणजीत)", r(inc_total)],
    ["एकूण दिलेला खर्च (कार्तिक + रणजीत)", r(exp_total)],
    ["अजून द्यायचे - विक्रेते / कामे (देणे दारी)", r(dues_vendor)],
    ["<b>उत्सवाचा एकूण खर्च (दिलेला + द्यायचा)</b>", f"<b>{r(cost_total)}</b>"],
    ["अजून द्यायचे - रणजीत यांना परत", r(dues_r)],
], cls="sum", foot=["एकूण जमा − उत्सवाचा एकूण खर्च", r(inc_total - cost_total)]))

w(f"""<div class="note">
<b>या आकड्यांचा अर्थ:</b>
<ul>
<li>सर्व वर्गणी कार्तिक यांच्याकडे जमा झाली: रोख {rs(k_in_cash)}, ऑनलाइन {rs(k_in_gpay)}. यादीप्रमाणे त्यांनी {rs(k_exp)} खर्च केले. हिशोबाप्रमाणे त्यांच्याकडे {rs(k_bal)} असायला हवेत.</li>
<li>प्रत्यक्षात कार्तिक यांच्याकडे फक्त <b>{rs(k_act)}</b> आहेत (ऑनलाइन {r(k_act_gpay)} + रोख {r(k_act_cash)}). रोख खर्च रोख जमेपेक्षा जास्त असल्याने सुमारे {rs(withdraw)} ऑनलाइन मधून रोख काढून वापरले असे धरले आहे. तरीही <b>{rs(miss)}</b> चा खर्च यादीत लिहायचा राहिला आहे; त्याची नोंद करा.</li>
<li>रणजीत यांना {rs(r_in)} मिळाले आणि त्यांनी {rs(r_exp)} खर्च केले. म्हणजे त्यांनी <b>{rs(r_own)}</b> स्वतःच्या खिशातून घातले. पण देणे दारी यादीत त्यांना फक्त {rs(dues_r)} परत द्यायचे लिहिले आहे. <b>{rs(r_own - dues_r)} चा फरक</b> रणजीत यांच्याशी बोलून तपासा.</li>
<li>देणे दारी {rs(dues_total)} पूर्ण दिल्यावर मंडळाकडे <b>{sign(final)}</b> राहील.</li>
<li>सर्व येणे ({rs(V['pending'])}) वसूल झाले तरी शेवटी <b>{sign(final_after)}</b> राहील.</li>
</ul></div>""")
# दिवसवार सारांश
w('<h2>२. दिवसानुसार वर्गणी सारांश</h2>')
rows = []
for pg in pages:
    t = pg["t"]; wr = pg["written"]
    rows.append([pg["date"] + (f"<br><small>{pg['title']}</small>" if pg.get("title") else ""), len(pg["rows"]), r(t["total"]), r(t["cash"]), r(t["gpay"]),
                 r(t["later_cash"] + t["later_gpay"]), r(t["pending"]), r(wr["total"])])
w(table(["दिनांक", "नावे", "ठरलेली वर्गणी", "रोख मिळाले", "ऑनलाइन मिळाले", "नंतर जमा", "अजून येणे", "वहीतील एकूण"], rows,
        cls="num", foot=["एकूण", sum(len(p["rows"]) for p in pages), r(V["total"]), r(V["cash"]), r(V["gpay"]),
                          r(V["later_cash"] + V["later_gpay"]), r(V["pending"]), r(V_written["total"])]))
w('<p class="small">“ठरलेली वर्गणी” = नावांसमोर लिहिलेल्या रकमांची बेरीज. “वहीतील एकूण” = प्रत्येक पानाच्या खाली हाताने लिहिलेली बेरीज. दोन्हीतील फरक भाग ८ मध्ये स्पष्ट केला आहे.</p>')


# जमा तपशील
w('<h2>३. मोठ्या देणग्या, सभासद वर्गणी व इतर जमा</h2>')
w('<h3>३.१ मोठ्या देणग्या (वहीतील वेगळे पान) - कार्तिक</h3>')
w(table(["#", "नाव", "रक्कम", "प्रकार", "कार्तिक तपासणी"], [[i + 1, escape(n), r(a), badge(m), BOX] for i, (n, a, m) in enumerate(BIG_DONORS)],
        cls="num", foot=["", "एकूण", r(big_cash + big_gpay), f"रोख {r(big_cash)} · ऑनलाइन {r(big_gpay)}", ""]))
w('<h3>३.२ सभासद वर्गणी व इतर वर्गणी - कार्तिक (सर्व मिळाले)</h3>')
w(table(["#", "नाव", "तपशील", "प्रकार", "रक्कम", "कार्तिक तपासणी"], [[i + 1, escape(n), g, badge(m), r(a), BOX] for i, (n, a, m, g) in enumerate(OTHER_INCOME)],
        cls="num exp", foot=["", "एकूण", "", f"रोख {r(oth_cash)} · ऑनलाइन {r(oth_gpay)}", r(oth_cash + oth_gpay), ""]))
w('<h3>३.३ रणजीत यांच्याकडे आलेली जमा</h3>')
w(table(["#", "नाव", "तपशील", "प्रकार", "रक्कम"], [[i + 1, escape(n), g, badge(m), r(a)] for i, (n, a, m, g) in enumerate(RANJEET_INCOME)],
        cls="num exp", foot=["", "एकूण", "", "", r(r_in)]))

# खर्च
w('<h2 class="pb">४. खर्च तपशील (गटानुसार)</h2>')
grows = []
for g, items in groups.items():
    kk = sum(e[1] for e in items if e[5] == K); rr_ = sum(e[1] for e in items if e[5] == R)
    grows.append([g, r(kk), r(rr_), r(kk + rr_), f"{(kk + rr_) * 100 / exp_total:.1f}%"])
w(table(["खर्चाचा गट", "कार्तिक", "रणजीत", "एकूण", "टक्के"], grows, cls="num",
        foot=["एकूण दिलेला खर्च", r(k_exp), r(r_exp), r(exp_total), "100%"]))
n = 0
for g, items in groups.items():
    w(f'<h3>{g}</h3>')
    rows_ = []
    for d, a, m, _, dt, who in items:
        n += 1
        rows_.append([n, escape(d), dt or "—", who, badge(m), r(a)])
    w(table(["#", "तपशील", "दिनांक", "कोणी दिले", "प्रकार", "रक्कम"], rows_, cls="num exp",
            foot=["", "गट एकूण", "", "", "", r(sum(e[1] for e in items))], widths=["6%", "42%", "11%", "13%", "13%", "15%"]))
w('<p class="small">एकूण खर्च (दिलेला + देणे दारी): सजावट 80,000 (रणजीत 40,000 + कार्तिक 10,000 आगाऊ + 15,000 + बाकी 15,000). मंडप समीर कोळेकर 75,000 (40,000 दिले + 35,000 बाकी). हलगी 17,000 (7,000 + 10,000). ट्रॉली ट्रॅक्टर 16,000 (6,000 दिले + 10,000 बाकी).</p>')

# देणे दारी
w('<h2>५. देणे दारी (अजून द्यायचे पैसे)</h2>')
w(table(["#", "कोणाला / कशासाठी", "रक्कम"], [[i + 1, escape(n_), r(a)] for i, (n_, a) in enumerate(DUES)],
        cls="num", foot=["", "एकूण देणे", r(dues_total)]))
# येणे यादी
w('<h2 class="pb">६. अजून येणे बाकी असलेली वर्गणी (वसुली यादी)</h2>')
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
w('<h2 class="pb">७. दिवसानुसार संपूर्ण वर्गणी यादी</h2>')
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
        rr.append([i + 1, nm, r(e["amount"]), st, escape(e["note"]), BOX if e["mode"] != "yene" or e["later"] else ""])
    w(table(["#", "नाव", "रक्कम", "स्थिती", "टीप", "तपासणी"], rr, cls="num list",
            foot=["", "एकूण", r(t["total"]), f'रोख {r(t["cash"] + t["later_cash"])} · ऑनलाइन {r(t["gpay"] + t["later_gpay"])} · बाकी {r(t["pending"])}', "", ""],
            widths=["5%", "28%", "10%", "29%", "20%", "8%"]))

# फरक व गृहीतके
w('<h2 class="pb">८. वहीशी न जुळणाऱ्या बेरजा व घेतलेले निर्णय</h2>')
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
<li><b>नंतर जमा झालेले येणे (वहीत नोंद नसलेले):</b> तुंगे काकू 700 (16/10), प्रसाद दादा 301 (16/10), आशिष बारे 251 (11/10) ऑनलाइन; योगेश दादा 1,001 व मोरे काकू 1,001 रोख.</li>

</ul></div>""")


w(f"""<h2>९. अंतिम ताळेबंद</h2>
<table class="final"><tbody>
<tr><td>कार्तिक - एकूण जमा</td><td>{rs(k_in)}</td></tr>
<tr><td>कार्तिक - एकूण खर्च</td><td>{rs(k_exp)}</td></tr>
<tr><td>हिशोबाप्रमाणे शिल्लक</td><td>{rs(k_bal)}</td></tr>
<tr><td>न लिहिलेला खर्च (यादी यायची आहे)</td><td>{rs(miss)}</td></tr>
<tr class="hl"><td>कार्तिक यांच्याकडे प्रत्यक्ष शिल्लक</td><td>{rs(k_act)}</td></tr>
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

print(json.dumps(dict(k_in_cash=k_in_cash, k_in_gpay=k_in_gpay, k_exp_cash=k_exp_cash, k_exp_gpay=k_exp_gpay, k_bal=k_bal, miss_cash=miss_cash, miss_gpay=miss_gpay,
                      r_in=r_in, r_exp=r_exp, r_own=r_own, dues=dues_total, final=final, pending=V["pending"],
                      final_after=final_after, inc_total=inc_total, exp_total=exp_total, cost_total=cost_total), ensure_ascii=False, indent=1))
