from app.agents.reception import handle_reception
from app.agents.doctors import handle_doctors
from app.agents.departments import handle_departments
from app.agents.billing import handle_billing


def is_smalltalk(q: str) -> str | None:
    q = q.strip().lower()
    if len(q.split()) > 3:
        return None

    thanks = ["faleminderit", "shume faleminderit", "flm", "rrofsh", "thanks", "thank you"]
    hello = ["pershendetje", "përshëndetje", "hi", "hello", "tung", "mirëdita", "miremengjes", "mirëmëngjes", "mirembrema", "mirëmbrëma"]
    bye = ["mirupafshim", "shihemi", "bye", "natën e mirë", "naten e mire", "goodbye"]
    ok_words = ["ok", "okay", "mirë", "mire", "dakord", "në rregull", "ne rregull", "super"]

    if q in hello:
        return "Përshëndetje! Si mund t’ju ndihmoj?"
    if q in thanks:
        return "Me kënaqësi! Nëse keni pyetje tjetër, jam këtu."
    if q in bye:
        return "Mirupafshim! Ju uroj shëndet të mirë."
    if q in ok_words:
        return "Dakord. A ka diçka tjetër që dëshironi të dini?"

    return None

def normalize_followup(question: str, history: list[str]) -> str:
    q = question.strip().lower()

    followups = ["po", "po tjeter", "tjeter", "edhe", "jo", "jo tjeter"]

    if q in followups and history:
        last_user_question = ""
        for h in reversed(history):
            if h.get("role") == "user":
                last_user_question = h.get("content")
                break

        if last_user_question:
            return f"{last_user_question}. Jep më shumë informacion."

    return question


def route_question(question: str, history=None) -> dict:
    if history is None:
        history = []

    small = is_smalltalk(question)
    if small:
        return {"agent": "smalltalk", "answer": small, "sources": []}
    q = question.lower()

    billing_keywords = ["cmim", "çmim", "pages", "pagese", "fature", "fatur", "kosto", "paket", "sigurim", "analiza", "analizat", "laborator", "tarifa"]
    doctors_keywords = ["mjek", "doktor", "specialist", "prof", "dr"]
    departments_keywords = ["departament", "sherbim", "shërbim", "ku te shkoj", "ku duhet", "klinike", "klinikë"]
    reception_keywords = ["orari", "kontakt", "adrese", "adresë", "rezerv", "takim", "parking", "vendndodhje"]

    if any(k in q for k in billing_keywords):
        return handle_billing(question, history=history)

    if any(k in q for k in doctors_keywords):
        return handle_doctors(question, history=history)

    if any(k in q for k in departments_keywords):
        return handle_departments(question, history=history)

    if any(k in q for k in reception_keywords):
        return handle_reception(question, history=history)

    return handle_reception(question, history=history)
