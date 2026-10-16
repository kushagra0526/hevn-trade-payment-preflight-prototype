"""Synthetic goods trades: commercial invoice, bill of lading, packing list and a payment instruction as text in two
layouts each, with planted issues the generator labels (truth). Benign look-alikes (name aliases, HS formatting, port
aliases, correct partial payments) are planted too and must pass.

Lists here are ILLUSTRATIVE (fictional listed parties; a small controlled-goods and sanctioned-area set), not legal lists.
"""
import datetime as dt
import random

from .check import docs_sig

# order matters: later plants must not undo earlier ones (goods swaps before price/math/amount edits)
ISSUES = ["NAME_MISMATCH", "THIRD_PARTY_PAYER", "CONTROLLED_GOODS", "SANCTIONED_ROUTE", "DOC_MISMATCH", "MILESTONE", "PRICE_ANOMALY",
          "LISTED_PARTY", "PURPOSE_MISMATCH", "LINE_MATH", "AMOUNT_MISMATCH", "CURRENCY_MISMATCH"]


def pick(rng, xs):
    return xs[rng.randrange(len(xs))]


def alias(rng, name, B):
    """A benign spelling of the same legal entity."""
    out = name
    for a, b in B["form_variants"]:
        if a in out and rng.random() < 0.6:
            out = out.replace(a, b)
    for a, b in B["translit"]:
        if a in out and rng.random() < 0.6:
            out = out.replace(a, b)
    if rng.random() < 0.4:
        out = out.upper()
    return out


def terms_amount(terms, total, stage):
    from .check import schedule
    sch = schedule(terms, total)
    return sch.get(stage, next(iter(sch.values())))


def stages(terms):
    from .check import schedule
    return list(schedule(terms, 100.0))


