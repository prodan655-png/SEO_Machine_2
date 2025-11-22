# SEO Analyzer (SurferSEO Clone)

**Внутрішній інструмент для аналізу та оптимізації SEO-контенту**

Аналіз конкурентів з Google SERP → Генерація рекомендацій → Live Content Score (0-100)

---

## 🚀 Основні функції

- **SERP Analysis**: Автоматичний збір топ-10 конкурентів з Google
- **Content Guidelines**: Рекомендації по довжині, заголовках, зображеннях
- **Terms Extraction**: TF-IDF + NLP для визначення важливих термінів
- **Content Scoring**: Оцінка вашого тексту (0-100 балів) з детальним breakdown
- **AI Features** (Phase 6): Brief generation, content enhancement, meta tags, коучинг
- **Ukrainian UI**: Інтерфейс українською мовою

---

## 📋 Статус проєкту

**Поточна версія**: Alpha (Phase 1-2 в розробці)

### ✅ Completed
- Phase 1: Project setup, config, database models, logging
- SERP fetcher (mock + real implementation)
- Mock implementations для безкоштовної розробки

### 🚧 In Progress
- Phase 2: Content extractor, semantic analyzer, guidelines generator

### 📝 Planned
- Phases 3-6: API, Frontend, AI integration, Testing

---

## 🛠 Technology Stack

**Backend**:
- Python 3.10+
- FastAPI (async API server)
- SQLAlchemy (ORM with SQLite/PostgreSQL)
- BeautifulSoup4 (web scraping)
- scikit-learn (TF-IDF)
- spaCy (NLP for Ukrainian & English)
- Google Gemini 1.5 Pro (AI features)

**Frontend**:
- Vanilla HTML/CSS/JavaScript
- Quill.js (rich text editor)
- Modern Ukrainian UI design

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/SEO_Machine_2.git
cd SEO_Machine_2
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Download spaCy Models
```bash
# Ukrainian model
python -m spacy download uk_core_news_sm

# English model
python -m spacy download en_core_web_sm
```

### 4. Configure Environment

**For Development** (uses mocks, no API costs):
```bash
# .env.development is already configured
# No changes needed!
```

**For Production** (requires API keys):
```bash
cp .env.production .env
# Edit .env and add your real API keys:
# - SERPAPI_KEY (from serpapi.com)
# - GEMINI_API_KEY (from Google AI Studio)
```

### 5. Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

---

## 🚀 Running the Application

### Development Mode (with mocks)
```bash
cd backend
ENV=development uvicorn main:app --reload --port 8000
```

### Production Mode (with real APIs)
```bash
cd backend
ENV=production uvicorn main:app --port 8000
```

### Frontend
```bash
cd frontend
python -m http.server 8080
```

Open: http://localhost:8080

---

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Create Analysis
```bash
curl -X POST http://localhost:8000/api/analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "кето дієта",
    "language": "uk",
    "location": "Ukraine",
    "device": "desktop"
  }'
```

#### Score Draft
```bash
curl -X POST http://localhost:8000/api/analysis/{id}/score \
  -H "Content-Type: application/json" \
  -d '{
    "draft_text": "<h1>Кето дієта</h1><p>Текст статті...</p>",
    "format": "html"
  }'
```

---

## ⚙️ Configuration

### config.yaml
Adjust scoring weights, thresholds, and features:

```yaml
scoring:
  weights:
    terms: 60    # Term coverage (0-60)
    structure: 20  # Structure score (0-20)
    headings: 20   # Headings score (0-20)

semantic_analyzer:
  top_terms_limit: 80
  min_docs_used_in: 3  # Term must appear in ≥3 competitors
```

### Environment Variables
See `.env.example` for all available options.

---

## 🔒 Security

- **CORS**: Configured for localhost (dev) and your domain (prod)
- **Secrets**: Never logged; API keys redacted in logs
- **XSS Protection**: HTML sanitization with bleach
- **Rate Limiting**: Enabled in production
- **Input Validation**: Pydantic models for all requests

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific module tests
pytest backend/tests/test_serp_fetcher.py -v

# With coverage
pytest --cov=backend --cov-report=html
```

---

## 📁 Project Structure

```
SEO_Machine_2/
├── backend/
│   ├── modules/           # Core analysis modules
│   │   ├── serp_fetcher.py
│   │   ├── content_extractor.py
│   │   ├── semantic_analyzer.py
│   │   ├── guidelines_generator.py
│   │   ├── content_scorer.py
│   │   ├── ai/            # AI features
│   │   └── mocks/         # Mock implementations
│   ├── config.py          # Configuration loader
│   ├── database.py        # SQLAlchemy models
│   ├── logger.py          # Logging with secret redaction
│   ├── models.py          # Pydantic models
│   ├── main.py            # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docs/
│   ├── implementation_plan.md
│   ├── phase6_ai_integration.md
│   ├── tasks_backlog.md
│   └── decisions.md
└── .env.development       # Dev environment (mocks)
```

---

## 🤝 Contributing

Це внутрішній інструмент, але можна:
1. Створити Issue для bug reports
2. Запропонувати features через Pull Request
3. Покращити документацію

---

## 📝 License

Proprietary - Internal Tool

---

## 🆘 Troubleshooting

### Database errors
```bash
# Reset database
rm dev_seo_analyzer.db
python -c "from database import init_db; init_db()"
```

### spaCy model not found
```bash
python -m spacy download uk_core_news_sm
python -m spacy download en_core_web_sm
```

### SERP API errors (production)
- Check SERPAPI_KEY in .env
- Verify API credits at serpapi.com
- In dev mode, set `USE_MOCK_SERP=true`

---

## 📚 Documentation

- [Implementation Plan](docs/implementation_plan.md) - Full technical specification
- [AI Integration](docs/phase6_ai_integration.md) - AI features details
- [Architecture Decisions](docs/decisions.md) - Key technical choices
- [Tasks Backlog](docs/tasks_backlog.md) - Future enhancements

---

**Built with ❤️ by Yurii**
