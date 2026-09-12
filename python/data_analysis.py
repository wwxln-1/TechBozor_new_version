"""
TechBozor — Data Analytics qismi (JUNIOR versiya).

Bu versiyada faqat Junior Data Analyst darajasiga mos ishlar bor:
- Ma'lumotni yuklash va umumiy ko'rinish (EDA)
- Tavsifiy statistika (mean, median, std)
- Oddiy pandas groupby tahlillari
- Oddiy grafiklar (matplotlib / seaborn)

Advanced qism (Confidence Interval, Hypothesis Testing, Forecasting,
RFM segmentatsiya, Logistic Regression) OLIB TASHLANDI — bular Middle/
Senior daraja uchun mavzular, Junior portfolioda shart emas.
"""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2

sns.set_theme(style="whitegrid")
import os
CHARTS = os.path.join(os.path.dirname(__file__), "..", "charts")

conn = psycopg2.connect(host="localhost", dbname="techbozor", user="postgres", password="1234")

# ============================================================
# 1. MA'LUMOTNI YUKLASH
# ============================================================
orders_df = pd.read_sql("""
    SELECT o.order_id, o.customer_id, o.order_date, o.status,
           c.city,
           SUM(oi.quantity * oi.unit_price) AS order_value,
           SUM(oi.quantity) AS total_items
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY o.order_id, o.customer_id, o.order_date, o.status, c.city
""", conn)

orders_df["order_date"] = pd.to_datetime(orders_df["order_date"])

print("=" * 60)
print("1. EDA — Ma'lumotning umumiy ko'rinishi")
print("=" * 60)
print(orders_df.info())
print("\nBo'sh (missing) qiymatlar:\n", orders_df.isnull().sum())
print("\nBirinchi 5 qator:\n", orders_df.head())


# ============================================================
# 2. TAVSIFIY STATISTIKA (Descriptive Statistics)
# ============================================================
print("\n" + "=" * 60)
print("2. Tavsifiy statistika — order_value (buyurtma qiymati)")
print("=" * 60)
ov = orders_df["order_value"]
print(f"Mean (o'rtacha)   = {ov.mean():.2f}")
print(f"Median (mediana)  = {ov.median():.2f}")
print(f"Std (standart og'ish) = {ov.std():.2f}")
print(f"Min / Max         = {ov.min():.2f} / {ov.max():.2f}")
print("\nTo'liq statistika (describe):\n", ov.describe().round(2))


# ============================================================
# 3. OYLIK SOTUV TRENDI
# ============================================================
monthly = orders_df.groupby(orders_df["order_date"].dt.to_period("M"))["order_value"].sum()
monthly.index = monthly.index.to_timestamp()

print("\n" + "=" * 60)
print("3. Oylik sotuv")
print("=" * 60)
print(monthly.round(0))

plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("TechBozor — Oylik sotuv trendi")
plt.xlabel("Oy")
plt.ylabel("Sotuv ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHARTS}/01_monthly_trend.png", dpi=130)
plt.close()


# ============================================================
# 4. SHAHARLAR BO'YICHA SOTUV
# ============================================================
by_city = orders_df.groupby("city")["order_value"].sum().sort_values(ascending=False)

print("\n" + "=" * 60)
print("4. Shaharlar bo'yicha jami sotuv")
print("=" * 60)
print(by_city.round(0))

plt.figure(figsize=(8, 5))
by_city.plot(kind="bar", color="#4C72B0")
plt.title("Shaharlar bo'yicha jami sotuv")
plt.ylabel("Sotuv ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHARTS}/02_sales_by_city.png", dpi=130)
plt.close()


# ============================================================
# 5. MIJOZLARNI ODDIY GURUHLASH — "bir martalik" vs "qayta kelgan"
#    (RFM/ML o'rniga oddiy value_counts asosida)
# ============================================================
orders_per_customer = orders_df.groupby("customer_id")["order_id"].nunique()
customer_type = orders_per_customer.apply(
    lambda n: "Bir martalik mijoz" if n == 1 else "Qayta xarid qilgan mijoz"
)

print("\n" + "=" * 60)
print("5. Mijozlar guruhlari")
print("=" * 60)
print(customer_type.value_counts())

plt.figure(figsize=(6, 5))
customer_type.value_counts().plot(kind="bar", color=["#55A868", "#DD8452"])
plt.title("Mijozlar: bir martalik vs qayta xarid qilgan")
plt.ylabel("Mijozlar soni")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{CHARTS}/03_customer_types.png", dpi=130)
plt.close()


# ============================================================
# 6. KATEGORIYA BO'YICHA SOTUV
# ============================================================
cat_df = pd.read_sql("""
    SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS revenue
    FROM categories c
    JOIN products p ON p.category_id = c.category_id
    JOIN order_items oi ON oi.product_id = p.product_id
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY c.category_name
    ORDER BY revenue DESC
""", conn)

print("\n" + "=" * 60)
print("6. Kategoriya bo'yicha jami sotuv")
print("=" * 60)
print(cat_df)

plt.figure(figsize=(8, 5))
sns.barplot(data=cat_df, x="revenue", y="category_name", color="#4C72B0")
plt.title("Kategoriya bo'yicha jami sotuv")
plt.xlabel("Sotuv ($)")
plt.ylabel("")
plt.tight_layout()
plt.savefig(f"{CHARTS}/04_category_revenue.png", dpi=130)
plt.close()

print("\n✅ Barcha grafiklar saqlandi:", CHARTS)
conn.close()
