"""ER diagramma - TechBozor ma'lumotlar bazasi tuzilishi (soddalashtirilgan)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 9.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 9.2)
ax.axis("off")

LINE_H = 0.36
TITLE_H = 0.55

def draw_table(x, y, w, title, fields, color):
    h = TITLE_H + len(fields) * LINE_H + 0.25
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                          linewidth=1.5, edgecolor="#333333", facecolor=color)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.32, title, ha="center", va="top",
            fontsize=12, fontweight="bold", color="white")
    ax.plot([x+0.15, x+w-0.15], [y+h-TITLE_H+0.08, y+h-TITLE_H+0.08], color="white", linewidth=1)
    for i, f in enumerate(fields):
        ax.text(x + 0.25, y + h - TITLE_H - i*LINE_H, f, ha="left", va="top",
                fontsize=10, color="white", family="monospace")
    return h

# CUSTOMERS (top-left)
h_cust = draw_table(0.4, 4.9, 3.0, "CUSTOMERS", [
    "PK customer_id",
    "   full_name",
    "   email (UQ)",
    "   city",
    "   registered_at"
], "#4C72B0")

# CATEGORIES (top-middle)
h_cat = draw_table(4.6, 7.0, 2.8, "CATEGORIES", [
    "PK category_id",
    "   category_name"
], "#8172B2")

# PRODUCTS (middle)
h_prod = draw_table(4.6, 3.7, 2.8, "PRODUCTS", [
    "PK product_id",
    "   sku (UQ)",
    "   product_name",
    "FK category_id",
    "   price / stock"
], "#DD8452")

# ORDERS (bottom-left)
h_ord = draw_table(0.4, 1.6, 3.0, "ORDERS", [
    "PK order_id",
    "FK customer_id",
    "   order_date",
    "   status"
], "#55A868")

# ORDER_ITEMS (right)
h_oi = draw_table(8.4, 3.3, 3.2, "ORDER_ITEMS", [
    "PK,FK order_id",
    "PK,FK product_id",
    "      quantity",
    "      unit_price"
], "#C44E52")

def arrow(p1, p2, label, label_offset=(0.15, 0.1)):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=15,
                         color="#444444", linewidth=1.4,
                         connectionstyle="arc3,rad=0.0")
    ax.add_patch(a)
    mx = (p1[0]+p2[0])/2 + label_offset[0]
    my = (p1[1]+p2[1])/2 + label_offset[1]
    ax.text(mx, my, label, fontsize=9, color="#333333", ha="left", va="center",
            style="italic", bbox=dict(facecolor="white", edgecolor="none", pad=1))

# customers -> orders (vertical, left column)
arrow((1.9, 4.9), (1.9, 3.8), "1:N", label_offset=(0.2, 0))
# orders -> order_items (long diagonal, routed below products)
arrow((3.4, 2.3), (8.4, 3.5), "1:N", label_offset=(-2.3, 0.35))
# categories -> products (vertical, middle column)
arrow((6.0, 7.0), (6.0, 5.75), "1:N", label_offset=(0.2, 0))
# products -> order_items (short horizontal-ish)
arrow((7.4, 4.6), (8.4, 4.6), "1:N", label_offset=(0.05, 0.2))

ax.text(6, 9.0, "TechBozor — Ma'lumotlar Bazasi ER Diagrammasi",
        ha="center", fontsize=14, fontweight="bold")
ax.text(6, 8.75, "(PK = Primary Key, FK = Foreign Key, UQ = Unique)",
        ha="center", fontsize=9.5, color="#555555", style="italic")

plt.tight_layout()
plt.savefig("/home/claude/project/charts/00_er_diagram.png", dpi=140, bbox_inches="tight")
print("saved")
