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

def sg(n):
    return ("+" if n > 0 else "") + r(n)

kexp = [e for e in b.EXPENSES if e[6] in ("B", "A")]
cash_out = sum(e[1] for e in kexp if e[2] == "cash")
gpay_out = sum(e[1] for e in kexp if e[2] == "gpay")
cash_items = [(n.split(" (")[0] if n.startswith("शुभम") or n.startswith("कार्तिक") else n, a) for n, a, m in b.BASE_INCOME if m == "cash"]
cash_items = [(n, a) for n, a, m in b.BASE_INCOME if m == "cash"]
cash_items = [("मोठ्या देणग्या (रोख)", cash_items[0][1]), (f"कार्तिक ({b.BASE_DATE} पर्यंत)", cash_items[1][1]), ("सभासद (रोहन + कार्तिक)", cash_items[2][1])]
cash_items += [(n.replace(" (येणे)", ""), a) for n, a, m, d, g in AFTER_INCOME if m == "cash"]
cash_in = sum(a for _, a in cash_items)
exp_items = [(e[0] + (f" {e[4]}" if e[4] else "") + (" (ऑनलाइन)" if e[2] == "gpay" else ""), e[1]) for e in kexp]

html = f"""<!doctype html><html lang="mr"><head><meta charset="utf-8"><title>नवरात्र उत्सव २०२६ - हिशोब</title><style>
@page {{ size: A4; margin: 10mm 11mm; }}
body {{ font-family: "Mukta", sans-serif; font-size: 8.6pt; color: #1f2328; margin: 0; line-height: 1.15; }}
h1 {{ text-align: center; color: #8a1c22; margin: 0; font-size: 15pt; }}
.sub {{ text-align: center; font-size: 9pt; color: #57606a; margin-bottom: 6px; }}
h3 {{ color: #8a1c22; font-size: 11pt; margin: 6px 0 2px; border-bottom: 1px solid #e3c2c4; }}
table {{ width: 100%; border-collapse: collapse; }}
td, th {{ padding: 1px 5px; border-bottom: 1px solid #eee; }}
th {{ background: #8a1c22; color: #fff; font-weight: 600; text-align: left; }}
td:not(:first-child), th:not(:first-child) {{ text-align: right; }}
tr.b td {{ font-weight: 700; background: #f3e6e7; }}
.two {{ display: flex; gap: 12px; }} .two .t {{ flex: 1; font-size: 8.6pt; }}
.tot {{ text-align: right; font-size: 9.5pt; margin-top: 2px; }}
.grid {{ display: flex; gap: 12px; }} .grid > div {{ flex: 1; }}
.final td {{ font-size: 10.5pt; }}
.small {{ font-size: 8.5pt; color: #57606a; }}
</style></head><body>
<h1>॥ श्री ॥ नवरात्र उत्सव २०२६ - हिशोब</h1>
<div class="sub">दि. 20/10/2026</div>

<h3>१. कार्तिक यांच्याकडील हिशोब (संपूर्ण उत्सव)</h3>
<table><thead><tr><th>तपशील</th><th>रोख</th><th>ऑनलाइन (GPay)</th><th>एकूण</th></tr></thead><tbody>
<tr><td>एकूण जमा</td><td>{r(cash_in)}</td><td>{r(b.ONLINE_TOTAL)}</td><td>{r(cash_in + b.ONLINE_TOTAL)}</td></tr>
<tr><td>ऑनलाइन मधून रोखीत वळवले</td><td>+{r(b.BASE_TRANSFER)}</td><td>−{r(b.BASE_TRANSFER)}</td><td>0</td></tr>
<tr><td>− एकूण खर्च</td><td>{r(cash_out)}</td><td>{r(gpay_out)}</td><td>{r(cash_out + gpay_out)}</td></tr>
<tr class="b"><td>हिशोबाप्रमाणे शिल्लक असायला हवी</td><td>{r(b.c_cash)}</td><td>{r(b.c_gpay)}</td><td>{r(b.k_bal)}</td></tr>
<tr class="b"><td>प्रत्यक्ष शिल्लक</td><td>{r(b.k_act_cash)}</td><td>{r(b.k_act_gpay)}</td><td>{r(b.k_act)}</td></tr>
<tr class="b"><td>फरक (प्रत्यक्ष − हिशोब)</td><td>{sg(b.k_act_cash - b.c_cash)}</td><td>{sg(b.k_act_gpay - b.c_gpay)}</td><td>{sg(b.extra)}</td></tr>
</tbody></table>
<div class="small">ऑनलाइन जमा = कार्तिक यांच्या GPay यादीतील बेरीज 51,962 − 5,000 = {r(b.ONLINE_TOTAL)}. फरक उणे (−) म्हणजे हिशोबापेक्षा पैसे कमी आहेत: तेवढा खर्च लिहायचा राहिला आहे किंवा रक्कम कोणाकडे तरी आहे.</div>

{two_col("२. रोख जमा", cash_items, "एकूण रोख जमा", cash_in)}
<div class="tot">ऑनलाइन जमा (GPay यादी): <b>{rs(b.ONLINE_TOTAL)}</b></div>
{two_col("३. खर्च ", exp_items, f"रोख {r(cash_out)} + ऑनलाइन {r(gpay_out)} = एकूण", cash_out + gpay_out)}

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
