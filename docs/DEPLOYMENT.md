# 🚀 Deployment Guide - SEO Analyzer

## Варіанти Deployment

### 1. Railway (Рекомендовано) - Full Stack
**Безкоштовно** для невеликих проєктів

#### Підготовка
```bash
# 1. Створіть Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy models
RUN python -m spacy download uk_core_news_sm
RUN python -m spacy download en_core_web_sm

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend

# Set environment
ENV ENV=production
ENV PORT=8000

# Run application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
EOF

# 2. Створіть railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
```

#### Deploy на Railway
1. **Зареєструйтеся**: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Select repo**: `SEO_Machine_2`
4. **Add Variables**:
   ```
   ENV=production
   DATABASE_URL=postgresql://... (Railway надасть автоматично)
   USE_MOCK_SERP=true
   ALLOWED_ORIGINS=["https://your-app.railway.app"]
   ```
5. **Deploy!**

URL: `https://seo-analyzer-production.up.railway.app`

---

### 2. Vercel (Frontend) + Railway (Backend)
**Безкоштовно** з розділенням фронту і бека

#### Frontend на Vercel
```bash
# 1. Створіть vercel.json
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
EOF

# 2. Deploy
npm install -g vercel
vercel --prod
```

#### Backend на Railway
Див. варіант 1, але додайте CORS для Vercel domain:
```env
ALLOWED_ORIGINS=["https://your-app.vercel.app"]
```

---

### 3. Heroku (Класика)
**$5-7/міс** після безкоштовного періоду

```bash
# 1. Створіть Procfile
cat > Procfile << 'EOF'
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
EOF

# 2. Створіть runtime.txt
echo "python-3.11.0" > runtime.txt

# 3. Deploy
heroku create seo-analyzer-app
git push heroku main
heroku config:set ENV=production
heroku addons:create heroku-postgresql:mini
```

---

### 4. DigitalOcean App Platform
**$5/міс** за найпростіший droplet

```yaml
# app.yaml
name: seo-analyzer
services:
  - name: web
    github:
      repo: prodan655-png/SEO_Machine_2
      branch: main
    build_command: pip install -r backend/requirements.txt
    run_command: cd backend && uvicorn main:app --host 0.0.0.0 --port 8080
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: ENV
        value: production
      - key: DATABASE_URL
        type: SECRET
databases:
  - name: db
    engine: PG
    version: "14"
```

---

## Production Configuration

### Environment Variables
```env
# .env.production
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database (автоматично від хостингу)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# SERP (опціонально - використовуйте mock в початку)
USE_MOCK_SERP=true
# SERPAPI_KEY=your_key_here

# AI (опціонально)
AI_ENABLED=false
# GEMINI_API_KEY=your_key_here

# Security
ALLOWED_ORIGINS=["https://your-domain.com"]
SECRET_KEY=your-secret-key-here
RATE_LIMIT_ENABLED=true
```

### Database Migration
```bash
# При першому deploy
python -c "from backend.database import init_db; init_db()"

# Або через Railway CLI
railway run python -c "from backend.database import init_db; init_db()"
```

---

## Testing Before Deploy

### Local Production Test
```bash
# 1. Build Docker image
docker build -t seo-analyzer .

# 2. Run container
docker run -p 8000:8000 \
  -e ENV=production \
  -e DATABASE_URL=sqlite:///./prod_test.db \
  seo-analyzer

# 3. Test
curl http://localhost:8000/health
```

### Load Testing
```bash
# Install k6
brew install k6  # macOS
# або завантажте з k6.io

# Run load test
k6 run - << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function() {
  let res = http.get('http://localhost:8000/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
EOF
```

---

## Monitoring

### Railway Logs
```bash
railway logs
```

### Vercel Logs
```bash
vercel logs
```

### Error Tracking (Optional)
Додайте Sentry для production:
```bash
pip install sentry-sdk
```

```python
# backend/main.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## Custom Domain

### Railway
1. **Settings** → **Domains**
2. **Add Custom Domain**: `seo-analyzer.yourdomain.com`
3. **Add DNS Record**:
   ```
   Type: CNAME
   Name: seo-analyzer
   Value: your-app.railway.app
   ```

### Vercel
1. **Settings** → **Domains**
2. **Add Domain**: `yourdomain.com`
3. **Follow DNS instructions**

---

## SSL/HTTPS
**Автоматично** на всіх платформах:
- ✅ Railway
- ✅ Vercel
- ✅ Heroku
- ✅ DigitalOcean

---

## Costs Estimate

| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Railway** | 500 годин/міс | $5-10/міс |
| **Vercel** | Unlimited frontend | $20/міс (для команд) |
| **Heroku** | Немає безкоштовного | $7/міс |
| **DigitalOcean** | $200 credit | $5/міс |

**Рекомендація**: Railway (free tier) для початку

---

## Troubleshooting

### Port Issues
```python
# main.py - використовуйте змінну PORT
import os
port = int(os.getenv("PORT", 8000))
uvicorn.run("main:app", host="0.0.0.0", port=port)
```

### Database Connection
```bash
# Перевірте DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); print(engine.connect())"
```

### Memory Issues
Збільшіть instance size або додайте swap:
```dockerfile
# Dockerfile - оптимізація
RUN pip install --no-cache-dir -r requirements.txt
```

---

## Backup Strategy

### Database Backup
```bash
# Railway
railway run pg_dump $DATABASE_URL > backup.sql

# Heroku
heroku pg:backups:capture
heroku pg:backups:download
```

### Code Backup
GitHub вже є вашим backup! 🎉

---

**Готово!** Ваш SEO Analyzer буде доступний 24/7 🚀
