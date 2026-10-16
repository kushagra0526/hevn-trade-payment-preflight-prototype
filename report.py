"""out/report.html from held-out first run + after fixes."""
import json

F = json.load(open("out/heldout_first_run.json"))["summary"]
A = json.load(open("out/heldout.json"))["summary"]
N = {"exact_screen": "Exact-name + country-word screen", "amount_only": "Amount = invoice total", "preflight": "Pre-flight check"}
rows = ""
for p in N:
    a, f = A[p], F[p]
    rows += (f"<tr class={'g' if p == 'preflight' else ''}><td>{N[p]}</td><td>{a['problem_stopped']}/{a['problem']}</td><td>{a['needs_hold_held']}/{a['needs_hold']}</td>"
             f"<td>{a['clean_stopped']}/{a['clean']}</td><td>{f['clean_stopped']}/{f['clean']}</td></tr>")
iss = "".join(f"<tr><td>{k}</td><td>{v}</td><td>{F['preflight_by_issue'][k]}</td></tr>" for k, v in A["preflight_by_issue"].items())
open("out/report.html", "w", encoding="utf-8").write(f"""<!doctype html><meta charset=utf-8><title>trade payment pre-flight</title>
<style>body{{font:15px system-ui;margin:24px;max-width:1060px}}table{{border-collapse:collapse;margin:8px 0 14px}}td,th{{border:1px solid #ccc;padding:6px 10px;text-align:right}}td:first-child,th:first-child{{text-align:left}}.g td{{background:#eaf7ee;font-weight:600}}</style>
<h2>Trade payment pre-flight: held-out, 1,500 synthetic goods payments</h2>
<p>Invoice + B/L + payment instruction per payment; truth = planted issues. Lists illustrative, parties fictional. Unofficial prototype, not affiliated with HEVN.</p>
<table><tr><th>Check</th><th>Problem payments stopped</th><th>Needed a HOLD, got one</th><th>Clean payments stopped (after fixes)</th><th>Clean stopped, first run</th></tr>{rows}</table>
<div style="display:flex;gap:30px"><table><tr><th>Issue</th><th>Named (after fixes)</th><th>First run</th></tr>{iss}</table>
<p style="max-width:420px">First run stopped 596 clean payments: names written differently on held-out (Mueller / Müller, ß, ł, dotless ı, "Joint Stock Company" / JSC).
Fixed with a transliteration table + multi-word legal forms; the second fix added a document fingerprint to the payment ledger (50/50 terms make the amount ambiguous).
Legitimate look-alikes passed: {A['benign_lookalikes_ready']}/{A['benign_lookalikes']}.</p></div>""")
