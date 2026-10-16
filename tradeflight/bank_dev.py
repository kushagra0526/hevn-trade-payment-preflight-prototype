"""Dev bank. All companies, vessels and listed parties are fictional. Lists are illustrative, not legal lists."""

BANK = {
    "companies": [
        {"name": "Gulf Steel Trading FZE", "country": "AE"}, {"name": "Novak Metals d.o.o.", "country": "SI"},
        {"name": "Anatolia Agro Gida Ltd. Sti.", "country": "TR"}, {"name": "Rhein Fertilizer GmbH", "country": "DE"},
        {"name": "Pearl Logistics LLC", "country": "AE"}, {"name": "Shenzhen Brightway Electronics Co., Ltd.", "country": "CN"},
        {"name": "Öztürk Tekstil A.Ş.", "country": "TR"}, {"name": "Danube Grain S.R.L.", "country": "RO"},
        {"name": "Kaveri Polymers Private Limited", "country": "IN"}, {"name": "Lagos Cocoa Exports Limited", "country": "NG"},
    ],
    "form_variants": [("FZE", "F.Z.E."), ("LLC", "L.L.C."), ("GmbH", "G.m.b.H."), ("Co., Ltd.", "Company Limited"), ("Private Limited", "Pvt Ltd"),
                      ("Limited", "Ltd"), ("S.R.L.", "SRL"), ("d.o.o.", "DOO"), ("A.Ş.", "AS"), ("Ltd. Sti.", "Ltd Sti")],
    "translit": [("Ö", "O"), ("ü", "u"), ("ı", "i"), ("Ş", "S")],
    "goods": [
        {"desc": "Hot-rolled steel coils", "hs": "720839", "unit": "MT", "qty": (100, 900), "price": (520, 680)},
        {"desc": "Urea 46% granular", "hs": "310210", "unit": "MT", "qty": (200, 2000), "price": (280, 380)},
        {"desc": "Refined sunflower oil", "hs": "151219", "unit": "MT", "qty": (50, 500), "price": (900, 1150)},
        {"desc": "Copper cathodes", "hs": "740311", "unit": "MT", "qty": (20, 200), "price": (8200, 9600)},
        {"desc": "LLDPE granules", "hs": "390140", "unit": "MT", "qty": (40, 400), "price": (950, 1250)},
        {"desc": "Cotton T-shirts", "hs": "610910", "unit": "PCS", "qty": (5000, 60000), "price": (1.8, 3.5)},
        {"desc": "Laptops 14-inch", "hs": "847130", "unit": "PCS", "qty": (100, 2000), "price": (310, 520)},
        {"desc": "5-axis CNC milling machines", "hs": "845910", "unit": "SET", "qty": (1, 6), "price": (90000, 160000), "controlled": True},
        {"desc": "Thermal imaging camera cores", "hs": "852589", "unit": "PCS", "qty": (20, 300), "price": (900, 2400), "controlled": True},
    ],
    "controlled_hs": ["845910", "852589", "880699", "930190", "284440"],
    "terms": ["100% advance", "30% advance, 70% against B/L copy", "100% against B/L copy"],
    "routes": [
        {"pol": "Jebel Ali", "pod": "Koper", "pod_alias": "Port of Koper", "vessel": "MSC ARIANNA", "incoterm": "CFR"},
        {"pol": "Constanta", "pod": "Mersin", "pod_alias": "Mersin Intl Port", "vessel": "CMA CGM RHONE", "incoterm": "FOB"},
        {"pol": "Hamburg", "pod": "Jebel Ali", "pod_alias": "Jebel Ali (Dubai)", "vessel": "HAPAG ESSEN", "incoterm": "CIF"},
        {"pol": "Shekou", "pod": "Jebel Ali", "pod_alias": "Jebel Ali, Dubai", "vessel": "COSCO SHIPPING ARIES", "incoterm": "CIF", "via": "Port Klang"},
        {"pol": "Nhava Sheva", "pod": "Rotterdam", "pod_alias": "Rotterdam Maasvlakte", "vessel": "MAERSK EINDHOVEN", "incoterm": "CFR"},
        {"pol": "Lagos (Apapa)", "pod": "Antwerp", "pod_alias": "Antwerp-Bruges", "vessel": "GRANDE TEMA", "incoterm": "FOB"},
    ],
    "bad_routes": [
        {"pol": "Jebel Ali", "pod": "Bandar Abbas", "pod_alias": "Bandar Abbas, Iran", "vessel": "SEA LOTUS", "incoterm": "CFR"},
        {"pol": "Mersin", "pod": "Latakia", "pod_alias": "Latakia (SY)", "vessel": "BLUE HERON", "incoterm": "CIF"},
        {"pol": "Shekou", "pod": "Busan", "pod_alias": "Busan", "vessel": "ORIENT STAR", "incoterm": "CIF", "via": "Nampo"},
        {"pol": "Constanta", "pod": "Sevastopol", "pod_alias": "Sevastopol, Crimea", "vessel": "KAIROS", "incoterm": "FOB"},
    ],
    "sanctioned_places": {"bandar abbas": "IR", "iran": "IR", "latakia": "SY", "syria": "SY", "nampo": "KP", "north korea": "KP",
                          "sevastopol": "Crimea", "crimea": "Crimea", "havana": "CU", "cuba": "CU"},
    "listed_parties": ["ROSMAR SHIPPING COMPANY", "ALTAIR GLOBAL TRADING LLC", "NORTHGATE MARINE SERVICES FZE"],
    "other_beneficiaries": ["{first} Holdings Ltd", "Global Commodities FZCO", "{first} Investments Inc."],
    "service_purposes": ["Consulting services Q3", "Software license fee", "Marketing services retainer", "Loan repayment"],
    "price_bands": {},   # filled from goods
    "p_issue": {"NAME_MISMATCH": 0.06, "THIRD_PARTY_PAYER": 0.05, "AMOUNT_MISMATCH": 0.06, "CURRENCY_MISMATCH": 0.04, "DUPLICATE_INVOICE": 0.04,
                "LINE_MATH": 0.04, "PURPOSE_MISMATCH": 0.05, "CONTROLLED_GOODS": 0.04, "SANCTIONED_ROUTE": 0.04, "DOC_MISMATCH": 0.05,
                "MILESTONE": 0.05, "PRICE_ANOMALY": 0.04, "LISTED_PARTY": 0.03},
    "p_vague_ok": 0.2,
}
for g in BANK["goods"]:
    BANK["price_bands"][g["hs"]] = g["price"]
