from app.agents.reception import handle_reception
from app.agents.doctors import handle_doctors
from app.agents.departments import handle_departments
from app.agents.billing import handle_billing
from app.rag.retriever import retrieve
from app.agents.common import llm_answer_stream


def is_smalltalk(q: str) -> str | None:
    q = q.strip().lower()
    if len(q.split()) > 3:
        return None

    thanks = ["faleminderit", "shume faleminderit", "flm", "rrofsh", "thanks", "thank you"]
    hello = ["pershendetje", "përshëndetje", "hi", "hello", "tung", "mirëdita", "miremengjes", "mirëmëngjes", "mirembrema", "mirëmbrëma"]
    bye = ["mirupafshim", "shihemi", "bye", "natën e mirë", "naten e mire", "goodbye"]
    ok_words = ["ok", "okay", "mirë", "mire", "dakord", "në rregull", "ne rregull", "super"]

    if q in hello:
        return "Përshëndetje! Si mund t'ju ndihmoj?"
    if q in thanks:
        return "Me kënaqësi! Nëse keni pyetje tjetër, jam këtu."
    if q in bye:
        return "Mirupafshim! Ju uroj shëndet të mirë."
    if q in ok_words:
        return "Dakord. A ka diçka tjetër që dëshironi të dini?"

    return None


def normalize_followup(question: str, history: list) -> str:
    q = question.strip().lower()
    followups = ["po", "po tjeter", "tjeter", "edhe", "jo", "jo tjeter"]
    if q in followups and history:
        for h in reversed(history):
            if h.get("role") == "user":
                return f"{h.get('content')}. Jep më shumë informacion."
    return question


def _pick_agent(question: str) -> str:
    q = question.lower()
    billing_kw    = ["cmim", "çmim", "pages", "pagese", "fature", "fatur", "kosto", "paket",
                     "sigurim", "analiza", "analizat", "laborator", "tarifa",
                     "price", "cost", "billing", "payment", "package", "insurance"]
    doctors_kw    = ["mjek", "doktor", "specialist", "prof", "dr",
                     "doctor", "physician", "surgeon"]
    departments_kw = ["departament", "sherbim", "shërbim", "ku te shkoj", "ku duhet",
                      "klinike", "klinikë", "department", "service", "ward", "unit"]
    reception_kw  = ["orari", "kontakt", "adrese", "adresë", "rezerv", "takim", "parking",
                     "vendndodhje", "hours", "contact", "address", "appointment", "schedule",
                     "location", "directions"]

    if any(k in q for k in billing_kw):
        return "billing"
    if any(k in q for k in doctors_kw):
        return "doctors"
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