def trade(seed, B, history):
    rng = random.Random(seed)
    seller, buyer = rng.sample(B["companies"], 2)
    g = pick(rng, [x for x in B["goods"] if not x.get("controlled")])
    n_lines = rng.randint(1, 2)
    lines = []
    for i in range(n_lines):
        gg = g if i == 0 else pick(rng, [x for x in B["goods"] if x["hs"] != g["hs"] and not x.get("controlled")])
        qty = rng.randint(*gg["qty"])
        price = round(rng.uniform(*gg["price"]), 2)
        lines.append({"desc": gg["desc"], "hs": gg["hs"], "qty": qty, "unit": gg["unit"], "price": price, "amount": round(qty * price, 2)})
    total = round(sum(l["amount"] for l in lines), 2)
    cur = pick(rng, ["USD", "USD", "EUR", "AED"])
    terms = pick(rng, B["terms"])
    route = pick(rng, B["routes"])
    inv_no = f"INV-{rng.randint(10, 99)}{seed:06d}"
    inv_date = dt.date(2026, rng.randint(1, 9), rng.randint(1, 28))
    bl_date = inv_date + dt.timedelta(days=rng.randint(3, 20))
    st = stages(terms)
    stage = pick(rng, st)
    pay_date = bl_date + dt.timedelta(days=rng.randint(1, 10)) if stage == "balance" else inv_date + dt.timedelta(days=rng.randint(1, 5))
    T = {"seller": seller, "buyer": buyer, "lines": lines, "total": total, "currency": cur, "terms": terms, "route": route, "inv_no": inv_no,
         "inv_date": inv_date, "bl_date": bl_date, "has_bl": stage == "balance" or rng.random() < 0.5, "stage": stage, "pay_date": pay_date,
         "beneficiary": alias(rng, seller["name"], B), "ordering": alias(rng, buyer["name"], B), "pay_currency": cur,
         "amount": terms_amount(terms, total, stage), "purpose": f"Payment for {inv_no} {lines[0]['desc']}", "bl_lines": [dict(l) for l in lines],
         "shipper": alias(rng, seller["name"], B), "consignee": alias(rng, buyer["name"], B), "issues": set(), "benign": []}
    if T["amount"] != total:
        T["benign"].append("partial payment per terms")
    if T["beneficiary"] != seller["name"]:
        T["benign"].append("name alias")
    # ---- plant issues ----
    for iss in ISSUES:
        if rng.random() >= B["p_issue"].get(iss, 0):
            continue
        if iss == "NAME_MISMATCH":
            T["beneficiary"] = pick(rng, B["other_beneficiaries"]).format(first=seller["name"].split()[0])
        elif iss == "THIRD_PARTY_PAYER":
            T["ordering"] = pick(rng, [c for c in B["companies"] if c["name"] not in (seller["name"], buyer["name"])])["name"]
        elif iss == "AMOUNT_MISMATCH":
            T["amount"] = round(T["amount"] * pick(rng, [1.1, 0.9, 1.25]), 2)
        elif iss == "CURRENCY_MISMATCH":
            T["pay_currency"] = pick(rng, [c for c in ["USD", "EUR", "AED", "GBP"] if c != cur])
        elif iss == "LINE_MATH":
            T["lines"][0]["amount"] = round(T["lines"][0]["amount"] * pick(rng, [1.08, 0.92]), 2)
            T["total"] = round(sum(l["amount"] for l in T["lines"]), 2)
            T["amount"] = terms_amount(terms, T["total"], T["stage"])
        elif iss == "PURPOSE_MISMATCH":
            T["purpose"] = pick(rng, B["service_purposes"])
        elif iss == "CONTROLLED_GOODS":
            c = pick(rng, [x for x in B["goods"] if x.get("controlled")])
            qty, price = rng.randint(*c["qty"]), round(rng.uniform(*c["price"]), 2)
            T["lines"][0] = {"desc": c["desc"], "hs": c["hs"], "qty": qty, "unit": c["unit"], "price": price, "amount": round(qty * price, 2)}
            T["bl_lines"][0] = dict(T["lines"][0])
            T["total"] = round(sum(l["amount"] for l in T["lines"]), 2)
            T["amount"] = terms_amount(terms, T["total"], T["stage"])
            T["purpose"] = f"Payment for {T['inv_no']} {c['desc']}"
        elif iss == "SANCTIONED_ROUTE":
            T["route"] = pick(rng, B["bad_routes"])
        elif iss == "DOC_MISMATCH":
            T["has_bl"] = True
            T["bl_lines"][0]["qty"] = int(T["bl_lines"][0]["qty"] * pick(rng, [0.8, 0.6]))
        elif iss == "MILESTONE":
            if "balance" not in stages(terms):
                continue
            T["stage"], T["has_bl"] = "balance", False
            T["amount"] = terms_amount(terms, T["total"], "balance")
        elif iss == "PRICE_ANOMALY":
            l = T["lines"][0]
            l["price"] = round(l["price"] * pick(rng, [4.0, 0.2]), 2)
            l["amount"] = round(l["qty"] * l["price"], 2)
            T["bl_lines"][0]["price"] = l["price"]
            T["total"] = round(sum(x["amount"] for x in T["lines"]), 2)
            T["amount"] = terms_amount(terms, T["total"], T["stage"])
        elif iss == "LISTED_PARTY":
            if "MILESTONE" in T["issues"]:          # that case is about the missing B/L; don't add one
                continue
            lp = pick(rng, B["listed_parties"])
            T["consignee"] = alias(rng, lp, B) if rng.random() < 0.5 else lp.title()
            T["has_bl"] = True
        T["issues"].add(iss)
    T["purpose"] = T["purpose"] if "PURPOSE_MISMATCH" in T["issues"] or rng.random() > B["p_vague_ok"] else f"Goods {T['inv_no']}"
    return T


# ---------------- documents as text ----------------
def money(x):
    return f"{x:,.2f}"


