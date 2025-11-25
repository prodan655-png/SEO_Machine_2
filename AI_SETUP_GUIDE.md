# AI Features Setup Guide

## Проблема: AI кнопки не працюють

**Симптоми:**
- AI Writer не працює
- Auto-optimize не працює  
- SEO Coach не працює
- Generate Images вставляє заглушки

**Причина:** Відсутній GEMINI_API_KEY або AI вимкнено

---

## Рішення

### Крок 1: Отримайте Gemini API Key

1. Перейдіть на https://makersuite.google.com/app/apikey
2. Створіть новий API key
3. Скопіюйте ключ

### Крок 2: Додайте ключ у .env.development

Відкрийте файл `backend/.env.development` і додайте:

```bash
# AI Configuration
GEMINI_API_KEY=ваш_ключ_тут_AIzaSy...
AI_ENABLED=true
AI_PROVIDER=gemini
```

### Крок 3: Перезапустіть backend

```powershell
# Зупиніть backend (Ctrl+C у терміналі)
# Запустіть знову:
cd backend
python -m uvicorn main:app --reload --port 8000
```

---

## Перевірка

После перезапуску backend у логах має бути:
```
AI Enabled: True
AI Provider: gemini
```

Якщо все правильно, AI функції запрацюють!

---

## Content Score проблема

**Питання:** Чому додавання пробілу змінює score з 72 до 57?

**Відповідь:** 

Скоринг враховує:
1. **Word Count** - додавання пробілу може змінити розрахунок кількості слів
2. **Term Density** - якщо збільшується загальна кількість слів, density термінів зменшується
3. **Structure Score** - перевіряє чи word count в recommended range

**Приклад:**
- Було: 1500 слів, 10 разів "SEO" = 0.67% density ✅
- Стало: 1501 слів, 10 разів "SEO" = 0.666% density ❌ (нижче мінімуму)

**Рішення:**  
Це нормально - додавайте контент цілими реченнями, а не окремими пробілами.

---

## Image Generation

**Проблема:** Generate Images вставляє заглушки

**Причина:** Imagen API потребує окремого налаштування

**Тимчасове рішення:**  
Використо вуйте placeholder images або додайте свої зображення вручну
