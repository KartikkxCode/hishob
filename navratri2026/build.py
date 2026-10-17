"""नवरात्र उत्सव २०२६ - जमा-खर्च हिशोब PDF साठी HTML तयार करते."""
from collections import OrderedDict
from html import escape
import json

from data import VARGANI, BIG_DONORS, OTHER_INCOME, EXPENSES

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

big_cash = sum(a for _, a, m in BIG_DONORS if m == "cash")
big_gpay = sum(a for _, a, m in BIG_DONORS if m == "gpay")
oth_gpay = sum(a for _, a, m, _ in OTHER_INCOME if m == "gpay")
oth_cash = sum(a for _, a, m, _ in OTHER_INCOME if m == "cash")
oth_other_acct = sum(a for _, a, m, g in OTHER_INCOME if "दुसऱ्या खात्यात" in g)

inc_cash = V["cash"] + V["later_cash"] + big_cash + oth_cash
inc_gpay = V["gpay"] + V["later_gpay"] + big_gpay + oth_gpay
inc_total = inc_cash + inc_gpay

exp_cash = sum(a for _, a, m, _, _ in EXPENSES if m == "cash")
exp_gpay = sum(a for _, a, m, _, _ in EXPENSES if m == "gpay")
exp_total = exp_cash + exp_gpay

bal_cash = inc_cash - exp_cash
bal_gpay = inc_gpay - exp_gpay
bal_total = inc_total - exp_total

groups = OrderedDict()
for d, a, m, g, dt in EXPENSES:
    groups.setdefault(g, []).append((d, a, m, dt))

gpay_kartik = inc_gpay - oth_other_acct

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

# मुखपृष्ठ + सारांश
w(f"""
<header class="top">
  <div class="shri">॥ श्री ॥</div>
  <h1>नवरात्र उत्सव २०२६</h1>
  <div class="sub">जमा-खर्च हिशोब · वर्गणी दि. 03/10/2026 ते 16/10/2026</div>
  <div class="meta">अहवाल तयार केल्याचा दिनांक: 17/10/2026 · स्रोत: वर्गणी वही (11 पाने) व खर्च यादी</div>
</header>

<section class="cards">
  <div class="card"><div class="k">एकूण जमा (मिळालेले)</div><div class="v pos">{rs(inc_total)}</div><div class="s">रोख {rs(inc_cash)} · ऑनलाइन {rs(inc_gpay)}</div></div>
  <div class="card"><div class="k">एकूण खर्च</div><div class="v neg">{rs(exp_total)}</div><div class="s">रोख {rs(exp_cash)} · ऑनलाइन {rs(exp_gpay)}</div></div>
  <div class="card"><div class="k">{'शिल्लक' if bal_total >= 0 else 'तूट (कमी पडलेले)'}</div><div class="v {'pos' if bal_total >= 0 else 'neg'}">{rs(abs(bal_total))}</div><div class="s">जमा − खर्च</div></div>
  <div class="card"><div class="k">अजून येणे बाकी (वर्गणी)</div><div class="v warn">{rs(V['pending'])}</div><div class="s">+ {V['blank']} नावे रक्कम न लिहिलेली</div></div>
</section>
""")

w('<h2>१. एकूण सारांश</h2>')
w(table(["तपशील", "रोख", "ऑनलाइन", "एकूण"], [
    ["दैनंदिन वर्गणी - त्याच दिवशी मिळालेली", r(V['cash']), r(V['gpay']), r(V['cash'] + V['gpay'])],
    ["दैनंदिन वर्गणी - येणे पैकी नंतर जमा", r(V['later_cash']), r(V['later_gpay']), r(V['later_cash'] + V['later_gpay'])],
    ["मोठ्या देणग्या (वेगळे पान)", r(big_cash), r(big_gpay), r(big_cash + big_gpay)],
    ["सभासद वर्गणी व इतर देणग्या", r(oth_cash), r(oth_gpay), r(oth_cash + oth_gpay)],
    ["<b>एकूण जमा</b>", f"<b>{r(inc_cash)}</b>", f"<b>{r(inc_gpay)}</b>", f"<b>{r(inc_total)}</b>"],
    ["<b>एकूण खर्च</b>", f"<b>{r(exp_cash)}</b>", f"<b>{r(exp_gpay)}</b>", f"<b>{r(exp_total)}</b>"],
], cls="sum", foot=["शिल्लक (+) / तूट (−)", r(bal_cash), r(bal_gpay), r(bal_total)]))

