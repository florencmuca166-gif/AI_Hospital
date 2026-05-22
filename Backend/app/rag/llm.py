import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"  # Backend/.env
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Put it in Backend/.env")

# Gemini exposes an OpenAI-compatible endpoint — no extra library needed
client = OpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT = (
    "Ti je asistenti informues i Spitalit Hygeia Tiranë.\n"
    "Detyra jote: përgjigju qartë dhe natyrshëm në shqip ose anglisht, "
    "sipas gjuhës që përdor vizitori.\n\n"

    "RREGULLI KRYESOR (FAKTET):\n"
    "- Për pyetje me FAKTE (orare, adresa, kontakt, çmime/paketa, departamente, mjekë, rregulla, dokumente), "
    "përdor VETËM informacionin te KONTEKSTI.\n"
    "- Mos shpik dhe mos supozo.\n"
    "- Nëse KONTEKSTI nuk e ka faktin e kërkuar, përgjigju: "
    "\"Nuk e gjej këtë informacion. Kontaktoni recepsionin për detaje.\"\n\n"

    "Bisedë natyrshme (JO-FAKTE):\n"
    "- Nëse përdoruesi thotë përshëndetje/faleminderit/ok/mirupafshim ose hello/thanks/bye, "
    "përgjigju shkurt e miqësisht në gjuhën e tyre.\n"
    "- Mos jep këshilla mjekësore ose diagnozë.\n\n"

    "STILI I PËRGJIGJES:\n"
    "- Mos kopjo fjalë për fjalë nga konteksti; përmbledh me fjalët e tua.\n"
    "- Përgjigju zakonisht 2–6 rreshta (më gjatë vetëm kur pyetja kërkon detaje).\n"
    "- Përdor pika (•) vetëm për lista/hapa.\n"
    "- Mos shto 'Kontakt...' në çdo përgjigje; vendose vetëm kur vizitori pyet ose informacioni mungon.\n\n"

    "RREGULLI I PLOTËSISË:\n"
    "- Nëse KONTEKSTI ka disa pjesë relevante, përfshiji të gjitha.\n"
    "- Mos jep përgjigje të pjesshme.\n\n"

    "UDHËZIME SIPAS LLOJIT:\n"
    "1) Paketa/Çmime: emri, çmimi, çfarë përfshin, vlefshmëria.\n"
    "2) Departamente: nëse e përgjithshme, listo grupet; nëse specifike, detaje të plota.\n"
    "3) Mjekë: të gjithë mjekët e specialitetit nga KONTEKSTI.\n"
    "4) Recepsion: rregulla vizitorësh, orare, dokumente, pranim urgjence.\n\n"

    "SIGURIA:\n"
    "- Kur ka simptoma ose urgjencë, mos diagnostiko; sugjero urgjencën ose spitalin.\n"
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
            f"KONTEKSTI:\n{context}\n\n"
            f"PYETJA:\n{question}\n\n"
            "PËRGJIGJJA:"
        )
    })
    return messages


def generate_answer(question: str, context: str, history=None) -> str:
    if history is None:
        history = []
    messages = _build_messages(question, context, history)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()
    except RateLimitError:
        return "Aktualisht jam i ngarkuar. Provo përsëri pas pak minutash."
    except Exception:
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
            max_tokens=350,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except RateLimitError:
        yield "Aktualisht jam i ngarkuar. Provo përsëri pas pak minutash."
    except Exception:
        yield "Ndodhi një problem teknik. Provo përsëri."
