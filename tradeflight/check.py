"""Parse trade documents and check a payment against them. Every finding cites document + field.

Verdict: READY (with an evidence pack for the bank) / FIX (correct before sending) / HOLD (enhanced due diligence).
"""
import re
import unicodedata

HOLD = {"CONTROLLED_GOODS", "SANCTIONED_ROUTE", "LISTED_PARTY", "DUPLICATE_INVOICE", "PRICE_ANOMALY", "THIRD_PARTY_PAYER", "NAME_MISMATCH"}
LEGAL = {"fze", "fzco", "llc", "gmbh", "co", "company", "ltd", "limited", "private", "pvt", "srl", "doo", "as", "sti", "inc", "sa", "ag", "bv",
         "plc", "corp", "corporation", "spa", "sarl", "jsc", "ooo", "pte", "kft", "sp", "zoo", "oy", "ab", "nv", "sas", "bhd", "sdn"}
SERVICE = re.compile(r"\b(consult\w*|software|licen[cs]e|marketing|services?|loan|retainer|advisory|royalt\w*|subscription|commission)\b", re.I)
NUM = r"[\d,]+\.\d{2}"


def m(x):
    return float(x.replace(",", ""))


# letters NFKD can't split (they'd be silently dropped), and multi-word legal forms
FOLD = str.maketrans({"ß": "ss", "ẞ": "ss", "ł": "l", "Ł": "L", "ı": "i", "İ": "I", "ø": "o", "Ø": "O", "æ": "ae", "Æ": "AE", "đ": "d", "Đ": "D",
                      "þ": "th", "œ": "oe", "Œ": "OE"})
LEGAL_PHRASES = [r"public joint stock company", r"joint stock company", r"limited liability company", r"private limited company",
                 r"sp\s*z\s*o\s*o", r"s\s*a\s*de\s*c\s*v", r"gmbh\s*(?:and|&)?\s*co\s*kg", r"sdn\s*bhd", r"pte\s*ltd", r"ltd\s*sti"]
LEGAL |= {"jsc", "pjsc", "kg", "dmcc", "fzllc"}


def core(name, german=False):
    t = name.translate(FOLD).lower()
    if german:                                  # Mueller ~ Müller: write umlauts as their two-letter spelling
        t = t.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().replace("&", " and ")
    t = re.sub(r"[^a-z0-9 ]", " ", t.replace(".", ""))
    t = " ".join(t.split())
    for ph in LEGAL_PHRASES:
        t = re.sub(rf"\b{ph}\b", " ", t)
    return [w for w in t.split() if w not in LEGAL]


def same_entity(a, b):
    ca = core(a)
    return bool(ca) and (ca == core(b) or core(a, True) == core(b, True))


def similar(a, b):
    ca, cb = set(core(a)), set(core(b))
    if not ca or not cb:
        return False
    return ca == cb or (core(a)[0] == core(b)[0] and len(ca & cb) / len(ca | cb) >= 0.5)


# ---------------- parsing ----------------
def parse_invoice(t):
    d = {}
    if t.startswith("COMMERCIAL INVOICE"):
        d["no"] = re.search(r"No\. (\S+)", t).group(1)
        d["seller"] = re.search(r"Seller: (.+), (\w\w)$", t, re.M).group(1)
        d["buyer"] = re.search(r"Buyer: (.+), (\w\w)$", t, re.M).group(1)
        d["currency"] = re.search(r"Currency: (\w+)", t).group(1)
        d["lines"] = [{"desc": a.strip(), "hs": h.strip(), "qty": float(q), "unit": u.strip(), "price": m(p), "amount": m(am)}
                      for a, h, q, u, p, am in re.findall(rf"^(.+?) \| (\d{{6}}) \| ([\d.]+) \| (\w+) \| ({NUM}) \| ({NUM})$", t, re.M)]
        d["total"] = m(re.search(rf"TOTAL \w+ ({NUM})", t).group(1))
        d["terms"] = re.search(r"Payment terms: (.+)", t).group(1).strip()
    else:
        d["no"] = re.search(r"INVOICE\s+(\S+)", t).group(1)
        d["seller"] = re.search(r"From: (.+) \((\w\w)\)", t).group(1)
        d["buyer"] = re.search(r"Bill to: (.+) \((\w\w)\)", t).group(1)
        d["terms"] = re.search(r"; payment (.+)", t).group(1).strip()
        d["lines"] = []
        for q, u, desc, hs, cur, p, am in re.findall(rf"^- ([\d.]+) (\w+) (.+?) \(HS (\d{{4}}\.\d{{2}})\) @ (\w+) ({NUM}) = ({NUM})$", t, re.M):
            d["lines"].append({"desc": desc, "hs": hs.replace(".", ""), "qty": float(q), "unit": u, "price": m(p), "amount": m(am)})
            d["currency"] = cur
        d["total"] = m(re.search(rf"Amount due: ({NUM})", t).group(1))
    return d


