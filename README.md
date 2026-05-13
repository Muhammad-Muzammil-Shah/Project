# ⚡ Resume Tailor Automation Tool

AI-powered system that tailors LaTeX resumes to job descriptions with 100% ATS compliance.

---

## 🏗 Project Structure

```
resume-tailor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS
│   │   ├── api/
│   │   │   ├── upload.py        # POST /api/upload/resume
│   │   │   ├── analyze.py       # POST /api/analyze/
│   │   │   ├── generate.py      # POST /api/generate/
│   │   │   ├── compile.py       # POST /api/compile/{id}
│   │   │   └── history.py       # GET  /api/history/{user_id}
│   │   ├── nlp/
│   │   │   └── pipeline.py      # spaCy + sentence-transformers
│   │   ├── services/
│   │   │   └── latex_updater.py # AI-powered LaTeX rewriter
│   │   ├── models/
│   │   │   └── models.py        # SQLAlchemy ORM models
│   │   └── core/
│   │       └── database.py      # PostgreSQL connection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── UploadStep.jsx
│       │   ├── AnalyzeStep.jsx
│       │   ├── Dashboard.jsx
│       │   ├── ScoreRing.jsx    # also: KeywordChips, LaTeXPreview
│       │   └── History.jsx
│       ├── utils/api.js
│       └── styles/globals.css
├── latex-templates/
│   └── base_resume.tex          # ATS-ready LaTeX template
├── sample-data/
│   └── sample_jd.json           # Test job description
└── docker-compose.yml
```

---

## 🚀 Local Setup (5 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Docker)
- `pdflatex` — install via `sudo apt-get install texlive-latex-base`

### Step 1 — Clone & Configure

```bash
git clone https://github.com/yourrepo/resume-tailor
cd resume-tailor
cp .env.example .env
# Edit .env:
#   ANTHROPIC_API_KEY=your_key_here
#   DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_tailor
```

### Step 2 — Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Init database
python -c "from app.core.database import init_db; init_db()"

# Run server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Step 3 — Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
# → http://localhost:3000
```

### Step 4 — Docker (all-in-one)

```bash
export ANTHROPIC_API_KEY=your_key
docker-compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/docs
```

---

## 📡 API Reference

| Method | Endpoint                      | Description                        |
|--------|-------------------------------|------------------------------------|
| POST   | /api/upload/resume            | Upload .tex/.txt/.json resume      |
| POST   | /api/upload/jd                | Submit job description text        |
| POST   | /api/analyze/                 | Run NLP analysis + scoring         |
| GET    | /api/analyze/keywords?jd_text | Quick JD keyword extraction        |
| POST   | /api/generate/                | AI-tailor resume with Claude       |
| POST   | /api/compile/{session_id}     | Compile LaTeX → PDF                |
| GET    | /api/compile/download/{id}    | Download compiled PDF              |
| GET    | /api/history/{user_id}        | Get user's session history         |
| GET    | /api/history/session/{id}     | Get specific session details       |

---

## 🧪 Testing with Sample Data

```bash
# 1. Upload sample resume
curl -X POST http://localhost:8000/api/upload/resume \
  -F "file=@latex-templates/base_resume.tex" \
  -F "user_id=test-user"

# 2. Run analysis with sample JD
JD=$(cat sample-data/sample_jd.json | python -c "import sys,json; print(json.load(sys.stdin)['description'])")
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d "{\"resume_id\": \"RESUME_ID\", \"jd_text\": \"$JD\", \"user_id\": \"test-user\"}"

# 3. Generate tailored version
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "resume_data": {"name": "Muhammad Muzammil", "role": "Senior AI Engineer", "contact": {"email": "muzammil@example.com", "phone": "+92-300-0000000", "location": "Karachi, Pakistan"}, "skills": ["Python", "LangChain", "Azure AI", "FastAPI"], "experience_years": 3}}'

# 4. Compile PDF
curl -X POST http://localhost:8000/api/compile/SESSION_ID

# 5. Download PDF
curl -o tailored_resume.pdf http://localhost:8000/api/compile/download/SESSION_ID
```

---

## ☁️ Cloud Deployment

### Azure (Recommended — you're already in the Azure ecosystem)

```bash
# 1. Create Resource Group
az group create --name resume-tailor-rg --location eastus

# 2. Azure Container Registry
az acr create --name resumetailoracr --resource-group resume-tailor-rg --sku Basic

# 3. Build and push images
az acr build --registry resumetailoracr --image backend:latest ./backend
az acr build --registry resumetailoracr --image frontend:latest ./frontend

# 4. Deploy to Azure Container Apps
az containerapp env create \
  --name resume-tailor-env \
  --resource-group resume-tailor-rg \
  --location eastus

az containerapp create \
  --name resume-tailor-api \
  --resource-group resume-tailor-rg \
  --environment resume-tailor-env \
  --image resumetailoracr.azurecr.io/backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars ANTHROPIC_API_KEY=secretref:anthropic-key DATABASE_URL=secretref:db-url

# 5. Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group resume-tailor-rg \
  --name resume-tailor-db \
  --sku-name Standard_B1ms \
  --admin-user postgres \
  --admin-password YourSecurePassword
```

### AWS Alternative

```bash
# ECS Fargate + RDS PostgreSQL
# Use provided docker-compose.yml with:
# ecs-cli compose --file docker-compose.yml service up

# Or deploy to Elastic Beanstalk:
# eb init && eb create resume-tailor-prod
```

---

## 🤖 AI Logic Details

### NLP Pipeline
1. **spaCy** (en_core_web_sm) → Named entity recognition for tech names
2. **Regex patterns** → 50+ tech/skill patterns across 5 categories  
3. **sentence-transformers** (all-MiniLM-L6-v2) → Semantic similarity (cosine)
4. **Gap analysis** → Set difference: JD keywords minus resume keywords

### LaTeX Updater Flow
1. Parse LaTeX into named sections (`\section{}` blocks)
2. Send each section to Claude Sonnet 4 with JD context + missing keywords
3. Claude rewrites content: adds keywords naturally, strengthens action verbs, adds measurable achievements
4. Inject updated sections back into LaTeX template
5. Run `pdflatex` to compile final ATS-clean PDF

### ATS Compliance Rules
- No images, icons, or tables (plain text only)
- Standard fonts (no custom/embedded)
- Proper heading hierarchy
- Keywords in plain text (not hidden or same-color)
- `.tex → .pdf` produces searchable text (not image-based)

---

## 📊 Example Output

**Input**: Resume match score 42% for a Senior AI Engineer JD  
**Missing keywords detected**: `["Pinecone", "vector database", "fine-tuning", "Kubernetes", "semantic search"]`  
**After generation**: Match score → 78%, all 5 missing keywords naturally integrated  
**Compile time**: ~8 seconds for PDF output  

---

## 🔒 Environment Variables

| Variable           | Required | Description                            |
|--------------------|----------|----------------------------------------|
| ANTHROPIC_API_KEY  | ✅       | Claude API key from console.anthropic.com |
| DATABASE_URL       | ✅       | PostgreSQL connection string            |
| UPLOAD_DIR         | Optional | Resume upload path (default: /tmp/...)  |
| OUTPUT_DIR         | Optional | PDF output path (default: /tmp/...)     |
| VITE_API_URL       | Frontend | Backend URL (default: http://localhost:8000) |
#   P r o j e c t  
 