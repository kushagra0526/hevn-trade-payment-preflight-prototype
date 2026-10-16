import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tradeflight.bank_dev import BANK
from tradeflight.check import check, same_entity, schedule
from tradeflight.synth import case

INV = """COMMERCIAL INVOICE No. INV-1   Date: 2026-03-01
Seller: Müller Agrarhandel GmbH & Co. KG, DE
Buyer: Volga Timber Joint Stock Company, KZ
Incoterms: CFR Koper
Currency: USD
Description | HS code | Qty | Unit | Unit price | Amount
Urea 46% granular | 310210 | 1000 | MT | 300.00 | 300,000.00
TOTAL USD 300,000.00
Payment terms: 30% advance, 70% against B/L copy"""


def pay(amount, purpose="Payment for INV-1 Urea", ben="MUELLER AGRARHANDEL GMBH AND CO KG", ordering="Volga Timber JSC", cur="USD"):
    return (f"PAYMENT INSTRUCTION  value date 2026-03-05\nOrdering customer: {ordering}\nBeneficiary: {ben}\nBeneficiary bank country: DE\n"
            f"Amount: {cur} {amount:,.2f}\nRemittance information: {purpose}")


def kinds(docs, ledger=()):
    v, F, pack = check(docs, list(ledger), BANK)
    return v, {f["kind"] for f in F}, pack


def test_names_and_terms():
    assert same_entity("Öztürk Tekstil A.Ş.", "OZTURK TEKSTIL AS") and same_entity("Größer GmbH", "Groesser G.m.b.H.")
    assert not same_entity("Gulf Steel Trading FZE", "Gulf Steel Holdings Ltd")
    assert schedule("20% advance, 80% against B/L copy", 100) == {"advance": 20.0, "balance": 80.0}


def test_clean_advance_is_ready_with_pack():
    v, k, pack = kinds({"invoice": INV, "payment": pay(90000.00)})
    assert v == "READY" and not k and "advance" in pack


def test_balance_without_bl_and_wrong_amount():
    assert kinds({"invoice": INV, "payment": pay(210000.00)})[1] == {"MILESTONE"}
    assert kinds({"invoice": INV, "payment": pay(300000.00)})[1] == {"AMOUNT_MISMATCH"}


def test_purpose_third_party_currency():
    v, k, _ = kinds({"invoice": INV, "payment": pay(90000.00, purpose="Consulting services Q3", ordering="Pearl Logistics LLC", cur="EUR")})
    assert v == "HOLD" and k == {"PURPOSE_MISMATCH", "THIRD_PARTY_PAYER", "CURRENCY_MISMATCH"}


def test_route_from_invoice_before_shipment():
    inv = INV.replace("CFR Koper", "CFR Bandar Abbas")
    assert "SANCTIONED_ROUTE" in kinds({"invoice": inv, "payment": pay(90000.00)})[1]


def test_duplicate_by_ledger():
    led = [{"inv_no": "INV-1", "seller": "Müller Agrarhandel GmbH & Co. KG", "amount": 90000.00, "stage": "advance"}]
    assert "DUPLICATE_INVOICE" in kinds({"invoice": INV, "payment": pay(90000.00)}, led)[1]


def test_dev_bank_no_false_stops():
    hist = []
    for s in range(1, 301):
        docs, truth, ledger = case(s, BANK, hist)
        v, F, _ = check(docs, ledger, BANK)
        if not truth["issues"]:
            assert v == "READY", (s, F)
