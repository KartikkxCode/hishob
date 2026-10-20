"""नवरात्र मंडळ - संपूर्ण हिशोब (12/10 च्या हिशोबाच्या नमुन्याप्रमाणे)."""
import contextlib, io

with contextlib.redirect_stdout(io.StringIO()):
    import build as b
from data import AFTER_INCOME, DUES, RANJEET_INCOME, BASE_INCOME, BASE_TRANSFER, ONLINE_TOTAL

r = b.r
kexp = [e for e in b.EXPENSES if e[6] in ("B", "A")]
exp_gpay = [e for e in kexp if e[2] == "gpay"]
exp_cash = [e for e in kexp if e[2] == "cash"]
ranj_exp = [e for e in b.EXPENSES if e[6] == "R"]

jama = [
    ("कार्तिक (शुभम) - रोख, मोठ्या देणग्या (वहीनुसार)", 17700),
    ("कार्तिक - रोख (दैनंदिन वहीनुसार, 12/10 पर्यंत)", 23943),
    ("सभासद वर्गणी (रोहन 5,000 + कार्तिक 5,000) - रोख", 10000),
]
jama += [(n.replace(" (येणे)", "") + " - रोख", a) for n, a, m, d, g in AFTER_INCOME if m == "cash"]
cash_in = sum(a for _, a in jama)
jama.append(("कार्तिक - ऑनलाईन (GPay)", ONLINE_TOTAL))
jama_total = cash_in + ONLINE_TOTAL

def label(e):
    return e[0] + (f" ({e[4]})" if e[4] else "")

def tbl(rows, total_label, total):
    body = "".join(f"<tr><td class='n'>{i}</td><td>{t}</td><td class='a'>{r(a)}</td></tr>" for i, (t, a) in enumerate(rows, 1))
    return f"""<table><thead><tr><th class='n'></th><th>तपशील</th><th class='a'>रक्कम (₹)</th></tr></thead>
<tbody>{body}<tr class='t'><td></td><td>{total_label}</td><td class='a'>{r(total)}</td></tr></tbody></table>"""

c_out = sum(e[1] for e in exp_cash)
g_out = sum(e[1] for e in exp_gpay)
cash_bal = cash_in + BASE_TRANSFER - c_out
gpay_bal = ONLINE_TOTAL - BASE_TRANSFER - g_out
act_c, act_g = b.k_act_cash, b.k_act_gpay

def sg(n):
    return ("+" if n > 0 else "") + r(n)

