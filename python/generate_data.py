"""
TechBozor uchun realistik (sintetik) ma'lumot generatsiyasi.
Bu skript keyingi tahlil (EDA, forecasting, segmentatsiya) uchun
haqiqiy bozor xatti-harakatiga o'xshash ma'lumot yaratadi:
- Kunlar davomida o'sish trendi + bayram mavsumiyligi
- Ba'zi "sodiq" mijozlar tez-tez xarid qiladi (RFM tahlili uchun)
- Kategoriyalar bo'yicha turlicha talab
"""
import random
import datetime
import psycopg2
from faker import Faker

random.seed(42)
fake = Faker()

conn = psycopg2.connect(host="localhost", dbname="techbozor", user="postgres", password="1234")
cur = conn.cursor()

# ---------- 1. CATEGORIES ----------
categories = ["Smartfonlar", "Noutbuklar", "Aksessuarlar", "Audio texnika", "Planshetlar"]
cur.execute("TRUNCATE order_items, orders, products, categories, customers RESTART IDENTITY CASCADE;")
for c in categories:
    cur.execute("INSERT INTO categories (category_name) VALUES (%s)", (c,))
conn.commit()

cur.execute("SELECT category_id, category_name FROM categories")
cat_map = {name: cid for cid, name in cur.fetchall()}

# ---------- 2. PRODUCTS ----------
products_data = [
    # (name, category, price)
    ("iPhone 13", "Smartfonlar", 799.00), ("iPhone 15", "Smartfonlar", 999.00),
    ("Samsung Galaxy S23", "Smartfonlar", 749.00), ("Samsung Galaxy A54", "Smartfonlar", 349.00),
    ("Xiaomi Redmi Note 12", "Smartfonlar", 219.00), ("Xiaomi Poco X5", "Smartfonlar", 259.00),
    ("Realme 11", "Smartfonlar", 279.00), ("OnePlus Nord 3", "Smartfonlar", 399.00),
    ("MacBook Air M2", "Noutbuklar", 1099.00), ("MacBook Pro 14", "Noutbuklar", 1999.00),
    ("Dell XPS 13", "Noutbuklar", 1199.00), ("HP Pavilion 15", "Noutbuklar", 649.00),
    ("Lenovo ThinkPad E14", "Noutbuklar", 799.00), ("Asus Vivobook 15", "Noutbuklar", 549.00),
    ("Acer Aspire 5", "Noutbuklar", 499.00),
    ("AirPods Pro 2", "Aksessuarlar", 249.00), ("Samsung Galaxy Buds2", "Aksessuarlar", 129.00),
    ("Anker Power Bank 20000mAh", "Aksessuarlar", 39.00), ("USB-C Kabel", "Aksessuarlar", 9.00),
    ("Wireless Mouse Logitech", "Aksessuarlar", 25.00), ("Mexanik Klaviatura", "Aksessuarlar", 65.00),
    ("Telefon G'ilofi", "Aksessuarlar", 12.00), ("Quvvatlash Kabeli 65W", "Aksessuarlar", 22.00),
    ("JBL Flip 6", "Audio texnika", 129.00), ("Sony WH-1000XM5", "Audio texnika", 349.00),
    ("Marshall Emberton", "Audio texnika", 149.00), ("Bose SoundLink", "Audio texnika", 199.00),
    ("iPad 10", "Planshetlar", 449.00), ("iPad Air", "Planshetlar", 599.00),
    ("Samsung Galaxy Tab S9", "Planshetlar", 699.00), ("Xiaomi Pad 6", "Planshetlar", 349.00),
]

product_ids = {}
for i, (name, cat, price) in enumerate(products_data, start=1):
    sku = f"SKU-{1000+i}"
    stock = random.randint(5, 200)
    cur.execute(
        "INSERT INTO products (sku, product_name, category_id, price, stock) VALUES (%s,%s,%s,%s,%s) RETURNING product_id",
        (sku, name, cat_map[cat], price, stock)
    )
    product_ids[name] = (cur.fetchone()[0], price)
conn.commit()

# ---------- 3. CUSTOMERS ----------
cities = ["Toshkent", "Samarqand", "Andijon", "Buxoro", "Namangan", "Farg'ona", "Nukus", "Qarshi"]
NUM_CUSTOMERS = 180
customer_ids = []
start_reg = datetime.date(2024, 1, 1)
for _ in range(NUM_CUSTOMERS):
    name = fake.name()
    email = fake.unique.email()
    city = random.choice(cities)
    reg_date = start_reg + datetime.timedelta(days=random.randint(0, 500))
    cur.execute(
        "INSERT INTO customers (full_name, email, city, registered_at) VALUES (%s,%s,%s,%s) RETURNING customer_id",
        (name, email, city, reg_date)
    )
    customer_ids.append(cur.fetchone()[0])
conn.commit()

# Ba'zi mijozlarni "sodiq" (loyal) qilib belgilaymiz - ular ko'proq xarid qiladi
loyal_customers = random.sample(customer_ids, 25)
one_time_customers = random.sample([c for c in customer_ids if c not in loyal_customers], 40)

# ---------- 4. ORDERS + ORDER_ITEMS ----------
# 14 oylik davr: 2024-01-01 dan 2025-02-28 gacha, bayram mavsumiyligi bilan
product_list = list(product_ids.items())

def seasonal_weight(d: datetime.date) -> float:
    """Noyabr-Dekabr (chegirma mavsumi) va yoz oxiri (yangi o'quv yili) da talab oshadi."""
    w = 1.0
    if d.month in (11, 12):
        w *= 1.8
    if d.month in (8, 9):
        w *= 1.3
    if d.month == 1:
        w *= 0.7  # yangi yildan keyin pasayish
    return w

order_count = 0
current = datetime.date(2024, 1, 1)
end = datetime.date(2025, 2, 28)

while current <= end:
    base_orders_today = 1.3 * seasonal_weight(current)
    # trend: vaqt o'tishi bilan sekin o'sish
    days_passed = (current - datetime.date(2024,1,1)).days
    trend_factor = 1 + (days_passed / 365) * 0.4
    n_orders = max(0, int(random.gauss(base_orders_today * trend_factor, 1.0)))

    for _ in range(n_orders):
        # 40% ehtimol bilan sodiq mijoz, aks holda tasodifiy
        if random.random() < 0.45:
            cust = random.choice(loyal_customers)
        else:
            cust = random.choice(customer_ids)

        status = random.choices(["completed", "pending", "cancelled"], weights=[0.85, 0.08, 0.07])[0]
        cur.execute(
            "INSERT INTO orders (customer_id, order_date, status) VALUES (%s,%s,%s) RETURNING order_id",
            (cust, current, status)
        )
        order_id = cur.fetchone()[0]
        order_count += 1

        n_items = random.choices([1,2,3,4], weights=[0.5,0.3,0.15,0.05])[0]
        chosen_products = random.sample(product_list, k=min(n_items, len(product_list)))
        for pname, (pid, price) in chosen_products:
            qty = random.choices([1,2,3], weights=[0.7,0.2,0.1])[0]
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (order_id, product_id) DO NOTHING",
                (order_id, pid, qty, price)
            )
    current += datetime.timedelta(days=1)

conn.commit()
print(f"✅ Yaratildi: {len(categories)} kategoriya, {len(products_data)} mahsulot, "
      f"{NUM_CUSTOMERS} mijoz, {order_count} buyurtma")

cur.close()
conn.close()
