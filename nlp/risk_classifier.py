import logging

log = logging.getLogger(__name__)

RISK_KEYWORDS = {
    "military": [
        "war", "missile", "troops", "military", "attack", "bomb", "strike",
        "invasion", "soldier", "weapon", "conflict", "ceasefire", "nuclear",
        "navy", "army", "airstrike", "combat", "artillery", "blockade",
        "hostage", "terrorist", "insurgent", "drone", "escalation"
    ],
    "economic": [
        "sanction", "tariff", "trade war", "recession", "inflation", "gdp",
        "currency", "debt", "bank", "stock", "market crash", "embargo",
        "export", "import", "supply chain", "oil price", "commodity",
        "financial", "economic crisis", "default", "fiscal", "investment"
    ],
    "political": [
        "election", "coup", "government", "president", "parliament", "protest",
        "diplomat", "treaty", "negotiation", "alliance", "sanction", "veto",
        "united nations", "nato", "summit", "policy", "regime", "opposition",
        "democracy", "authoritarian", "referendum", "minister", "congress"
    ],
    "energy": [
        "oil", "gas", "petroleum", "pipeline", "opec", "fuel", "energy",
        "strait of hormuz", "lng", "coal", "nuclear power", "electricity",
        "power grid", "refinery", "barrel", "crude", "natural gas",
        "energy crisis", "power shortage", "renewable", "solar"
    ]
}

def classify_risk(title: str, description: str = "", content: str = "") -> dict:
    combined = f"{title} {description} {content}".lower()

    scores = {category: 0 for category in RISK_KEYWORDS}

    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined:
                scores[category] += 1

    top_category = max(scores, key=scores.get)
    top_score    = scores[top_category]

    if top_score == 0:
        return {"category": "general", "score": 1, "all_scores": scores}

    normalized = min(10, max(1, round((top_score / len(RISK_KEYWORDS[top_category])) * 10 * 3)))

    return {
        "category":   top_category,
        "score":      normalized,
        "all_scores": scores
    }