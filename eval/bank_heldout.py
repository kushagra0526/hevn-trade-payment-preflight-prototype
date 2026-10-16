"""Held-out bank. Committed to git before the first run; never tuned against. All parties/vessels fictional; lists illustrative.

New: companies and legal forms (GmbH & Co. KG, Sp. z o.o., S.A. de C.V., Pte. Ltd., Sdn. Bhd., Joint Stock Company/JSC),
German/Polish/Turkish romanisations (ü->ue, ö->oe, ß->ss, ł->l, ğ->g), goods, routes, payment terms (20/80, 50/50, net 45),
listed parties, purposes.
"""

BANK = {
    "companies": [
        {"name": "Müller Agrarhandel GmbH & Co. KG", "country": "DE"}, {"name": "Baltic Amber Trade Sp. z o.o.", "country": "PL"},
        {"name": "Aceros del Norte S.A. de C.V.", "country": "MX"}, {"name": "Straits Rice Pte. Ltd.", "country": "SG"},
        {"name": "Kenanga Palm Sdn. Bhd.", "country": "MY"}, {"name": "Volga Timber Joint Stock Company", "country": "KZ"},
        {"name": "Doğan Gıda Sanayi A.Ş.", "country": "TR"}, {"name": "Łódź Textile Works Sp. z o.o.", "country": "PL"},
        {"name": "Al Noor General Trading LLC", "country": "AE"}, {"name": "Größer Maschinenbau GmbH", "country": "DE"},
        {"name": "Mekong Seafood Joint Stock Company", "country": "VN"},
    ],
    "form_variants": [("GmbH & Co. KG", "GmbH and Co KG"), ("Sp. z o.o.", "Sp z oo"), ("S.A. de C.V.", "SA de CV"), ("Pte. Ltd.", "Pte Ltd"),
                      ("Sdn. Bhd.", "Sdn Bhd"), ("Joint Stock Company", "JSC"), ("LLC", "L.L.C."), ("A.Ş.", "AS"), ("GmbH", "G.m.b.H.")],
    "translit": [("ü", "ue"), ("ö", "oe"), ("ß", "ss"), ("Ł", "L"), ("ł", "l"), ("ğ", "g"), ("ı", "i"), ("Ş", "S"), ("ó", "o")],
    "goods": [
        {"desc": "Aluminium ingots P1020", "hs": "760110", "unit": "MT", "qty": (50, 600), "price": (2200, 2700)},
        {"desc": "Long-grain white rice 5% broken", "hs": "100630", "unit": "MT", "qty": (200, 3000), "price": (420, 560)},
        {"desc": "Crude palm oil", "hs": "151110", "unit": "MT", "qty": (500, 5000), "price": (780, 980)},
        {"desc": "Frozen vannamei shrimp", "hs": "030617", "unit": "KG", "qty": (5000, 60000), "price": (6.5, 9.8)},
        {"desc": "Monocrystalline solar modules 550W", "hs": "854143", "unit": "PCS", "qty": (500, 8000), "price": (85, 120)},
        {"desc": "Sawn pine timber", "hs": "440711", "unit": "M3", "qty": (200, 3000), "price": (180, 260)},
        {"desc": "Denim fabric 12oz", "hs": "520942", "unit": "M", "qty": (10000, 120000), "price": (2.2, 3.6)},
        {"desc": "Unmanned aerial vehicles (quadcopters)", "hs": "880699", "unit": "PCS", "qty": (10, 400), "price": (1500, 6000), "controlled": True},
        {"desc": "Hydraulic presses, numerically controlled", "hs": "846241", "unit": "SET", "qty": (1, 4), "price": (120000, 260000), "controlled": True},
    ],
    "controlled_hs": ["880699", "846241", "845910", "852589", "930190"],
    "terms": ["100% advance", "20% advance, 80% against B/L copy", "50% advance, 50% against B/L copy", "net 45 days after B/L date"],
    "routes": [
        {"pol": "Port Klang", "pod": "Gdansk", "pod_alias": "Port of Gdańsk", "vessel": "EVER GIVEN STAR", "incoterm": "CIF"},
        {"pol": "Hai Phong", "pod": "Jebel Ali", "pod_alias": "Jebel Ali Free Zone", "vessel": "ONE HARMONY", "incoterm": "CFR"},
        {"pol": "Veracruz", "pod": "Hamburg", "pod_alias": "Hamburg (DE)", "vessel": "HAMBURG SUD RIO", "incoterm": "FOB"},
        {"pol": "Aktau", "pod": "Baku", "pod_alias": "Port of Baku (Alat)", "vessel": "CASPIAN PEARL", "incoterm": "DAP"},
        {"pol": "Singapore", "pod": "Mundra", "pod_alias": "Mundra Port", "vessel": "KOTA PERDANA", "incoterm": "CIF", "via": "Colombo"},
        {"pol": "Mersin", "pod": "Durres", "pod_alias": "Port of Durrës", "vessel": "ARKAS IZMIR", "incoterm": "CFR"},
    ],
    "bad_routes": [
        {"pol": "Jebel Ali", "pod": "Bandar Imam Khomeini", "pod_alias": "Bandar Imam Khomeini (IR)", "vessel": "DESERT ROSE", "incoterm": "CFR"},
        {"pol": "Mersin", "pod": "Tartus", "pod_alias": "Tartus, Syria", "vessel": "NIKOLAOS", "incoterm": "CIF"},
        {"pol": "Dalian", "pod": "Vladivostok", "pod_alias": "Vladivostok", "vessel": "HAIYANG 7", "incoterm": "FOB", "via": "Chongjin"},
        {"pol": "Veracruz", "pod": "Mariel", "pod_alias": "Mariel, Cuba", "vessel": "CARIBE SOL", "incoterm": "CFR"},
    ],
    "sanctioned_places": {"bandar imam khomeini": "IR", "bandar abbas": "IR", "iran": "IR", "tartus": "SY", "latakia": "SY", "syria": "SY",
                          "chongjin": "KP", "nampo": "KP", "north korea": "KP", "mariel": "CU", "havana": "CU", "cuba": "CU",
                          "sevastopol": "Crimea", "crimea": "Crimea"},
    "listed_parties": ["CASPIAN HORIZON SHIPPING JSC", "MERIDIAN STAR TRADING FZE", "OCEANIC BRIDGE LOGISTICS PTE LTD", "TALON INDUSTRIAL SUPPLY LLC"],
    "other_beneficiaries": ["{first} Group Holdings", "Prime Commodities DMCC", "{first} Capital Partners"],
    "service_purposes": ["Advisory fee", "IT support services", "Commission payment", "Subscription renewal", "Royalties Q2"],
    "price_bands": {},
    "p_issue": {"NAME_MISMATCH": 0.06, "THIRD_PARTY_PAYER": 0.06, "AMOUNT_MISMATCH": 0.06, "CURRENCY_MISMATCH": 0.04, "DUPLICATE_INVOICE": 0.05,
                "LINE_MATH": 0.04, "PURPOSE_MISMATCH": 0.05, "CONTROLLED_GOODS": 0.05, "SANCTIONED_ROUTE": 0.05, "DOC_MISMATCH": 0.05,
                "MILESTONE": 0.05, "PRICE_ANOMALY": 0.04, "LISTED_PARTY": 0.04},
    "p_vague_ok": 0.25,
}
for g in BANK["goods"]:
    BANK["price_bands"][g["hs"]] = g["price"]
SEEDS = range(30_001, 31_501)   # 1,500 payments
