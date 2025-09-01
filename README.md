# Personal Finance Assistant

The **Personal Finance Assistant** is a full-stack application with a **FastAPI backend** and a **React (Vite) frontend**.  
It helps track income and expenses, extract text from receipts using **OCR**, and display visual summaries.

OCR uses **pytesseract**, which requires the **native Tesseract binary** to be installed and available on `PATH` for image/PDF text extraction.

---

## 📦 Prerequisites

- **Backend**:  
  - Python **3.11+**  
  - `pip` and a virtual environment  
  - [Uvicorn](https://www.uvicorn.org/) to run the FastAPI server  

- **OCR**:  
  - The **Tesseract OCR engine** must be installed system-wide.  
  - `pytesseract` alone is not enough.  

---

## ⚙️ Backend Setup

From the `backend` directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

The entry point is src/main.py, which exposes app.

Uvicorn runs it using module:app syntax.

The server reloads automatically in development mode.

🗄 Database Setup (PostgreSQL)

Install PostgreSQL and create a database:

createdb finance_app


Create a .env file in backend/ with the following:

DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/finance_app


Apply database migrations using Alembic:

alembic upgrade head


Keep Alembic migrations under version control for reproducible deployments.

🎨 Frontend Setup

Run the frontend with Vite’s dev server. It should be configured to call the backend API at http://localhost:8000 during development.

cd frontend
npm install
npm run dev


Runs on default Vite port (e.g., 5173)

Ensure CORS is enabled on the backend for the dev origin

🔠 Tesseract Installation
Ubuntu/Debian
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-eng
tesseract --version

macOS
brew install tesseract
tesseract --version

Windows

Install Tesseract OCR for Windows
.

Ensure C:\Program Files\Tesseract-OCR is added to PATH.

Or configure in code:

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

Docker

For images based on Debian/Ubuntu:

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng && rm -rf /var/lib/apt/lists/*

🚀 Running the Stack

Run backend and frontend in separate terminals:

Backend: http://localhost:8000

Frontend: http://localhost:5173

Check FastAPI’s interactive docs at:
👉 http://localhost:8000/docs

🔑 Environment Variables

Create backend/.env with at least:

DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/finance_app

# Optional examples if used by the app:
# SECRET_KEY=change-me
# CORS_ORIGINS=http://localhost:5173


Keep .env out of version control

Use environment-specific .env files for local/dev/prod