# Швидкий запуск SEO Machine

## 🚀 Команди для запуску

### Варіант 1: Два окремих термінали

**Термінал 1 - Backend:**
```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Термінал 2 - Frontend:**
```powershell
cd frontend
python -m http.server 8080
```

---

### Варіант 2: Одна команда (PowerShell)

```powershell
# Backend в новому вікні
Start-Process cmd -ArgumentList '/k', 'cd backend && python -m uvicorn main:app --reload --port 8000'

# Frontend в новому вікні
Start-Process cmd -ArgumentList '/k', 'cd frontend && python -m http.server 8080'
```

---

## 📍 URLs після запуску

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🛑 Як зупинити

- Натисни `Ctrl+C` в кожному терміналі
- Або просто закрий вікна терміналів

---

## ⚙️ Перевірка що все працює

1. Відкрий http://localhost:8000/docs - має показати Swagger UI
2. Відкрий http://localhost:8080 - має показати frontend
3. Перевір консоль backend - не має бути помилок з API ключами

---

## 🔧 Troubleshooting

### Помилка: "Address already in use"
Порт вже зайнятий. Знайди процес:
```powershell
# Знайти процес на порту 8000
netstat -ano | findstr :8000

# Вбити процес (замість PID підстав номер процесу)
taskkill /PID <PID> /F
```

### Помилка: "GEMINI_API_KEY not found"
Перевір що `.env.development` містить правильні ключі:
```powershell
cat .env.development
```

### Помилка: "No module named 'uvicorn'"
Встанови залежності:
```powershell
cd backend
pip install -r requirements.txt
```
