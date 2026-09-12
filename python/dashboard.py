"""
TechBozor — Streamlit Dashboard.
PostgreSQL (sotuvlar) va MongoDB (sharh/suhbat) ma'lumotlarini
bitta interaktiv web-panelda ko'rsatadi.

Ishga tushirish:
    streamlit run python/dashboard.py
"""
import os
import sys

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mongodb"))
from seed_mongo import get_client, seed  # noqa: E402

st.set_page_config(page_title="TechBozor Dashboard", layout="wide")


@st.cache_resource
def get_mongo_db():
    client = get_client()
    db = client["techbozor"]
    seed(db)
    return db


@st.cache_data
def load_orders():
    conn = psycopg2.connect(host="localhost", dbname="techbozor", user="postgres", password="1234")
    df = pd.read_sql(
        """
        SELECT o.order_id, o.customer_id, o.order_date, o.status,
               c.city, c.full_name,
               SUM(oi.quantity * oi.unit_price) AS order_value,
               SUM(oi.quantity) AS total_items
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY o.order_id, o.customer_id, o.order_date, o.status, c.city, c.full_name
        """,
        conn,
    )
    cat_df = pd.read_sql(
        """
        SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS revenue,
               SUM(oi.quantity) AS units_sold
        FROM categories c
        JOIN products p ON p.category_id = c.category_id
        JOIN order_items oi ON oi.product_id = p.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY c.category_name
        ORDER BY revenue DESC
        """,
        conn,
    )
    conn.close()
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df, cat_df


st.title("📊 TechBozor — Sotuvlar va Sharhlar Dashboardi")

orders_df, cat_df = load_orders()
db = get_mongo_db()

# ---------------- Sidebar filtrlar ----------------
st.sidebar.header("Filtrlar")
cities = sorted(orders_df["city"].unique())
selected_cities = st.sidebar.multiselect("Shahar", cities, default=cities)

min_d, max_d = orders_df["order_date"].min(), orders_df["order_date"].max()
date_range = st.sidebar.date_input("Sana oralig'i", (min_d, max_d), min_value=min_d, max_value=max_d)

f = orders_df[orders_df["city"].isin(selected_cities)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    f = f[(f["order_date"] >= start) & (f["order_date"] <= end)]

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jami buyurtmalar", f"{f['order_id'].nunique():,}")
c2.metric("Jami sotuv ($)", f"{f['order_value'].sum():,.0f}")
c3.metric("O'rtacha buyurtma ($)", f"{f['order_value'].mean():,.0f}" if len(f) else "0")
c4.metric("Faol mijozlar", f"{f['customer_id'].nunique():,}")

st.divider()

# ---------------- Grafiklar ----------------
col1, col2 = st.columns(2)

with col1:
    monthly = f.groupby(f["order_date"].dt.to_period("M"))["order_value"].sum()
    monthly.index = monthly.index.to_timestamp()
    fig = px.line(x=monthly.index, y=monthly.values, markers=True,
                  labels={"x": "Oy", "y": "Sotuv ($)"}, title="Oylik sotuv trendi")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    by_city = f.groupby("city")["order_value"].sum().sort_values(ascending=False)
    fig = px.bar(x=by_city.index, y=by_city.values,
                 labels={"x": "Shahar", "y": "Sotuv ($)"}, title="Shaharlar bo'yicha sotuv")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = px.bar(cat_df, x="revenue", y="category_name", orientation="h",
                 labels={"revenue": "Sotuv ($)", "category_name": ""},
                 title="Kategoriya bo'yicha sotuv")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    opc = f.groupby("customer_id")["order_id"].nunique()
    ctype = opc.apply(lambda n: "Bir martalik" if n == 1 else "Qayta xarid qilgan").value_counts()
    fig = px.pie(names=ctype.index, values=ctype.values, title="Mijozlar: bir martalik vs qayta xarid")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Eng ko'p xarid qilgan mijozlar")
top_customers = (
    f.groupby(["customer_id", "full_name", "city"])
    .agg(order_count=("order_id", "nunique"), total_spent=("order_value", "sum"))
    .sort_values("total_spent", ascending=False)
    .head(15)
    .reset_index()
)
st.dataframe(top_customers, use_container_width=True, hide_index=True)

st.divider()

# ---------------- MongoDB: sharhlar va suhbatlar ----------------
st.header("🗨️ Mahsulot sharhlari va qo'llab-quvvatlash (MongoDB)")

mcol1, mcol2 = st.columns(2)

with mcol1:
    st.subheader("Mahsulotlar bo'yicha o'rtacha reyting")
    pipeline = [
        {"$match": {"verified_purchase": True}},
        {"$group": {"_id": "$product_name", "avg_rating": {"$avg": "$rating"}, "review_count": {"$sum": 1}}},
        {"$sort": {"avg_rating": -1}},
    ]
    rating_df = pd.DataFrame(list(db.product_reviews.aggregate(pipeline)))
    rating_df.columns = ["Mahsulot", "O'rtacha reyting", "Sharhlar soni"]
    st.dataframe(rating_df, use_container_width=True, hide_index=True)

with mcol2:
    st.subheader("Support mavzulari bo'yicha statistika")
    pipeline2 = [
        {"$group": {"_id": "$topic", "count": {"$sum": 1},
                     "resolved_count": {"$sum": {"$cond": ["$resolved", 1, 0]}}}},
        {"$sort": {"count": -1}},
    ]
    topics_df = pd.DataFrame(list(db.support_chats.aggregate(pipeline2)))
    topics_df["hal qilingan %"] = (100 * topics_df["resolved_count"] / topics_df["count"]).round(0)
    topics_df.columns = ["Mavzu", "Jami", "Hal qilingan", "Hal qilingan %"]
    st.dataframe(topics_df, use_container_width=True, hide_index=True)

st.caption("TechBozor — PostgreSQL + MongoDB + Streamlit demo dashboard")
