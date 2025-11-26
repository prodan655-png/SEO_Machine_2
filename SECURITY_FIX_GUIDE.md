# 🔐 Гайд по захисту API ключів

## ⚠️ КРИТИЧНО: Твої API ключі скомпрометовані!

GitHub виявив, що наступні API ключі були закомічені в публічний репозиторій:
- **SERPAPI_KEY**: `d807d5f307defbeaf8ad65206c2c6b6219fa2b51`
- **GEMINI_API_KEY**: `AIzaSyDAPhsg40lTE6RfHyz8JD_95VEvvxDWHz4`

Ці ключі знаходяться в історії Git (коміт `b98895d5`) і доступні публічно.

---

## 📋 Покрокова інструкція виправлення

### Крок 1: Замінити скомпрометовані ключі (ТЕРМІНОВО!)

#### 1.1 Gemini API Key
1. Перейди на https://aistudio.google.com/app/apikey
2. Видали старий ключ `AIzaSyDAPhsg40lTE6RfHyz8JD_95VEvvxDWHz4`
3. Створи новий API ключ
4. Скопіюй новий ключ

#### 1.2 SerpAPI Key
1. Перейди на https://serpapi.com/manage-api-key
2. Видали старий ключ `d807d5f307defbeaf8ad65206c2c6b6219fa2b51`
3. Створи новий API ключ
4. Скопіюй новий ключ

#### 1.3 Оновити локальний `.env` файл
```bash
# Відкрий або створи файл .env в корені проекту
# Додай нові ключі:
GEMINI_API_KEY=твій_новий_ключ_тут
SERPAPI_KEY=твій_новий_ключ_тут
```

---

### Крок 2: Очистити історію Git

> **⚠️ УВАГА**: Це змінить історію Git! Координуй з командою перед виконанням.

#### Варіант A: Використати BFG Repo-Cleaner (рекомендовано)

```bash
# 1. Встанови BFG
# Завантаж з https://rtyley.github.io/bfg-repo-cleaner/

# 2. Створи файл з секретами для видалення
echo "d807d5f307defbeaf8ad65206c2c6b6219fa2b51" > secrets.txt
echo "AIzaSyDAPhsg40lTE6RfHyz8JD_95VEvvxDWHz4" >> secrets.txt

# 3. Запусти BFG
java -jar bfg.jar --replace-text secrets.txt SEO_Machine_2

# 4. Очисти Git
cd SEO_Machine_2
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (УВАГА: координуй з командою!)
git push --force --all
```

#### Варіант B: Використати git filter-branch

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.development" \
  --prune-empty --tag-name-filter cat -- --all

git push --force --all
```

---

### Крок 3: Профілактика на майбутнє

#### 3.1 Створити `.env.example` шаблон
Файл `.env.example` вже створено в проекті - використовуй його як шаблон.

#### 3.2 Встановити pre-commit hook

```bash
# Встанови gitleaks для сканування секретів
# Windows (через Chocolatey):
choco install gitleaks

# Або завантаж з https://github.com/gitleaks/gitleaks/releases

# Створи pre-commit hook
# Файл: .git/hooks/pre-commit
```

Вміст файлу `.git/hooks/pre-commit`:
```bash
#!/bin/sh
gitleaks protect --staged --verbose
```

#### 3.3 Налаштувати GitHub Secret Scanning

1. Перейди в Settings → Security → Code security and analysis
2. Увімкни "Secret scanning"
3. Увімкни "Push protection" (блокує пуш з секретами)

---

## ✅ Перевірка безпеки

Після виконання всіх кроків перевір:

```bash
# 1. Перевір що .env не в Git
git ls-files | grep .env
# Має бути порожньо (окрім .env.example)

# 2. Перевір історію на секрети
git log -p -S "AIza" -- .
# Не має знайти нічого

# 3. Перевір що .gitignore працює
git status
# .env файли не мають відображатися
```

---

## 🎯 Чому це важливо?

1. **Фінансові втрати**: Хтось може використати твої ключі і витратити твій баланс
2. **Витік даних**: Доступ до твоїх API може розкрити конфіденційну інформацію
3. **Репутація**: Витік ключів - це серйозна проблема безпеки

---

## 📚 Додаткові ресурси

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Git Filter-Branch](https://git-scm.com/docs/git-filter-branch)