def parse_bl(t):
    g = lambda k: (re.search(rf"^{k}: (.+)$", t, re.M) or [None, ""])[1].strip()  # noqa: E731
    return {"date": re.search(r"Date of shipment: (\S+)", t).group(1), "shipper": g("Shipper"), "consignee": g("Consignee"), "vessel": g("Vessel"),
            "pol": g("Port of loading"), "pod": g("Port of discharge"), "via": g("Transshipment"),
            "goods": [{"qty": float(q), "unit": u, "desc": d, "hs": h} for q, u, d, h in re.findall(r"^Goods: ([\d.]+) (\w+) (.+), HS (\d{6})$", t, re.M)]}


def parse_payment(t):
    g = lambda k: re.search(rf"^{k}: (.+)$", t, re.M).group(1).strip()  # noqa: E731
    cur, amt = re.search(rf"Amount: (\w+) ({NUM})", t).groups()
    return {"date": re.search(r"value date (\S+)", t).group(1), "ordering": g("Ordering customer"), "beneficiary": g("Beneficiary"),
            "bank_country": g("Beneficiary bank country"), "currency": cur, "amount": m(amt), "purpose": g("Remittance information")}


def schedule(terms, total):
    """'30% advance, 70% against B/L copy' / '100% advance' / '100% against B/L copy' / 'net 45 days after B/L date'
    -> {stage: amount due}. 'balance' stages are due against the B/L."""
    t = terms.lower()
    adv = re.search(r"(\d+(?:\.\d+)?)%\s*advance", t)
    a = float(adv.group(1)) / 100 if adv else 0.0
    out = {}
    if a > 0:
        out["advance"] = round(total * a, 2)
    if a < 1:
        out["balance"] = round(total * (1 - a), 2)
    return out


