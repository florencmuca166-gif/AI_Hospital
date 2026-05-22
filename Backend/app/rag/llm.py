import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"  # Backend/.env
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Put it in Backend/.env")

client = OpenAI(api_key=API_KEY)

def generate_answer(question: str, context: str, history=None) -> str:
    if history is None:
        history = []

    messages = [
        {
            "role": "system",
            "content": (
                "Ti je asistenti informues i Spitalit Hygeia Tiranë.\n"
                "Detyra jote: përgjigju qartë dhe natyrshëm në shqip.\n\n"

                "RREGULLI KRYESOR (FAKTET):\n"
                "- Për pyetje me FAKTE (orare, adresa, kontakt, çmime/paketa, departamente, mjekë, rregulla, dokumente), "
                "përdor VETËM informacionin te KONTEKSTI.\n"
                "- Mos shpik dhe mos supozo.\n"
                "- Nëse KONTEKSTI nuk e ka faktin e kërkuar, përgjigju vetëm: \"Nuk e gjej këtë informacion në dokumentet e mia.\"\n\n"

                "Bisedë natyrshme (JO-FAKTE):\n"
                "- Nëse përdoruesi thotë përshëndetje/faleminderit/ok/mirupafshim, përgjigju shkurt e miqësisht.\n"
                "- Nëse përdoruesi është i shqetësuar, i hutuar ose kërkon sqarim, jep një përgjigje qetësuese dhe sugjero hapin tjetër.\n"
                "- Për këto raste nuk kërkohet domosdoshmërisht që KONTEKSTI të ketë informacion.\n"
                "- Mos jep këshilla mjekësore ose diagnozë.\n\n"

                "STILI I PËRGJIGJES:\n"
                "- Mos kopjo fjalë për fjalë nga konteksti; përmbledh me fjalët e tua.\n"
                "- Përgjigju zakonisht 2–6 rreshta (më gjatë vetëm kur pyetja kërkon detaje).\n"
                "- Përdor pika (•) vetëm për lista/hapa.\n"
                "- Mos shto \"Kontakt...\" në çdo përgjigje. Vendose vetëm kur:\n"
                "  (a) përdoruesi pyet për kontakt/rezervim, ose\n"
                "  (b) informacioni mungon dhe duhet ta drejtojmë te burimi zyrtar.\n\n"

                "RREGULLI I PLOTËSISË (shumë i rëndësishëm):\n"
                "- Nëse KONTEKSTI ka më shumë se një pjesë të rëndësishme për pyetjen, përfshiji të gjitha në përgjigje.\n"
                "- Mos jep përgjigje të pjesshme kur KONTEKSTI përmban detaje.\n\n"

                "UDHËZIME SIPAS LLOJIT TË PYETJES:\n"
                "1) Paketa/Çmime/Shërbime:\n"
                "- Jep: emrin, çmimin (nëse ka), çfarë përfshin (pikat kryesore), dhe çdo kusht/vlefshmëri nëse ekziston.\n"
                "- Nëse ka disa paketa të ngjashme në KONTEKST, përmendi të gjitha shkurt.\n\n"

                "2) Departamente:\n"
                "- Nëse pyetja është e përgjithshme (p.sh. \"Cilat departamente ofron?\"), "
                "dhe KONTEKSTI ka grupime funksionale, përgjigju të organizuara sipas grupeve.\n"
                "- Nëse pyetja është për një departament specifik, përmblidh të gjitha detajet që KONTEKSTI ka për atë departament.\n\n"

                "3) Mjekë:\n"
                "- Nëse pyetja lidhet me një specialitet, jep të gjithë mjekët e atij specialiteti që gjenden në KONTEKST.\n"
                "- Nëse pyetja është \"a keni\" / \"cilët janë\", jep listë emrash + specialitet.\n\n"

                "4) Recepsion (rregulla/pranim/vizita/dokumente):\n"
                "- Kur pyetja është për rregulla vizitorësh, orare vizitash, dokumente për shtrim, pranim urgjence, dalje nga spitali, "
                "përfshi të gjitha pikat relevante që gjenden në KONTEKST.\n\n"

                "SIGURIA:\n"
                "- Nëse pyetja ka simptoma ose urgjencë, mos diagnostiko; sugjero të kontaktojnë urgjencën ose spitalin.\n"
            )

        }
    ]


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
            "PËRGJIGJJA (shkurt, e qartë, në shqip):"
        )
    })

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
