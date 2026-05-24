import spacy
import logging

log = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")

COUNTRY_LIST = {
    "usa", "united states", "america", "russia", "china", "iran", "ukraine",
    "israel", "india", "pakistan", "taiwan", "north korea", "south korea",
    "germany", "france", "uk", "britain", "japan", "saudi arabia", "turkey",
    "brazil", "australia", "canada", "cuba", "venezuela", "syria", "iraq",
    "afghanistan", "egypt", "qatar", "uae", "indonesia", "malaysia",
    "nigeria", "ethiopia", "poland", "finland", "sweden", "norway"
}

def extract_entities(text: str) -> dict:
    if not text or not text.strip():
        return {"countries": [], "organizations": [], "people": [], "all_entities": []}

    doc = nlp(text[:10000])

    countries      = set()
    organizations  = set()
    people         = set()
    all_entities   = []

    for ent in doc.ents:
        text_lower = ent.text.strip().lower()
        entry = {"text": ent.text.strip(), "type": ent.label_}
        all_entities.append(entry)

        if ent.label_ == "GPE":
            if text_lower in COUNTRY_LIST:
                countries.add(ent.text.strip())
            elif len(ent.text.strip()) > 2:
                countries.add(ent.text.strip())

        elif ent.label_ == "ORG":
            organizations.add(ent.text.strip())

        elif ent.label_ == "PERSON":
            people.add(ent.text.strip())

    return {
        "countries":     list(countries),
        "organizations": list(organizations),
        "people":        list(people),
        "all_entities":  all_entities
    }