def invoice_text(T, rng):
    if rng.random() < 0.5:
        out = [f"COMMERCIAL INVOICE No. {T['inv_no']}   Date: {T['inv_date'].isoformat()}", f"Seller: {T['seller']['name']}, {T['seller']['country']}",
               f"Buyer: {T['buyer']['name']}, {T['buyer']['country']}", f"Incoterms: {T['route']['incoterm']} {T['route']['pod']}", f"Currency: {T['currency']}",
               "Description | HS code | Qty | Unit | Unit price | Amount"]
        out += [f"{l['desc']} | {l['hs']} | {l['qty']} | {l['unit']} | {money(l['price'])} | {money(l['amount'])}" for l in T["lines"]]
        out += [f"TOTAL {T['currency']} {money(T['total'])}", f"Payment terms: {T['terms']}"]
    else:
        out = [f"INVOICE  {T['inv_no']}", f"Issued {T['inv_date'].strftime('%d.%m.%Y')}", f"From: {T['seller']['name']} ({T['seller']['country']})",
               f"Bill to: {T['buyer']['name']} ({T['buyer']['country']})", f"Terms of delivery {T['route']['incoterm']} {T['route']['pod']}; payment {T['terms']}"]
        for l in T["lines"]:
            hs = l["hs"][:4] + "." + l["hs"][4:]
            out.append(f"- {l['qty']} {l['unit']} {l['desc']} (HS {hs}) @ {T['currency']} {money(l['price'])} = {money(l['amount'])}")
        out.append(f"Amount due: {money(T['total'])} {T['currency']}")
    return "\n".join(out)


def bl_text(T, rng):
    r = T["route"]
    trans = f"Transshipment: {r['via']}" if r.get("via") else "Transshipment: none"
    out = [f"BILL OF LADING No. BL{rng.randint(100000, 999999)}   Date of shipment: {T['bl_date'].isoformat()}", f"Shipper: {T['shipper']}",
           f"Consignee: {T['consignee']}", f"Vessel: {r['vessel']}", f"Port of loading: {r['pol']}", f"Port of discharge: {r['pod_alias'] if rng.random() < 0.5 else r['pod']}",
           trans]
    out += [f"Goods: {l['qty']} {l['unit']} {l['desc']}, HS {l['hs']}" for l in T["bl_lines"]]
    return "\n".join(out)


def payment_text(T, rng):
    return "\n".join([f"PAYMENT INSTRUCTION  value date {T['pay_date'].isoformat()}", f"Ordering customer: {T['ordering']}",
                      f"Beneficiary: {T['beneficiary']}", f"Beneficiary bank country: {T['seller']['country']}",
                      f"Amount: {T['pay_currency']} {money(T['amount'])}", f"Remittance information: {T['purpose']}"])


def case(seed, B, history):
    """-> docs, truth, ledger (payments already sent from this account before this one)."""
    rng = random.Random(seed * 7 + 1)
    ledger = [h["ledger"] for h in history]
    if history and rng.random() < B["p_issue"].get("DUPLICATE_INVOICE", 0):
        prev = pick(rng, history)                       # the same invoice + documents submitted again
        docs = dict(prev["docs"])
        lines = docs["payment"].split("\n")
        lines[0] = f"PAYMENT INSTRUCTION  value date {(prev['pay_date'] + dt.timedelta(days=rng.randint(3, 40))).isoformat()}"
        docs["payment"] = "\n".join(lines)
        truth = {"issues": sorted(set(prev["truth"]["issues"]) | {"DUPLICATE_INVOICE"}), "benign": prev["truth"]["benign"]}
        return docs, truth, ledger
    T = trade(seed, B, history)
    docs = {"invoice": invoice_text(T, rng), "payment": payment_text(T, rng)}
    if T["has_bl"]:
        docs["bl"] = bl_text(T, rng)
    truth = {"issues": sorted(T["issues"]), "benign": T["benign"]}
    history.append({"docs": docs, "truth": truth, "pay_date": T["pay_date"],
                    "ledger": {"inv_no": T["inv_no"], "seller": T["seller"]["name"], "amount": T["amount"], "currency": T["pay_currency"], "stage": T["stage"],
                               "sig": docs_sig(docs)}})
    return docs, truth, ledger
