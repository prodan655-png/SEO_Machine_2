import os

# Delete database to force fresh schema
db_files = ['seo_machine.db', 'dev_seo_analyzer.db', 'analysis_cache.db', 'serp_cache.db']

for db_file in db_files:
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✅ Видалено {db_file}")
        except Exception as e:
            print(f"❌ Не вдалося видалити {db_file}: {e}")
    else:
        print(f"⚠️  {db_file} не знайдено")

print("\n✅ Перезапустіть backend - SQLAlchemy створить нові таблиці")
