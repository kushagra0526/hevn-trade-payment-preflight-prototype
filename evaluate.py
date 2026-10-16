"""Score the pre-flight check and two baselines against generator truth.

  exact_screen   party names exactly equal to a listed name, or a sanctioned country name in the text -> HOLD
  amount_only    payment amount != invoice total -> FIX (what a simple 'does it match the invoice' check does)
  preflight      tradeflight.check

python evaluate.py          # held-out
python evaluate.py --dev
"""
import collections
import json
import re
import sys

from tradeflight.check import check, parse_invoice, parse_payment
from tradeflight.synth import case

HOLDS = {"CONTROLLED_GOODS", "SANCTIONED_ROUTE", "LISTED_PARTY", "DUPLICATE_INVOICE", "PRICE_ANOMALY", "THIRD_PARTY_PAYER", "NAME_MISMATCH"}


def exact_screen(docs, B):
    text = "\n".join(docs.values())
    if any(lp in text for lp in B["listed_parties"]):
        return "HOLD"
    if re.search(r"\b(Iran|Syria|North Korea|Cuba|Crimea)\b", text):
        return "HOLD"
    return "READY"


def amount_only(docs, B):
    inv, pay = parse_invoice(docs["invoice"]), parse_payment(docs["payment"])
    return "FIX" if abs(inv["total"] - pay["amount"]) > 0.01 else "READY"


def run(B, seeds):
    hist = []
    rows = []
    for s in seeds:
        docs, truth, ledger = case(s, B, hist)
        v, F, pack = check(docs, ledger, B)
        rows.append({"seed": s, "truth": truth, "verdict": v, "kinds": sorted({f["kind"] for f in F}), "findings": F,
                     "exact_screen": exact_screen(docs, B), "amount_only": amount_only(docs, B), "pack": pack})
    S = {}
    for pol in ("exact_screen", "amount_only", "preflight"):
        c = collections.Counter()
        for r in rows:
            v = r["verdict"] if pol == "preflight" else r[pol]
            iss = set(r["truth"]["issues"])
            if not iss:
                c["clean"] += 1
                c["clean_stopped"] += v != "READY"
            else:
                c["problem"] += 1
                c["problem_stopped"] += v != "READY"
                if iss & HOLDS:
                    c["needs_hold"] += 1
                    c["needs_hold_held"] += v == "HOLD"
        S[pol] = dict(c)
    per = collections.Counter()
    for r in rows:
        for i in r["truth"]["issues"]:
            per[i + "_n"] += 1
            per[i + "_named"] += i in r["kinds"]
        for k in set(r["kinds"]) - set(r["truth"]["issues"]):
            per["false_" + k] += 1
    S["preflight_by_issue"] = {k[:-2]: f"{per[k[:-2] + '_named']}/{per[k]}" for k in sorted(per) if k.endswith("_n")}
    S["preflight_false_findings"] = {k[6:]: v for k, v in per.items() if k.startswith("false_")}
    S["benign_lookalikes_ready"] = sum(1 for r in rows if not r["truth"]["issues"] and r["truth"]["benign"] and r["verdict"] == "READY")
    S["benign_lookalikes"] = sum(1 for r in rows if not r["truth"]["issues"] and r["truth"]["benign"])
    return S, rows


if __name__ == "__main__":
    if "--dev" in sys.argv:
        from tradeflight.bank_dev import BANK
        seeds, name = range(1, 1201), "dev"
    else:
        from eval.bank_heldout import BANK, SEEDS
        seeds, name = SEEDS, "heldout"
    S, rows = run(BANK, seeds)
    json.dump({"summary": S, "misses_and_false": [r for r in rows if set(r["truth"]["issues"]) != set(r["kinds"]) and
                                                  (set(r["truth"]["issues"]) - set(r["kinds"]) or set(r["kinds"]) - set(r["truth"]["issues"]))][:200]},
              open(f"out/{name}.json", "w"), indent=1, default=str)
    print(json.dumps(S, indent=1))
