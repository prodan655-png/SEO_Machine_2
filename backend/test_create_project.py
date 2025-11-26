"""
Тестовий скрипт для створення проекту через API.
"""
import requests
import json

# 1. Створити проект "Flakes"
print("📦 Створюємо проект 'Flakes'...")
response = requests.post(
    "http://127.0.0.1:8000/api/projects",
    json={
        "name": "Flakes",
        "description": "Flakes - це бренд неактивних дріжджів для випічки. Продукт використовується пекарями та домашніми кондитерами для приготування хліба, булочок та іншої випічки.",
        "target_audience": "Пекарі, кондитери, домашні кухарі",
        "tone_of_voice": "Професійний, експертний"
    }
)

if response.status_code == 201:
    project = response.json()
    project_id = project['id']
    print(f"✅ Проект створено!")
    print(f"   ID: {project_id}")
    print(f"   Назва: {project['name']}")
    print(f"\n📋 Збережіть цей ID для створення аналізів:")
    print(f"   project_id = '{project_id}'")
    
    # Зберегти ID у файл для зручності
    with open('project_id.txt', 'w') as f:
        f.write(project_id)
    print(f"\n💾 ID збережено у файл project_id.txt")
else:
    print(f"❌ Помилка: {response.status_code}")
    print(response.text)

# 2. Показати список проектів
print("\n\n📋 Список всіх проектів:")
response = requests.get("http://127.0.0.1:8000/api/projects")
projects = response.json()
for p in projects:
    print(f"  - {p['name']} (ID: {p['id']})")
