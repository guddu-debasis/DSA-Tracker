# DSA Tracker

Full-stack app to track solved/unsolved LeetCode-pattern questions.
Backend: FastAPI + MongoDB (Beanie/Motor) + JWT auth.
Frontend: React (Vite) + React Router.

## 1. MongoDB
Make sure MongoDB is running locally (default `mongodb://localhost:27017`),
or update `MONGO_URI` in `backend/.env` to point at Atlas / another instance.

## 2. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then edit if needed
```

### Seed the questions
Place the PDF at `backend/data/Dsa_important_patterns.pdf` (the pattern list
you already have), then run:
```bash
python seed.py
```
This parses the PDF, splits it into categories/questions, and inserts them
into the `questions` collection. It's safe to re-run — it'll ask before
clearing existing questions. Generated LeetCode URLs are best-effort slugs;
double check a few and fix any mismatches directly in MongoDB if needed.

### Run the API
```bash
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

## 3. Frontend setup
```bash
cd frontend
npm install
copy .env.example .env         # points VITE_API_URL at http://localhost:8000
npm run dev
```
App: http://localhost:5173

## How it works
- Sign up / log in → JWT stored in localStorage, attached to every API call.
- `/questions` returns all questions grouped by category, joined with the
  logged-in user's progress.
- Ticking a checkbox calls `PUT /progress/{question_id}` which upserts a
  `Progress` document (`user_id`, `question_id`, `solved`) — so each user's
  progress is independent even though the question bank is shared.

## Next ideas (not built yet)
- Password reset / email verification
- Per-category progress charts on the dashboard
- Search/filter by question title
- Admin endpoint to add/edit questions without re-seeding
