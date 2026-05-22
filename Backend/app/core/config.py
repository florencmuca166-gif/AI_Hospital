from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # Backend/app
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
INDEX_DIR = DATA_DIR / "index"

PDF_PATHS = {
    "reception": PDF_DIR / "reception.pdf",
    "doctors": PDF_DIR / "doctors.pdf",
    "departments": PDF_DIR / "departments.pdf",
    "billing": PDF_DIR / "billing.pdf",
}

INDEX_PATHS = {
    "reception": INDEX_DIR / "reception",
    "doctors": INDEX_DIR / "doctors",
    "departments": INDEX_DIR / "departments",
    "billing": INDEX_DIR / "billing",
}