w(f"""<div class="note">
<b>या आकड्यांचा अर्थ:</b>
<ul>
<li>रोख खर्च ({rs(exp_cash)}) हा रोख जमेपेक्षा ({rs(inc_cash)}) <b>{rs(exp_cash - inc_cash)}</b> ने जास्त आहे. हे पैसे ऑनलाइन जमेतून काढून किंवा कोणीतरी स्वतःच्या खिशातून दिले असावेत. ते कोणी दिले, हे नोंदवून ठेवा.</li>
<li>सर्व येणे ({rs(V['pending'])}) वसूल झाले तरी एकूण हिशोब {rs(bal_total + V['pending'])} {'शिल्लक' if bal_total + V['pending'] >= 0 else 'तुटीत'} राहील.</li>
<li>एकूण ऑनलाइन जमा {rs(inc_gpay)} पैकी <b>{rs(gpay_kartik)}</b> कार्तिक यांच्या GPay वर आले. उरलेले <b>{rs(oth_other_acct)}</b> (अजित करंजकर 22,000 + स्वीकार देशपांडे 10,000) दुसऱ्या खात्यात जमा आहेत.</li>
<li>कार्तिक यांच्या GPay वरून सर्व ऑनलाइन खर्च ({rs(exp_gpay)}) झाला आहे. म्हणून वर्गणीपैकी <b>{rs(gpay_kartik - exp_gpay)}</b> त्यांच्याकडे ऑनलाइन शिल्लक असायला हवेत.</li>
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
w('<p class="small">“ठरलेली वर्गणी” = नावांसमोर लिहिलेल्या रकमांची बेरीज. “वहीतील एकूण” = प्रत्येक पानाच्या खाली हाताने लिहिलेली बेरीज. दोन्हीतील फरक भाग ७ मध्ये स्पष्ट केला आहे.</p>')

# मोठ्या देणग्या + इतर
w('<h2>३. मोठ्या देणग्या, सभासद वर्गणी व इतर जमा</h2>')
w('<h3>३.१ मोठ्या देणग्या (वहीतील वेगळे पान)</h3>')
w(table(["#", "नाव", "रक्कम", "प्रकार"], [[i + 1, escape(n), r(a), badge(m)] for i, (n, a, m) in enumerate(BIG_DONORS)],
        cls="num", foot=["", "एकूण", r(big_cash + big_gpay), f"रोख {r(big_cash)} · ऑनलाइन {r(big_gpay)}"]))
w('<h3>३.२ सभासद वर्गणी व इतर देणग्या (सर्व मिळाले)</h3>')
w(table(["#", "नाव", "तपशील", "प्रकार", "रक्कम"], [[i + 1, escape(n), g, badge(m), r(a)] for i, (n, a, m, g) in enumerate(OTHER_INCOME)],
        cls="num exp", foot=["", "एकूण", "", f"रोख {r(oth_cash)} · ऑनलाइन {r(oth_gpay)}", r(oth_cash + oth_gpay)]))

# खर्च
w('<h2>४. खर्च तपशील (गटानुसार)</h2>')
grows = []
for g, items in groups.items():
    c = sum(a for _, a, m, _ in items if m == "cash"); o = sum(a for _, a, m, _ in items if m == "gpay")
    grows.append([g, r(c), r(o), r(c + o), f"{(c + o) * 100 / exp_total:.1f}%"])
w(table(["खर्चाचा गट", "रोख", "ऑनलाइन", "एकूण", "टक्के"], grows, cls="num",
        foot=["एकूण खर्च", r(exp_cash), r(exp_gpay), r(exp_total), "100%"]))
n = 0
for g, items in groups.items():
    w(f'<h3>{g}</h3>')
    rr = []
    for d, a, m, dt in items:
        n += 1
        rr.append([n, escape(d), dt or "—", badge(m), r(a)])
    w(table(["#", "तपशील", "दिनांक", "प्रकार", "रक्कम"], rr, cls="num exp",
            foot=["", "गट एकूण", "", "", r(sum(a for _, a, _, _ in items))], widths=["6%", "52%", "12%", "14%", "16%"]))
w('<p class="small">टीप: तुमच्या सांगण्याप्रमाणे सजावट एकूण 45,000 (आगाऊ 30,000 + 16/10 रोजी 10,000 रोख + 5,000 ऑनलाइन) धरली आहे. हलगीचे 10,000 आणि आगाऊ 7,000 वेगवेगळे धरले आहेत. समीर कोळेकर यांचे 40,000 मंडपाचे आहेत.</p>')

# येणे यादी
w('<h2 class="pb">५. अजून येणे बाकी असलेली वर्गणी (वसुली यादी)</h2>')
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
w('<h2 class="pb">६. दिवसानुसार संपूर्ण वर्गणी यादी</h2>')
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
w('<h2 class="pb">७. वहीशी न जुळणाऱ्या बेरजा व घेतलेले निर्णय</h2>')
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

w(f"""<h2>८. अंतिम ताळेबंद</h2>
<table class="final"><tbody>
<tr><td>एकूण जमा</td><td>{rs(inc_total)}</td></tr>
<tr><td>एकूण खर्च</td><td>{rs(exp_total)}</td></tr>
<tr class="hl"><td>{'शिल्लक' if bal_total >= 0 else 'तूट'}</td><td>{rs(abs(bal_total))}</td></tr>
<tr><td>अजून वसूल करायची वर्गणी</td><td>{rs(V['pending'])}</td></tr>
<tr class="hl"><td>सर्व येणे वसूल झाल्यावर</td><td>{rs(bal_total + V['pending'])} {'शिल्लक' if bal_total + V['pending'] >= 0 else 'तूट'}</td></tr>
</tbody></table>
<div class="sign"><div>हिशोब तपासणारे<br><br>__________________</div><div>खजिनदार<br><br>__________________</div><div>अध्यक्ष<br><br>__________________</div></div>
""")

CSS = open("style.css", encoding="utf-8").read()
html = f"""<!doctype html><html lang="mr"><head><meta charset="utf-8"><title>नवरात्र उत्सव २०२६ - हिशोब</title><style>{CSS}</style></head><body>{''.join(H)}</body></html>"""
open("hishob.html", "w", encoding="utf-8").write(html)

print(json.dumps(dict(inc_cash=inc_cash, inc_gpay=inc_gpay, inc_total=inc_total, exp_cash=exp_cash, exp_gpay=exp_gpay,
                      exp_total=exp_total, bal=bal_total, pending=V["pending"], V=V, V_written=V_written,
                      pages=[(p["date"], p["t"]) for p in pages], gpay_kartik=gpay_kartik), ensure_ascii=False, indent=1))
