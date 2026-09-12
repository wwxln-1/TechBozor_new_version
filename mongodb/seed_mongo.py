"""
TechBozor — MongoDB qismi.
Nega MongoDB? Mahsulot sharhlari va mijozlar bilan yozishmalar
tuzilishi har xil (ba'zi sharhda rasm bor, ba'zisida yo'q; xabarlar
soni har bir suhbatda farq qiladi) — bu klassik semi-structured/
unstructured holat, va relatsion jadvalga qulay sig'maydi.

Bu skript avval haqiqiy MongoDB serverga ulanishga urinadi,
topilmasa "mongomock" (xotiradagi simulyator) bilan ishlaydi —
kod ikkalasida ham bir xil ishlaydi.
"""
import random
import datetime
from faker import Faker

fake = Faker()
random.seed(7)

def get_client():
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
        client.server_info()  # ulanishni tekshirish
        print("✅ Haqiqiy MongoDB serverga ulandi")
        return client
    except Exception:
        import mongomock
        print("ℹ️  Haqiqiy MongoDB topilmadi — mongomock (simulyator) bilan ishlaymiz")
        return mongomock.MongoClient()

PRODUCTS = [
    "iPhone 13", "iPhone 15", "Samsung Galaxy S23", "Xiaomi Redmi Note 12",
    "MacBook Air M2", "Dell XPS 13", "AirPods Pro 2", "JBL Flip 6",
    "iPad 10", "Sony WH-1000XM5"
]
TAGS_POOL = ["batareya", "narx", "sifat", "yetkazib_berish", "dizayn", "kamera"]
TOPICS = ["yetkazib berish kechikdi", "mahsulot nosoz keldi", "narx haqida savol",
          "qaytarish haqida", "kafolat muddati", "buyurtmani bekor qilish"]


def seed(db):
    """Berilgan db ob'ektiga sinov ma'lumotlarini yozadi (idempotent: avval tozalaydi)."""
    db.product_reviews.drop()
    db.support_chats.drop()

    # ---------- 1. product_reviews (semi-structured) ----------
    reviews = []
    for i in range(300):
        product = random.choice(PRODUCTS)
        rating = random.choices([5, 4, 3, 2, 1], weights=[0.40, 0.30, 0.15, 0.10, 0.05])[0]
        doc = {
            "review_id": i + 1,
            "product_name": product,
            "customer_name": fake.name(),
            "rating": rating,
            "comment": fake.sentence(nb_words=12),
            "tags": random.sample(TAGS_POOL, k=random.randint(1, 3)),
            "created_at": fake.date_time_between(start_date="-14mo", end_date="now"),
            "verified_purchase": random.choice([True, True, True, False]),
        }
        # Ba'zi sharhlarda rasm bo'ladi, ba'zisida yo'q — semi-structured xususiyat
        if random.random() < 0.3:
            doc["images"] = [f"https://cdn.techbozor.uz/reviews/{i}_{j}.jpg" for j in range(random.randint(1, 3))]
        reviews.append(doc)
    db.product_reviews.insert_many(reviews)

    # ---------- 2. support_chats (unstructured-ish: xabarlar massivi) ----------
    chats = []
    for i in range(80):
        n_messages = random.randint(2, 8)
        messages = []
        t0 = fake.date_time_between(start_date="-6mo", end_date="now")
        for m in range(n_messages):
            sender = "customer" if m % 2 == 0 else "support_agent"
            messages.append({
                "sender": sender,
                "text": fake.sentence(nb_words=10),
                "timestamp": t0 + datetime.timedelta(minutes=5 * m)
            })
        chats.append({
            "chat_id": i + 1,
            "customer_name": fake.name(),
            "topic": random.choice(TOPICS),
            "resolved": random.choice([True, True, False]),
            "messages": messages,
        })
    db.support_chats.insert_many(chats)

    print(f"✅ MongoDB: {db.product_reviews.count_documents({})} ta sharh, "
          f"{db.support_chats.count_documents({})} ta suhbat yozuvi qo'shildi")


if __name__ == "__main__":
    _client = get_client()
    seed(_client["techbozor"])
