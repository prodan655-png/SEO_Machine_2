# 🚀 Як запустити та протестувати SEO Analyzer API

## 1️⃣ Запуск API Сервера

### Спосіб 1: Через uvicorn (рекомендовано)
```bash
cd /Users/yurii/Desktop/SEO_Machine_2/backend
source ../venv/bin/activate
ENV=development uvicorn main:app --reload --port 8000
```

### Спосіб 2: Через Python
```bash
cd /Users/yurii/Desktop/SEO_Machine_2/backend
source ../venv/bin/activate
python main.py
```

**Результат:** Сервер запуститься на `http://localhost:8000`

Ви побачите:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## 2️⃣ Перевірка що сервер працює

### Відкрийте в браузері:
- **Swagger документація:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

Або в терміналі (відкрийте новий термінал):
```bash
curl http://localhost:8000/health
```

Очікуваний результат:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T18:30:00.000Z"
}
```

---

## 3️⃣ Тестування Endpoints

### A. Створити новий аналіз
```bash
curl -X POST http://localhost:8000/api/analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "seo оптимізація",
    "language": "uk",
    "location": "Ukraine",
    "device": "desktop"
  }'
```

**Результат:**
```json
{
  "analysis_id": "abc-123-def-456",
  "status": "processing"
}
```

**Збережіть `analysis_id` для наступних кроків!**

---

### B. Перевірити статус аналізу

Замініть `{ANALYSIS_ID}` на ID з попереднього кроку:

```bash
curl http://localhost:8000/api/analysis/{ANALYSIS_ID}
```

**Під час обробки:**
```json
{
  "id": "abc-123-def-456",
  "keyword": "seo оптимізація",
  "status": "PROCESSING",
  ...
}
```

**Після завершення (через ~5-10 секунд):**
```json
{
  "id": "abc-123-def-456",
  "status": "COMPLETED",
  "terms": [
    {"term": "seo", "range": {"min": 5, "max": 15, "median": 10}},
    {"term": "оптимізація", "range": {"min": 3, "max": 10, "median": 6}},
    ...
  ],
  "guidelines": {
    "word_count": {"min": 800, "max": 1500, "median": 1100},
    "headings_count": {"min": 3, "max": 8, "median": 5},
    ...
  },
  "competitors": [...]
}
```

---

### C. Оцінити свій контент

```bash
curl -X POST http://localhost:8000/api/analysis/{ANALYSIS_ID}/score \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<h1>SEO Оптимізація</h1><p>Детальний гайд по seo оптимізації вашого сайту...</p>",
    "format": "html"
  }'
```

**Результат:**
```json
{
  "total_score": 75,
  "breakdown": {
    "terms": {"score": 45, "max": 60},
    "structure": {"score": 16, "max": 20},
    "headings": {"score": 14, "max": 20}
  },
  "term_details": [...],
  ...
}
```

---

### D. Вимкнути конкурента

```bash
curl -X PUT http://localhost:8000/api/analysis/{ANALYSIS_ID}/competitors \
  -H "Content-Type: application/json" \
  -d '{
    "competitor_url": "https://example.com",
    "enabled": false
  }'
```

---

## 4️⃣ Перевірка бази даних

База даних зберігається в:
```
/Users/yurii/Desktop/SEO_Machine_2/backend/dev_seo_analyzer.db
```

Відкрити через SQLite:
```bash
cd /Users/yurii/Desktop/SEO_Machine_2/backend
sqlite3 dev_seo_analyzer.db

# В SQLite консолі:
.tables                           # Показати всі таблиці
SELECT * FROM analyses;           # Показати всі аналізи
SELECT keyword, status FROM analyses;  # Показати ключові слова
.quit                             # Вийти
```

---

## 5️⃣ Перегляд логів

Логи виводяться в консоль де запущений сервер. Ви побачите:
```
2025-11-22 20:30:00 - api - INFO - Created analysis abc-123 for keyword 'seo оптимізація'
2025-11-22 20:30:01 - modules.serp_fetcher - INFO - Fetching SERP for 'seo оптимізація' (mock mode)
2025-11-22 20:30:05 - api - INFO - Analysis abc-123 completed successfully
```

---

## 6️⃣ Зупинка сервера

В терміналі де запущений сервер:
- Натисніть **Ctrl + C**

---

## 🔍 Git Команди для Перевірки

```bash
# Останні коміти
git log --oneline -5

# Що було змінено в останньому коміті
git show HEAD --stat

# Всі файли в проєкті
git ls-files | grep -E '(backend|docs)'

# Подивитися зміни в конкретному файлі
git show HEAD:backend/main.py
```

---

## ⚙️ Налаштування для Production

Коли будете готові до production:

1. Створіть `.env.production`:
```env
ENV=production
USE_MOCK_SERP=false
SERP_API_KEY=your-real-api-key
```

2. Запустіть з production конфігом:
```bash
ENV=production uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🎯 Швидкий Тест (все разом)

```bash
# Термінал 1: Запустити сервер
cd /Users/yurii/Desktop/SEO_Machine_2/backend
source ../venv/bin/activate
ENV=development uvicorn main:app --reload --port 8000

# Термінал 2: Тестувати
curl http://localhost:8000/health

# Якщо все працює - побачите:
# {"status":"healthy","timestamp":"..."}
```

✅ Готово! API працює і готове до використання!
