# 🤖 AI Code Reviewer

Submit any public GitHub Pull Request URL and get an instant, AI-powered code review — issues are categorised by severity (critical / warning / suggestion), with the exact file, line number, and a suggested fix for each one.

Built with a **FastAPI** backend (Groq + Llama 3.3 70B) and a **React + TypeScript** frontend (Vite + Tailwind).

---

## ✨ Features

- Paste a GitHub PR URL and get a structured review in seconds
- Issues categorised as **critical**, **warning**, or **suggestion**
- Each issue includes file, line number, explanation, and a suggested fix
- PR validation endpoint for quick pre-checks before running a full review
- Clean, responsive UI built with React, Tailwind CSS, and Framer Motion

---

## 🧱 Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [Groq API](https://groq.com/) (Llama 3.3 70B) — AI code review
- [httpx](https://www.python-httpx.org/) — async GitHub API calls
- [Pydantic](https://docs.pydantic.dev/) — request/response models

**Frontend**
- [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/) — dev server & build tool
- [Tailwind CSS](https://tailwindcss.com/)
- [lucide-react](https://lucide.dev/) — icons
- [motion](https://motion.dev/) — animations

---

## 📁 Project Structure

```
Code-Review/
├── backend/
│   ├── main.py                # FastAPI app entrypoint
│   ├── models.py              # Pydantic request/response models
│   ├── requirements.txt
│   ├── routes/
│   │   ├── review.py          # POST /api/review
│   │   └── github.py          # GET /api/github/validate
│   ├── services/
│   │   ├── github.py          # GitHub PR fetching & diff formatting
│   │   └── groq.py            # AI review via Groq/Llama
│   └── tests/
│       └── test_review.py
├── src/
│   ├── App.tsx                # Main React app
│   ├── main.tsx
│   ├── types.ts
│   └── components/
│       ├── PRInput.tsx
│       ├── ReviewCard.tsx
│       └── SeverityBadge.tsx
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- A [Groq API key](https://console.groq.com/keys) (free tier available)
- (Optional) A [GitHub personal access token](https://github.com/settings/tokens) to raise API rate limits

### 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_token_here   # optional, raises rate limits
```

Run the API:

```bash
uvicorn main:app --reload --port 8000
```

- API base URL: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### 2. Frontend setup

From the project root:

```bash
npm install
```

Create a `.env` file in the project root if your backend isn't on the default port:

```env
VITE_API_URL=http://localhost:8000
```

Run the dev server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 🔌 API Reference

### `POST /api/review`

Submit a PR for a full AI review.

```json
{
  "pr_url": "https://github.com/owner/repo/pull/123"
}
```

Returns PR info, a list of categorised issues, a summary, and a total issue count.

### `GET /api/github/validate?pr_url=...`

Quickly checks that a PR URL is well-formed and the PR is accessible, without running a full review.

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 📄 License

No license has been specified for this project yet. Consider adding one (e.g. MIT) if you intend for others to use or contribute to it.