html = f"""<!doctype html><html lang="mr"><head><meta charset="utf-8"><title>नवरात्र मंडळ - संपूर्ण हिशोब</title><style>
@page {{ size: A4; margin: 14mm 16mm; }}
body {{ font-family: "Mukta", sans-serif; font-size: 10.5pt; color: #000; margin: 0; }}
h1 {{ text-align: center; font-size: 17pt; margin: 0 0 2px; }}
.date {{ text-align: center; font-size: 11pt; margin-bottom: 14px; }}
h2 {{ font-size: 13pt; margin: 16px 0 4px; break-after: avoid; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 4px; }}
th {{ text-align: left; font-weight: 700; border-bottom: 1.5px solid #000; padding: 3px 6px; }}
td {{ padding: 2px 6px; border-bottom: 1px solid #ddd; }}
tr {{ break-inside: avoid; }}
.n {{ width: 6%; }} .a {{ text-align: right; width: 22%; }}
tr.t td {{ font-weight: 700; border-top: 1.5px solid #000; border-bottom: none; }}
.note {{ font-size: 10pt; margin: 6px 0; }}
table.tal td:not(:first-child), table.tal th:not(:first-child) {{ text-align: right; width: 18%; }}
table.tal tr.t td {{ font-weight: 700; }}
</style></head><body>
<h1>नवरात्र मंडळ - संपूर्ण हिशोब</h1>
<div class="date">दिनांक: 20 ऑक्टोबर 2026</div>

<h2>१) जमा</h2>
<div class="note">12/10 च्या हिशोबात रोख जमा 17,000 (शुभम नावाने) + 19,555 = 36,555 धरली होती. वहीनुसार ती 17,700 + 23,943 = 41,643 आहे, म्हणजे <b>₹5,088 जास्त</b>. इथे वहीची रक्कम धरली आहे.</div>
{tbl(jama, "एकूण जमा", jama_total)}

<h2>२) खर्च - ऑनलाईन</h2>
{tbl([(label(e), e[1]) for e in exp_gpay], "एकूण ऑनलाईन खर्च", g_out)}

<h2>३) खर्च - रोख</h2>
{tbl([(label(e), e[1]) for e in exp_cash], "एकूण रोख खर्च", c_out)}
<div class="note">फक्त नोंद (बेरजेत नाही): ट्रॉली ट्रॅक्टरसाठी रणजीत कडून ₹1,000 रोख.</div>

<h2>४) रोख / ऑनलाईन ताळमेळ</h2>
<table class="tal"><thead><tr><th>तपशील</th><th>रोख (₹)</th><th>ऑनलाईन (₹)</th><th>एकूण (₹)</th></tr></thead><tbody>
<tr><td>जमा</td><td>{r(cash_in)}</td><td>{r(ONLINE_TOTAL)}</td><td>{r(jama_total)}</td></tr>
<tr><td>ऑनलाईनमधून रोखीत वळवले</td><td>+{r(BASE_TRANSFER)}</td><td>−{r(BASE_TRANSFER)}</td><td>0</td></tr>
<tr><td>खर्च</td><td>−{r(c_out)}</td><td>−{r(g_out)}</td><td>−{r(c_out + g_out)}</td></tr>
<tr class="t"><td>हिशोबाप्रमाणे शिल्लक</td><td>{r(cash_bal)}</td><td>{r(gpay_bal)}</td><td>{r(cash_bal + gpay_bal)}</td></tr>
<tr class="t"><td>प्रत्यक्ष शिल्लक</td><td>{r(act_c)}</td><td>{r(act_g)}</td><td>{r(act_c + act_g)}</td></tr>
<tr><td>फरक</td><td>{sg(act_c - cash_bal)}</td><td>{sg(act_g - gpay_bal)}</td><td>{sg(act_c + act_g - cash_bal - gpay_bal)}</td></tr>
</tbody></table>
<div class="note">फरक उणे (−) म्हणजे हिशोबाप्रमाणे असायला हवे त्यापेक्षा प्रत्यक्ष पैसे कमी आहेत. रोख व ऑनलाईन यांच्यात पैसे फिरल्यामुळे फक्त एकूण फरक पाहावा: ₹{r(act_c + act_g - cash_bal - gpay_bal)}.</div>

<h2>५) रणजीत यांचा हिशोब</h2>
{tbl([(f"जमा - {n}", a) for n, a, _, _ in RANJEET_INCOME], "एकूण जमा", b.r_in)}
{tbl([(e[0], e[1]) for e in ranj_exp], "एकूण खर्च", b.r_exp)}
<div class="note">रणजीत यांनी स्वतःच्या खिशातून घातलेले: <b>₹{r(b.r_own)}</b> (देणे यादीत ₹50,000 लिहिले आहे; ₹{r(b.r_own - b.dues_r)} चा फरक तपासायचा).</div>

<h2>६) देणे दारी (अजून द्यायचे)</h2>
{tbl(DUES, "एकूण देणे", b.dues_total)}

<h2>७) अंतिम सारांश</h2>
<table><tbody>
<tr><td>एकूण जमा</td><td class="a">{r(jama_total)}</td></tr>
<tr><td>एकूण खर्च ({r(g_out)} + {r(c_out)})</td><td class="a">{r(c_out + g_out)}</td></tr>
<tr class="t"><td>प्रत्यक्ष शिल्लक (रोख {r(act_c)} + ऑनलाईन {r(act_g)})</td><td class="a">{r(act_c + act_g)}</td></tr>
<tr><td>देणे दारी</td><td class="a">{r(b.dues_total)}</td></tr>
<tr class="t"><td>देणे दिल्यानंतर तूट</td><td class="a">{r(-b.final)}</td></tr>
<tr><td>अजून येणे बाकी वर्गणी</td><td class="a">{r(b.V['pending'])}</td></tr>
<tr class="t"><td>सर्व येणे आल्यावर तूट</td><td class="a">{r(-b.final_after)}</td></tr>
</tbody></table>
</body></html>"""
open("sampurna.html", "w", encoding="utf-8").write(html)