# ---------------- checks ----------------
def check(docs, ledger, L):
    inv, pay = parse_invoice(docs["invoice"]), parse_payment(docs["payment"])
    bl = parse_bl(docs["bl"]) if "bl" in docs else None
    F = []

    def add(kind, why):
        F.append({"kind": kind, "why": why, "level": "HOLD" if kind in HOLD else "FIX"})

    # parties
    listed = []
    parties = [("payment.beneficiary", pay["beneficiary"]), ("payment.ordering", pay["ordering"]), ("invoice.seller", inv["seller"]), ("invoice.buyer", inv["buyer"])]
    if bl:
        parties += [("bl.shipper", bl["shipper"]), ("bl.consignee", bl["consignee"])]
    for where, name in parties:
        for lp in L["listed_parties"]:
            if similar(name, lp):
                listed.append(where)
                add("LISTED_PARTY", f"{where} '{name}' matches listed party '{lp}'")
    if not same_entity(pay["beneficiary"], inv["seller"]):
        add("NAME_MISMATCH", f"payment.beneficiary '{pay['beneficiary']}' is not invoice.seller '{inv['seller']}' (third-party beneficiary needs an assignment letter)")
    if not same_entity(pay["ordering"], inv["buyer"]):
        add("THIRD_PARTY_PAYER", f"payment.ordering '{pay['ordering']}' is not invoice.buyer '{inv['buyer']}'")
    if bl and "bl.consignee" not in listed and not same_entity(bl["consignee"], inv["buyer"]):
        add("DOC_MISMATCH", f"bl.consignee '{bl['consignee']}' is not invoice.buyer '{inv['buyer']}'")
    if bl and "bl.shipper" not in listed and not same_entity(bl["shipper"], inv["seller"]):
        add("DOC_MISMATCH", f"bl.shipper '{bl['shipper']}' is not invoice.seller '{inv['seller']}'")

    # money
    if pay["currency"] != inv["currency"]:
        add("CURRENCY_MISMATCH", f"payment in {pay['currency']}, invoice {inv['no']} in {inv['currency']}")
    for i, l in enumerate(inv["lines"]):
        if abs(l["qty"] * l["price"] - l["amount"]) > 0.011:
            add("LINE_MATH", f"invoice line {i + 1}: {l['qty']:g} x {l['price']:,.2f} = {l['qty'] * l['price']:,.2f}, invoice says {l['amount']:,.2f}")
    if abs(sum(l["amount"] for l in inv["lines"]) - inv["total"]) > 0.011:
        add("LINE_MATH", f"invoice lines sum to {sum(l['amount'] for l in inv['lines']):,.2f}, total says {inv['total']:,.2f}")
    prior = [x for x in ledger if x["inv_no"] == inv["no"] and same_entity(x["seller"], inv["seller"])]
    paid_before = sum(x["amount"] for x in prior)
    total = inv["total"]
    terms = inv["terms"]
    expect = schedule(terms, total)
    cands = [k for k, v in expect.items() if abs(pay["amount"] - v) <= max(0.01, v * 0.002)]
    paid_stages = {x["stage"] for x in prior}
    sig = docs_sig(docs)
    same_docs = [x for x in prior if x.get("sig") == sig and abs(x["amount"] - pay["amount"]) < 0.01]
    unpaid = [c for c in cands if c not in paid_stages]
    if len(unpaid) > 1:                         # 50/50-style terms: the amount fits both stages
        unpaid = ["balance"] if bl and bl["date"] <= pay["date"] else ["advance"]
    stage = unpaid[0] if unpaid else (cands[0] if cands else None)
    if same_docs or (prior and cands and not unpaid) or (prior and paid_before + pay["amount"] > total + 0.01):
        why = (f"the same invoice{' and B/L' if bl else ''} already backed a payment of {same_docs[0]['amount']:,.2f}" if same_docs else
               f"invoice {inv['no']} already paid {paid_before:,.2f} ({', '.join(sorted(paid_stages))})")
        add("DUPLICATE_INVOICE", f"{why}; this would bring it to {paid_before + pay['amount']:,.2f} of {total:,.2f}")
    if stage is None:
        add("AMOUNT_MISMATCH", f"payment {pay['amount']:,.2f} matches none of the amounts due under '{terms}' on {total:,.2f}: "
                               + ", ".join(f"{k} {v:,.2f}" for k, v in expect.items()))
    if stage == "balance":
        if not bl:
            add("MILESTONE", f"'{terms}': balance {pay['amount']:,.2f} is due against the B/L, and no B/L is attached")
        elif bl["date"] > pay["date"]:
            add("MILESTONE", f"balance value date {pay['date']} is before shipment {bl['date']}")

    # goods
    for l in inv["lines"]:
        if l["hs"] in L["controlled_hs"]:
            add("CONTROLLED_GOODS", f"invoice line '{l['desc']}' HS {l['hs']} is on the controlled-goods list: export licence / end-user statement needed")
        band = L["price_bands"].get(l["hs"])
        if band and not (band[0] * 0.5 <= l["price"] <= band[1] * 2):
            add("PRICE_ANOMALY", f"'{l['desc']}' at {l['price']:,.2f}/{l['unit']} vs typical {band[0]:,.0f}-{band[1]:,.0f} (over/under-invoicing check)")
    if SERVICE.search(pay["purpose"]):
        add("PURPOSE_MISMATCH", f"remittance says '{pay['purpose']}', documents are goods ({inv['lines'][0]['desc']}). "
                                f"Use: 'Payment for {inv['no']} {inv['lines'][0]['desc']} HS {inv['lines'][0]['hs']}'")
    # route: B/L ports + transshipment, and the invoice's delivery place (all there is before shipment)
    inv_place = re.search(r"(?:Incoterms: |Terms of delivery )\w+ ([^;\n]+)", docs["invoice"])
    route = " ".join(([bl["pol"], bl["pod"], bl["via"]] if bl else []) + ([inv_place.group(1)] if inv_place else [])).lower()
    for place, code in L["sanctioned_places"].items():
        if re.search(rf"\b{re.escape(place)}\b", route):
            src = f"B/L {bl['pol']} -> {bl['pod']} ({bl['via']})" if bl else f"invoice delivery place {inv_place.group(1)}"
            add("SANCTIONED_ROUTE", f"route touches {place.title()} ({code}): {src}")
            break
    if bl:
        for l in inv["lines"]:
            g = next((x for x in bl["goods"] if x["hs"] == l["hs"]), None)
            if g is None:
                add("DOC_MISMATCH", f"invoice HS {l['hs']} ({l['desc']}) is not on the B/L")
            elif abs(g["qty"] - l["qty"]) > max(0.5, 0.02 * l["qty"]):
                add("DOC_MISMATCH", f"B/L ships {g['qty']:g} {g['unit']} {l['desc']}, invoice bills {l['qty']:g}")

    F = _dedupe(F)
    v = "HOLD" if any(f["level"] == "HOLD" for f in F) else ("FIX" if F else "READY")
    pack = evidence_pack(inv, pay, bl, stage, paid_before) if v == "READY" else None
    return v, F, pack


def docs_sig(docs):
    """Fingerprint of the trade documents behind a payment (what an account's payment ledger keeps)."""
    import hashlib
    return hashlib.sha256((docs["invoice"] + "\n--\n" + docs.get("bl", "")).encode()).hexdigest()[:16]


def _dedupe(F):
    seen, out = set(), []
    for f in F:
        if (f["kind"], f["why"]) not in seen:
            seen.add((f["kind"], f["why"]))
            out.append(f)
    return out


def evidence_pack(inv, pay, bl, stage, paid_before):
    l0 = inv["lines"][0]
    out = [f"Underlying trade: {inv['no']} - {inv['seller']} sells {', '.join(f'{l['qty']:g} {l['unit']} {l['desc']} (HS {l['hs']})' for l in inv['lines'])} "
           f"to {inv['buyer']}, total {inv['currency']} {inv['total']:,.2f}, terms '{inv['terms']}'.",
           f"This payment: {pay['currency']} {pay['amount']:,.2f} = {stage} under the terms; previously paid on this invoice {paid_before:,.2f}.",
           f"Parties match: beneficiary = invoice seller; ordering customer = invoice buyer."]
    if bl:
        out.append(f"Shipment: B/L dated {bl['date']}, {bl['pol']} -> {bl['pod']} on {bl['vessel']}, goods and quantities match the invoice.")
    out.append(f"Suggested remittance text: Payment for {inv['no']} {l0['desc']} HS {l0['hs']}")
    return "\n".join(out)
