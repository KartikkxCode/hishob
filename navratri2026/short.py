"""नवरात्र उत्सव २०२६ - मोजका (एक पानी) हिशोब."""
import contextlib, io

with contextlib.redirect_stdout(io.StringIO()):
    import build as b
from data import AFTER_INCOME, DUES

r, rs = b.r, b.rs
after_exp = [e for e in b.EXPENSES if e[6] == "A"]
ranj_exp = [e for e in b.EXPENSES if e[6] == "R"]

def rows(items):
    return "".join(f"<tr><td>{n}</td><td>{r(a)}</td></tr>" for n, a in items)

def two_col(title, items, total_label, total):
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    body = "".join(f'<table class="t"><tbody>{rows(c)}</tbody></table>' for c in cols)
    return f'<h3>{title}</h3><div class="two">{body}</div><div class="tot">{total_label}: <b>{rs(total)}</b></div>'

# शेवटी सापडलेल्या जमा नोंदी - अतिरिक्त रकमेतून वजा
LATE_NAMES = ("मंगेश बुजवे", "अमित बार (येणे)")
LATE = [(n.replace(" (येणे)", ""), a, "रोख" if m == "cash" else "ऑनलाइन") for n, a, m, d, g in AFTER_INCOME if n in LATE_NAMES]
LATE_TOTAL = sum(a for _, a, _ in LATE)

inc_items = [(n.replace(" (येणे)", ""), a) for n, a, m, d, g in AFTER_INCOME]
exp_items = [(e[0] + (f" {e[4]}" if e[4] else ""), e[1]) for e in after_exp]

html = f"""<!doctype html><html lang="mr"><head><meta charset="utf-8"><title>नवरात्र उत्सव २०२६ - हिशोब</title><style>
@page {{ size: A4; margin: 10mm 11mm; }}
body {{ font-family: "Mukta", sans-serif; font-size: 9pt; color: #1f2328; margin: 0; line-height: 1.2; }}
h1 {{ text-align: center; color: #8a1c22; margin: 0; font-size: 18pt; }}
.sub {{ text-align: center; font-size: 9pt; color: #57606a; margin-bottom: 6px; }}
h3 {{ color: #8a1c22; font-size: 11pt; margin: 6px 0 2px; border-bottom: 1px solid #e3c2c4; }}
table {{ width: 100%; border-collapse: collapse; }}
td, th {{ padding: 1px 5px; border-bottom: 1px solid #eee; }}
th {{ background: #8a1c22; color: #fff; font-weight: 600; text-align: left; }}
td:not(:first-child), th:not(:first-child) {{ text-align: right; }}
tr.b td {{ font-weight: 700; background: #f3e6e7; }}
.two {{ display: flex; gap: 12px; }} .two .t {{ flex: 1; font-size: 9pt; }}
.tot {{ text-align: right; font-size: 9.5pt; margin-top: 2px; }}
.grid {{ display: flex; gap: 12px; }} .grid > div {{ flex: 1; }}
.final td {{ font-size: 10.5pt; }}
.small {{ font-size: 8.5pt; color: #57606a; }}
</style></head><body>
<h1>॥ श्री ॥ नवरात्र उत्सव २०२६ - हिशोब</h1>
<div class="sub">दि. 19/10/2026 · पाया: {b.BASE_DATE} चा जुळलेला हिशोब</div>

<h3>१. कार्तिक यांच्याकडील हिशोब</h3>
<table><thead><tr><th>तपशील</th><th>रोख</th><th>ऑनलाइन</th><th>एकूण</th></tr></thead><tbody>
<tr><td>{b.BASE_DATE} ला शिल्लक</td><td>{r(b.b_bal_cash)}</td><td>{r(b.b_bal_gpay)}</td><td>{r(b.b_bal)}</td></tr>
<tr><td>+ नंतर आलेली जमा</td><td>{r(b.a_in_cash)}</td><td>{r(b.a_in_gpay)}</td><td>{r(b.a_in_cash + b.a_in_gpay)}</td></tr>
<tr><td>− नंतरचा खर्च</td><td>{r(b.a_exp_cash)}</td><td>{r(b.a_exp_gpay)}</td><td>{r(b.a_exp_cash + b.a_exp_gpay)}</td></tr>
<tr><td>ऑनलाइन मधून रोख काढले</td><td>+{r(b.withdraw)}</td><td>−{r(b.withdraw)}</td><td>0</td></tr>
<tr class="b"><td>हिशोबाप्रमाणे शिल्लक</td><td>{r(b.c_cash)}</td><td>{r(b.c_gpay)}</td><td>{r(b.k_bal)}</td></tr>
<tr class="b"><td>प्रत्यक्ष शिल्लक</td><td>{r(b.k_act_cash)}</td><td>{r(b.k_act_gpay)}</td><td>{r(b.k_act)}</td></tr>
<tr><td>नंतर सापडलेली जमा आधी धरून आलेला फरक</td><td></td><td></td><td>+{r(b.extra + LATE_TOTAL)}</td></tr>
{"".join(f'<tr><td>&nbsp;&nbsp;− {n} ({m})</td><td></td><td></td><td>−{r(a)}</td></tr>' for n, a, m in LATE)}
<tr class="b"><td>उरलेला फरक (नोंद न झालेली जमा)</td><td></td><td></td><td>+{r(b.extra)}</td></tr>
</tbody></table>

{two_col(f"२. {b.BASE_DATE} नंतर आलेली जमा", inc_items, f"रोख {r(b.a_in_cash)} + ऑनलाइन {r(b.a_in_gpay)} = एकूण", b.a_in_cash + b.a_in_gpay)}
{two_col(f"३. {b.BASE_DATE} नंतरचा खर्च", exp_items, f"रोख {r(b.a_exp_cash)} + ऑनलाइन {r(b.a_exp_gpay)} = एकूण", b.a_exp_cash + b.a_exp_gpay)}

<div class="grid"><div>
<h3>४. रणजीत</h3>
<table><tbody>{rows([("जमा (अजित 22,000 + स्वीकार 10,000)", b.r_in)] + [(e[0], e[1]) for e in ranj_exp])}
<tr class="b"><td>स्वतःच्या खिशातून</td><td>{r(b.r_own)}</td></tr></tbody></table>
<div class="small">देणे यादीत 50,000 लिहिले आहे; {r(b.r_own - b.dues_r)} चा फरक तपासा.</div>
</div><div>
<h3>५. देणे दारी</h3>
<table><tbody>{rows(DUES)}<tr class="b"><td>एकूण</td><td>{r(b.dues_total)}</td></tr></tbody></table>
</div></div>

<h3>६. अंतिम</h3>
<table class="final"><tbody>
<tr><td>कार्तिक यांच्याकडे प्रत्यक्ष शिल्लक</td><td>{rs(b.k_act)}</td></tr>
<tr><td>− देणे दारी</td><td>{rs(b.dues_total)}</td></tr>
<tr class="b"><td>देणे दिल्यावर</td><td>{b.sign(b.final)}</td></tr>
<tr><td>+ अजून येणे बाकी वर्गणी</td><td>{rs(b.V['pending'])}</td></tr>
<tr class="b"><td>सर्व येणे आल्यावर</td><td>{b.sign(b.final_after)}</td></tr>
</tbody></table>
</body></html>"""
open("short.html", "w", encoding="utf-8").write(html)
