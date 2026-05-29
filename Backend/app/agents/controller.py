from app.agents.reception import handle_reception
from app.agents.doctors import handle_doctors
from app.agents.departments import handle_departments
from app.agents.billing import handle_billing
from app.rag.retriever import retrieve
from app.agents.common import llm_answer_stream


def _is_english(q: str) -> bool:
    english_words = {"hi", "hello", "thanks", "thank you", "bye", "goodbye", "ok", "okay",
                     "yes", "no", "sure", "great", "more", "also", "and", "other"}
    return any(w in q.split() for w in english_words)


def is_smalltalk(q: str) -> str | None:
    q = q.strip().lower()
    if len(q.split()) > 3:
        return None

    english_hello = ["hi", "hello"]
    english_thanks = ["thanks", "thank you"]
    english_bye = ["bye", "goodbye"]
    english_ok = ["ok", "okay", "sure", "great"]

    albanian_hello = ["pershendetje", "përshëndetje", "tung", "mirëdita", "miremengjes", "mirëmëngjes", "mirembrema", "mirëmbrëma"]
    albanian_thanks = ["faleminderit", "shume faleminderit", "flm", "rrofsh"]
    albanian_bye = ["mirupafshim", "shihemi", "natën e mirë", "naten e mire"]
    albanian_ok = ["mirë", "mire", "dakord", "në rregull", "ne rregull", "super"]

    if q in english_hello:
        return "Hello! How can I help you?"
    if q in english_thanks:
        return "You're welcome! If you have any other questions, I'm here."
    if q in english_bye:
        return "Goodbye! Wishing you good health."
    if q in english_ok:
        return "Sure. Is there anything else you'd like to know?"

    if q in albanian_hello:
        return "Përshëndetje! Si mund t'ju ndihmoj?"
    if q in albanian_thanks:
        return "Me kënaqësi! Nëse keni pyetje tjetër, jam këtu."
    if q in albanian_bye:
        return "Mirupafshim! Ju uroj shëndet të mirë."
    if q in albanian_ok:
        return "Dakord. A ka diçka tjetër që dëshironi të dini?"

    return None


def normalize_followup(question: str, history: list) -> str:
    q = question.strip().lower()
    albanian_followups = ["po", "po tjeter", "tjeter", "edhe", "jo", "jo tjeter"]
    english_followups = ["yes", "more", "also", "and", "no", "other", "what else"]
    if q in albanian_followups and history:
        for h in reversed(history):
            if h.get("role") == "user":
                return f"{h.get('content')}. Jep më shumë informacion."
    if q in english_followups and history:
        for h in reversed(history):
            if h.get("role") == "user":
                return f"{h.get('content')}. Give more information."
    return question


def _pick_agent(question: str) -> str:
    q = question.lower()
    billing_kw     = ["cmim", "çmim", "pages", "pagese", "fature", "fatur", "kosto", "paket",
                      "sigurim", "tarifa",
                      "price", "cost", "billing", "payment", "package", "insurance"]
    doctors_kw     = ["mjek", "doktor", "specialist", "prof", "dr",
                      "doctor", "physician", "surgeon"]
    departments_kw = ["departament", "sherbim", "shërbim", "ku te shkoj", "ku duhet",
                      "klinike", "klinikë", "department", "service", "ward", "unit"]
    symptom_kw     = ["dhimbje", "dhemb", "pain", "hurts", "hurt", "ache", "aching",
                      "stomach", "barku", "barkun", "chest", "gjoks", "head", "kokë", "koka",
                      "back", "shpinë", "shpina", "kollë", "cough", "temperature", "fever",
                      "lodhje", "tired", "nausea", "të vjella", "vomit", "vomiting",
                      "breathing", "frymëmarrje", "urine", "urinar", "joint", "kyç",
                      "skin", "lëkurë", "rash", "skuqje", "vision", "shikim", "shikimi",
                      "ear", "vesh", "nose", "hundë", "throat", "fyt", "feel sick",
                      "ndihem", "symptom", "simptomë", "problem me", "probleme me",
                      "i have", "kam", "me dhemb", "my"]
    reception_kw   = ["orari", "kontakt", "adrese", "adresë", "rezerv", "takim", "parking",
                      "vendndodhje", "hours", "contact", "address", "appointment", "schedule",
                      "location", "directions", "book", "rezervim"]

    if any(k in q for k in billing_kw):
        return "billing"
    if any(k in q for k in doctors_kw):
        return "doctors"
    if any(k in q for k in symptom_kw):
        return "departments"
    if any(k in q for k in departments_kw):
        return "departments"
    if any(k in q for k in reception_kw):
        return "reception"
    return "reception"


def route_question(question: str, history=None) -> dict:
    if history is None:
        history = []

    small = is_smalltalk(question)
    if small:
        return {"agent": "smalltalk", "answer": small, "sources": []}

    question = normalize_followup(question, history)
    agent = _pick_agent(question)

    handlers = {
        "billing": handle_billing,
        "doctors": handle_doctors,
        "departments": handle_departments,
        "reception": handle_reception,
    }
    return handlers[agent](question, history=history)


def route_question_stream(question: str, history=None):
    """Yields dicts: {token: str} while streaming, then {done: True, agent, sources} at end."""
    if history is None:
        history = []

    small = is_smalltalk(question)
    if small:
        yield {"token": small}
        yield {"done": True, "agent": "smalltalk", "sources": []}
        return

    question = normalize_followup(question, history)
    agent = _pick_agent(question)

    hits = retrieve(agent, question, k=10)
    sources = [{"file": h["source"], "score": round(h["score"], 3)} for h in hits]
    context = "\n\n".join(h["text"] for h in hits) if hits else ""

    for token in llm_answer_stream(question, context, history=history):
        yield {"token": token}

    yield {"done": True, "agent": agent, "sources": sources}
