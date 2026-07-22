# AI-Powered Customer Complaint Management System

A full-stack web application designed for pharmaceutical Quality Assurance (QA) teams. It features a modern React frontend and a FastAPI backend, powered by an AI Copilot that automatically extracts and analyzes complaint data, assesses risk, and streamlines the QMS ledger process.

## Tech Stack

- **Frontend:** React 19, Vite, Redux Toolkit, React Router, Lucide Icons
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **AI Integration:** LangGraph, Groq (Llama 3.1 & 3.3 models)

---

## Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://www.python.org/) (v3.12 or higher)
- [PostgreSQL](https://www.postgresql.org/) (running locally or remotely)

---

## Getting Started

### 1. Database Setup
Ensure PostgreSQL is running and create a database for the application:
```sql
CREATE DATABASE complaints;
```

### 2. Backend Setup

Navigate to the backend directory and set up your Python environment:

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

**Configure `.env`:**
Open `backend/.env` and update the `DATABASE_URL` with your PostgreSQL credentials. 
*Note: You will also need a valid `GROQ_API_KEY` for the AI Copilot features to work.*

**Run Database Migrations:**
```bash
alembic upgrade head
```

### 3. Frontend Setup

Open a new terminal window, navigate to the root directory, and install the Node dependencies:

```bash
# In the project root directory
npm install
```

---

## Running the Application

You will need two terminal windows running simultaneously.

**Terminal 1 (Backend):**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
* The API will be available at `http://localhost:8000`
* Interactive API Docs (Swagger UI) at `http://localhost:8000/docs`

**Terminal 2 (Frontend):**
```bash
# In the project root directory
npm run dev
```
* The web interface will be available at `http://localhost:5173`

---

## Project Structure

```text
.
├── backend/                  # FastAPI Backend Application
│   ├── alembic/              # Database migration scripts
│   ├── app/                  # Application source code (API, Core, Models, Services)
│   ├── .env.example          # Template for backend environment variables
│   └── requirements.txt      # Python dependencies
├── src/                      # React Frontend Source Code
│   ├── api/                  # API client functions
│   ├── components/           # Reusable UI components
│   ├── pages/                # Page layouts (Dashboard, Detail, Form)
│   ├── store/                # Redux state management
│   └── styles.css            # Global stylesheet
├── .gitignore                # Git ignore rules
├── index.html                # Main HTML entry point
├── package.json              # Frontend dependencies and scripts
└── vite.config.js            # Vite configuration
```
