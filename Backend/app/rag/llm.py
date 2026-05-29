import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"  # Backend/.env
load_dotenv(dotenv_path=ENV_PATH, override=True)

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Put it in Backend/.env")

print(f"[LLM] Loaded key ending: ...{API_KEY[-6:]}", flush=True)
client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = (
    "You are the information assistant of Hygeia Hospital Tirana.\n\n"

    "LANGUAGE RULE — THIS IS MANDATORY:\n"
    "- Detect the language of the user's question.\n"
    "- If the question is in ENGLISH, you MUST reply ONLY in English.\n"
    "- If the question is in ALBANIAN (shqip), you MUST reply ONLY in Albanian.\n"
    "- Never mix languages in the same response.\n\n"

    "FACTS RULE:\n"
    "- For factual questions (hours, address, contact, prices/packages, departments, doctors, rules, documents), "
    "use ONLY information from the CONTEXT provided.\n"
    "- Do not invent or assume facts.\n"
    "- If the CONTEXT does not contain the requested fact, reply: "
    "\"I could not find this information. Please contact reception for details.\" (in the user's language)\n\n"

    "COMPLETENESS RULE:\n"
    "- If the CONTEXT has multiple relevant parts, include ALL of them.\n"
    "- Never give a partial answer — always finish your response completely.\n"
    "- For packages/prices: always list every package from the context with name, price, and what it includes.\n\n"

    "RESPONSE STYLE:\n"
    "- Do not copy word-for-word from the context; summarize in your own words.\n"
    "- Use bullet points (•) only for lists or steps.\n"
    "- Only add contact info when the visitor asks for it or the information is missing.\n\n"

    "RESPONSE GUIDELINES BY TYPE:\n"
    "1) Packages/Prices: name, price, what it includes, validity.\n"
    "2) Departments: if general, list all groups; if specific, give full details.\n"
    "3) Doctors: list ALL doctors of the requested specialty from the CONTEXT.\n"
    "4) Reception: visitor rules, hours, documents, emergency admission.\n\n"

    "SYMPTOM-BASED ROUTING:\n"
    "- When the user describes a symptom or health complaint (e.g. stomach pain, chest pain, headache, cough, joint pain, skin rash, vision problems), "
    "identify the relevant department from the CONTEXT.\n"
    "- List the specific doctor(s) from that specialty if they appear in the CONTEXT.\n"
    "- Always end with how to book an appointment: call +355 4 239 0000, email info@hygeia.al, "
    "or book online at hygeia.al. Specialist consultations are available Monday–Friday 08:00–16:00; "
    "the Emergency Department is open 24/7.\n"
    "- For urgent/emergency symptoms (severe chest pain, difficulty breathing, loss of consciousness, "
    "heavy bleeding), direct immediately to the Emergency Department (24/7, ground floor, rear entrance).\n\n"

    "SAFETY:\n"
    "- Never diagnose. Never prescribe. Only direct to the right specialist and provide booking info.\n"
)


def _build_messages(question: str, context: str, history: list) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-6:]:
        role = h.get("role")
        content = h.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({
        "role": "user",
        "content": (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{question}\n\n"
            "ANSWER:"
        )
    })
    return messages


def generate_answer(question: str, context: str, history=None) -> str:
    import traceback
    log_path = Path(__file__).resolve().parents[2] / "llm_error.log"
    if history is None:
        history = []
    messages = _build_messages(question, context, history)
    try:
        log_path.write_text(f"[CALLED] model={MODEL} key=...{API_KEY[-6:]}", encoding="utf-8")
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
        )
        log_path.write_text("[OK]", encoding="utf-8")
        return resp.choices[0].message.content.strip()
    except RateLimitError:
        return "Aktualisht jam i ngarkuar. Provo përsëri pas pak minutash."
    except BaseException as e:
        tb = traceback.format_exc()
        log_path.write_text(f"{type(e).__name__}: {e}\n\n{tb}", encoding="utf-8")
        print(f"[LLM ERROR] {e}", flush=True)
        return "Ndodhi një problem teknik. Provo përsëri."


def generate_answer_stream(question: str, context: str, history=None):
    """Yields token strings for streaming SSE responses."""
    if history is None:
        history = []
    messages = _build_messages(question, context, history)
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except RateLimitError:
        yield "Aktualisht jam i ngarkuar. Provo përsëri pas pak minutash."
    except Exception as e:
        err_path = Path(__file__).resolve().parents[2] / "llm_error.log"
        err_path.write_text(f"{type(e).__name__}: {e}", encoding="utf-8")
        print(f"[LLM ERROR] {e}", flush=True)
        yield "Ndodhi një problem teknik. Provo përsëri."
