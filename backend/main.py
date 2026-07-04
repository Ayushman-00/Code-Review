from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import review, github

load_dotenv()   # load .env variables before anything else runs

# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Code Reviewer",
    description=(
        "Submit any public GitHub PR URL and receive a structured, AI-powered "
        "code review categorised by severity — powered by Groq + Llama 3."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI  →  http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc UI    →  http://localhost:8000/redoc
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Update ALLOWED_ORIGINS when you deploy the frontend to Vercel

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://laughing-winner-5g6qp9rp9vw4hv9-3000.app.github.dev",  # ← 3000 not 5173
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # ← simplest fix for dev
    allow_credentials=False,   # ← must be False with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(review.router, prefix="/api", tags=["Review"])
app.include_router(github.router, prefix="/api", tags=["GitHub"])

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "message": "AI Code Reviewer API is running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}