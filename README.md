# TechBozor — Onlayn Elektronika Do'koni: Sotuvlar Tahlili

Onlayn elektronika do'koni uchun ma'lumotlar bazasi va sotuvlar tahlili loyihasi.
PostgreSQL (relatsion ma'lumotlar), MongoDB (sharh va suhbat ma'lumotlari) va
Python (pandas, matplotlib, seaborn) yordamida qurilgan.

## 📁 Loyiha tuzilishi

```
TechBozor/
├── sql/
│   ├── 01_schema.sql              ← Ma'lumotlar bazasi sxemasi (5 jadval)
│   └── 02_analytics_queries.sql   ← SELECT, JOIN, GROUP BY, HAVING so'rovlari
├── python/
│   ├── generate_data.py           ← Sintetik ma'lumot generatsiyasi (Faker)
│   ├── data_analysis.py           ← EDA, tavsifiy statistika, vizualizatsiya
│   └── er_diagram.py              ← ER diagrammani chizadi
├── mongodb/
│   ├── seed_mongo.py              ← Mahsulot sharhlari va suhbatlar ma'lumoti
│   └── queries_mongo.py           ← find, sort, pagination, aggregate so'rovlari
└── charts/                        ← Generatsiya qilingan grafiklar (PNG)
```

## 🚀 Loyihani ishga tushirish

### 1. Ma'lumotlar bazasini yaratish
```bash
createdb techbozor
psql -U postgres -d techbozor -f sql/01_schema.sql
```

### 2. Sintetik ma'lumot generatsiya qilish
```bash
pip install faker psycopg2-binary
python python/generate_data.py
```

### 3. SQL tahlil so'rovlarini ishga tushirish
```bash
psql -U postgres -d techbozor -f sql/02_analytics_queries.sql
```

### 4. Python tahlilini bajarish (grafiklar yaratiladi)
```bash
pip install pandas matplotlib seaborn psycopg2-binary
python python/data_analysis.py
```

### 5. MongoDB qismini ishga tushirish
```bash
pip install pymongo mongomock faker
python mongodb/queries_mongo.py
```
> Eslatma: agar lokal MongoDB serveri mavjud bo'lmasa, skript avtomatik ravishda
> `mongomock` (xotiradagi simulyator) bilan ishlaydi — kod ikkalasida ham bir xil.

## 📊 Loyiha haqida qisqacha

- **180** mijoz, **30** mahsulot, **~594** buyurtma (14 oylik davr, mavsumiylik bilan)
- **300** mahsulot sharhi va **80** qo'llab-quvvatlash suhbati (MongoDB)
- SQL: JOIN, GROUP BY, HAVING, oddiy UPDATE
- Python tahlili: EDA, tavsifiy statistika (mean/median/std), oylik sotuv trendi,
  shahar va kategoriya bo'yicha sotuv, mijozlarni oddiy guruhlash

## 🛠 Texnologiyalar

`PostgreSQL` · `MongoDB` · `Python (pandas, matplotlib, seaborn)` · `SQL`

## ✍️ Muallif

Mahammadjanova Gulnoza — PDP University, Data Analytics yo'nalishi
