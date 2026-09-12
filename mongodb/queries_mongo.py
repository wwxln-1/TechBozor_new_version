"""
TechBozor — MongoDB analitik so'rovlar.
find/$gt/$lt, sort, pagination, update operatorlari, aggregate pipeline.
"""
from seed_mongo import get_client, seed
import json
from bson import json_util

client = get_client()
db = client["techbozor"]
seed(db)

def show(title, cursor_or_list):
    print(f"\n--- {title} ---")
    for doc in cursor_or_list:
        doc.pop("_id", None)
        print(json.loads(json_util.dumps(doc)))

# 1) find + $gte — rating>=4 bo'lgan sharhlar, faqat 5 tasi
res = db.product_reviews.find({"rating": {"$gte": 4}}).limit(3)
show("1) Rating >= 4 bo'lgan sharhlar (birinchi 3 ta)", res)

# 2) sort + pagination (2-sahifa, page_size=5)
page, page_size = 2, 5
skip = (page - 1) * page_size
res = db.product_reviews.find().sort("rating", -1).skip(skip).limit(page_size)
show(f"2) Pagination: sahifa={page}, page_size={page_size} (skip={skip})", res)

# 3) update — verified_purchase=False bo'lgan hujjatlarni True qilib belgilash (1 tasini)
one = db.product_reviews.find_one({"verified_purchase": False})
if one:
    db.product_reviews.update_one({"_id": one["_id"]}, {"$set": {"verified_purchase": True}})
    print(f"\n--- 3) update_one bilan verified_purchase=True qilindi (review_id={one['review_id']}) ---")

# 4) $inc bilan misol — bitta review'ga "helpful_votes" maydonini oshirish (upsert bilan)
db.product_reviews.update_one(
    {"review_id": 1},
    {"$inc": {"helpful_votes": 1}},
    upsert=True
)
print("\n--- 4) $inc + upsert: review_id=1 ga helpful_votes qo'shildi ---")

# 5) aggregate: $match + $group — har mahsulot bo'yicha o'rtacha reyting va sharhlar soni
pipeline = [
    {"$match": {"verified_purchase": True}},
    {"$group": {
        "_id": "$product_name",
        "avg_rating": {"$avg": "$rating"},
        "review_count": {"$sum": 1}
    }},
    {"$sort": {"avg_rating": -1}},
    {"$limit": 5}
]
res = list(db.product_reviews.aggregate(pipeline))
print("\n--- 5) Aggregate: Top-5 mahsulot (tasdiqlangan xaridlar bo'yicha o'rtacha reyting) ---")
for r in res:
    print(f"{r['_id']:<25} avg_rating={r['avg_rating']:.2f}  review_count={r['review_count']}")

# 6) aggregate: eng ko'p uchraydigan muammo mavzulari (support_chats)
pipeline2 = [
    {"$group": {"_id": "$topic", "count": {"$sum": 1},
                "resolved_count": {"$sum": {"$cond": ["$resolved", 1, 0]}}}},
    {"$sort": {"count": -1}}
]
res2 = list(db.support_chats.aggregate(pipeline2))
print("\n--- 6) Support mavzulari bo'yicha statistika ---")
for r in res2:
    rate = 100 * r["resolved_count"] / r["count"]
    print(f"{r['_id']:<30} jami={r['count']:<4} hal qilingan={r['resolved_count']:<4} ({rate:.0f}%)")
