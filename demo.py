"""Four held-out payments: documents in, verdict + reasons (or the evidence pack) out."""
import sys

from eval.bank_heldout import BANK, SEEDS
from tradeflight.check import check
from tradeflight.synth import case

PICKS = [("a clean balance payment with name variants (JSC, G.m.b.H.)", lambda t, v: not t["issues"] and "name alias" in t["benign"] and v == "READY"),
         ("a services purpose on a goods shipment", lambda t, v: t["issues"] == ["PURPOSE_MISMATCH"]),
         ("same invoice + B/L submitted again", lambda t, v: t["issues"] == ["DUPLICATE_INVOICE"]),
         ("goods discharged at a sanctioned port", lambda t, v: t["issues"] == ["SANCTIONED_ROUTE"])]


def main():
    hist = []
    found = {}
    for s in SEEDS:
        docs, truth, ledger = case(s, BANK, hist)
        v, F, pack = check(docs, ledger, BANK)
        for title, pred in PICKS:
            if title not in found and pred(truth, v):
                found[title] = (s, docs, truth, v, F, pack)
        if len(found) == len(PICKS):
            break
    for title, _ in PICKS:
        s, docs, truth, v, F, pack = found[title]
        print(f"\n=== {title}  (payment {s}; planted: {truth['issues'] or 'nothing'})")
        print("  " + docs["payment"].replace("\n", "\n  "))
        print(f"  -> {v}")
        for f in F:
            print(f"     [{f['level']}] {f['kind']}: {f['why']}")
        if pack:
            print("     evidence pack for the bank:\n       " + pack.replace("\n", "\n       "))


if __name__ == "__main__":
    main()
