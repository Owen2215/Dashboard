#!/Applications/miniconda3/bin/python3
"""
CUHKSZ Course App — Single Server
Run:   python3 api_server.py
Open:  http://localhost:8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import json
import os

# ── Config ──────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "database": "course_db",
    "user":     "root",
    "password": "123",
}

SHEET_TO_DEPT = {
    "ACT":  "ACT",
    "AACT": "ACT",
    "FIN":  "FIN",
    "MGT":  "MGT",
    "MKT":  "MKT",
    "MIS":  "MIS",
    "CSC":  "CSC",
    "MAT":  "MAT",
    "GE":   "GEN",
    "PED":  "GEN",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# ── App ─────────────────────────────────────────────────────────────
app = FastAPI(title="CUHKSZ Course App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── DB helpers ───────────────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def safe_json(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (json.JSONDecodeError, TypeError):
        parts = [p.strip() for p in str(value).replace(";", "\n").splitlines() if p.strip()]
        return parts or [str(value)]

# ── API routes (must be defined BEFORE static mount) ────────────────
@app.get("/api/courses")
def get_courses():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sheet_name, course_code, title, lang,
                   description, outcome, syllabus, assessment,
                   reading_material, prerequisites, co_requisites
            FROM courses
            ORDER BY sheet_name, course_code
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    courses = []
    for r in rows:
        sheet = (r["sheet_name"] or "").strip().upper()
        dept  = SHEET_TO_DEPT.get(sheet, sheet or "OTHER")
        courses.append({
            "code":             (r["course_code"] or "").strip(),
            "title":            (r["title"] or "").strip(),
            "dept":             dept,
            "sheet_name":       sheet,
            "lang":             (r["lang"] or "").strip(),
            "description":      (r["description"] or "").strip(),
            "outcomes":         safe_json(r["outcome"]),
            "syllabus":         (r["syllabus"] or "").strip(),
            "assessment":       (r["assessment"] or "").strip(),
            "reading_material": (r["reading_material"] or "").strip(),
            "prerequisites":    (r["prerequisites"] or "").strip(),
            "co_requisites":    (r["co_requisites"] or "").strip(),
        })

    return {"courses": courses, "total": len(courses)}


@app.get("/api/courses/{course_code:path}")
def get_course(course_code: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses WHERE course_code = %s LIMIT 1", (course_code,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not row:
        raise HTTPException(status_code=404, detail="Course not found")

    sheet = (row["sheet_name"] or "").strip().upper()
    return {
        **{k: (v or "") for k, v in row.items()},
        "dept":     SHEET_TO_DEPT.get(sheet, sheet),
        "outcomes": safe_json(row["outcome"]),
    }


@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Explicit HTML page routes ────────────────────────────────────────
NO_CACHE = {"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"}

@app.get("/")
def root():
    index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, headers=NO_CACHE)
    return RedirectResponse(url="/app", status_code=307, headers=NO_CACHE)

@app.get("/index.html")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"), headers=NO_CACHE)

@app.get("/student_interface.html")
def serve_student():
    return FileResponse(os.path.join(BASE_DIR, "student_interface.html"), headers=NO_CACHE)

@app.get("/aa_dashboard.html")
def serve_aa():
    return FileResponse(os.path.join(BASE_DIR, "aa_dashboard.html"), headers=NO_CACHE)

@app.get("/app")
def serve_react_app_root():
    index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="React app not built yet. Run: npm run frontend:build")
    return FileResponse(index_file)

@app.get("/app/{path:path}")
def serve_react_app(path: str):
    index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
    candidate = os.path.join(FRONTEND_DIST_DIR, path)
    if os.path.exists(candidate) and os.path.isfile(candidate):
        return FileResponse(candidate)
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="React app not built yet. Run: npm run frontend:build")

# ── Static files (CSS, JS, assets) — mounted LAST ───────────────────
from fastapi import Request
from fastapi.responses import Response
import os as _os

@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("\n  CUHKSZ Course App")
    print("  Open: http://localhost:8080/app\n")
    uvicorn.run(app, host="0.0.0.0", port=8080)
