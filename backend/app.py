

import os
from datetime import datetime
from decimal import Decimal

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector import pooling
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

# ------------------------------------------------------------------
# DB settings - .env file
# ------------------------------------------------------------------
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "hotel_bar_db"),
}
APP_NAME = os.environ.get("APP_NAME", "Bar Ledger")
HOTEL_PHONE = os.environ.get("HOTEL_PHONE", "")
HOTEL_ADDRESS = os.environ.get("HOTEL_ADDRESS", "")
HOTEL_GSTIN = os.environ.get("HOTEL_GSTIN", "")
HOTEL_FSSAI = os.environ.get("HOTEL_FSSAI", "")
POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "10"))


FRONTEND_ORIGINS = os.environ.get("FRONTEND_ORIGIN", "http://127.0.0.1:8000,http://localhost:8000")

app = Flask(__name__)

_pool = None


def get_pool():
    """Connection pool ek veळach banto (lazy), pudhe reuse hoto."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(pool_name="hotelbar_pool", pool_size=POOL_SIZE, **DB_CONFIG)
    return _pool


def fetch_all(sql, params=()):
    con = get_pool().get_connection()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        con.close()  # pool la connection परत करto, band nahi karत


def fetch_one(sql, params=()):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    con = get_pool().get_connection()
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        con.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
    finally:
        con.close()


@app.errorhandler(MySQLError)
def handle_mysql_error(err):
    msg = str(err)
    if getattr(err, "errno", None) == 1062:
        return jsonify({"error": "Already exists. Please use a different name."}), 409
    return jsonify({"error": msg}), 500


def to_decimal(value):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def money(value):
    return float(f"{float(value or 0):.2f}")


def json_safe(row):
    """Decimal/datetime JSON madhe convert nahi hotात thet, mhanun fix."""
    if row is None:
        return None
    out = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def json_safe_list(rows):
    return [json_safe(r) for r in rows]


# ------------------------------------------------------------------ CORS --
@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    allowed = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]
    if origin in allowed:
        resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def cors_preflight(_any):
    return ("", 204)


def _check_db_config():
    if not DB_CONFIG.get("password"):
        print("=" * 60)
        print("WARNING: .env was not found or DB_PASSWORD is empty.")
        print("Copy .env.example to .env and fill in the required values.")
        print("=" * 60)


# =============================================================== ROUTES ==

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": APP_NAME})


@app.route("/api/dashboard")
def api_dashboard():
    stats = fetch_one("""
        SELECT
        (SELECT COUNT(*) FROM products) products,
        (SELECT COUNT(*) FROM vendors) vendors,
        (SELECT COALESCE(SUM(stock),0) FROM products) stock,
        (SELECT COALESCE(SUM(grand_total),0) FROM bills) sales
    """)
    low = fetch_all("SELECT * FROM products WHERE stock <= min_stock ORDER BY stock")
    return jsonify({"stats": json_safe(stats), "low_stock": json_safe_list(low), "app_name": APP_NAME})


@app.route("/api/products", methods=["GET", "POST"])
def api_products():
    if request.method == "POST":
        d = request.get_json(force=True)
        if not d.get("name"):
            return jsonify({"error": "Product name is required"}), 400
        category = d.get("category")
        volume_value = d.get("volume_value") or None
        volume_unit = d.get("volume_unit") or None
        if category == "Food":
            volume_value = None
            volume_unit = None
        execute(
            "INSERT INTO products(name,category,volume_value,volume_unit,rate,stock,min_stock) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (d.get("name"), category, volume_value, volume_unit, d.get("rate"), d.get("stock"), d.get("min_stock") or 5),
        )
        return jsonify({"ok": True}), 201
    rows = fetch_all("SELECT * FROM products ORDER BY category, name")
    return jsonify(json_safe_list(rows))


@app.route("/api/vendors", methods=["GET", "POST"])
def api_vendors():
    if request.method == "POST":
        d = request.get_json(force=True)
        if not d.get("name"):
            return jsonify({"error": "Vendor name is required"}), 400
        execute(
            "INSERT INTO vendors(name,phone,address) VALUES(%s,%s,%s)",
            (d.get("name"), d.get("phone"), d.get("address")),
        )
        return jsonify({"ok": True}), 201
    rows = fetch_all("SELECT * FROM vendors ORDER BY name")
    return jsonify(json_safe_list(rows))


@app.route("/api/purchases", methods=["GET", "POST"])
def api_purchases():
    if request.method == "POST":
        d = request.get_json(force=True)
        if not d.get("vendor_id") or not d.get("product_id"):
            return jsonify({"error": "Vendor and product are required"}), 400
        qty = int(d["qty"])
        if qty <= 0:
            return jsonify({"error": "Qty must be greater than 0"}), 400
        rate = to_decimal(d["rate"])
        total = qty * rate
        execute(
            "INSERT INTO purchases(vendor_id,product_id,qty,rate,total) VALUES(%s,%s,%s,%s,%s)",
            (d["vendor_id"], d["product_id"], qty, rate, total),
        )
        execute("UPDATE products SET stock = stock + %s WHERE id = %s", (qty, d["product_id"]))
        return jsonify({"ok": True}), 201
    rows = fetch_all("""
        SELECT pu.*, v.name AS vendor, p.name AS product, p.volume_value, p.volume_unit
        FROM purchases pu
        JOIN vendors v ON v.id = pu.vendor_id
        JOIN products p ON p.id = pu.product_id
        ORDER BY pu.id DESC
    """)
    return jsonify(json_safe_list(rows))


def _save_bill(hotel_name, table_no, customer_name, phone, payment, items):
    """items = list of dict {product_id, name, category, qty, rate}"""
    food = liquor = other = Decimal("0")
    lines = []
    for it in items:
        qty = int(it["qty"])
        if qty <= 0:
            continue
        rate = to_decimal(it["rate"])
        amount = rate * qty
        lines.append((it, qty, rate, amount))
        if it["category"] == "Food":
            food += amount
        elif it["category"] == "Liquor":
            liquor += amount
        else:
            other += amount

    if not lines:
        return None

    sgst = food * Decimal("0.025")
    cgst = food * Decimal("0.025")
    vat = liquor * Decimal("0.10")
    grand = food + sgst + cgst + liquor + vat + other
    bill_no = "BILL-" + datetime.now().strftime("%Y%m%d%H%M%S")

    bill_id = execute(
        """INSERT INTO bills(bill_no,hotel_name,hotel_phone,hotel_address,hotel_gstin,hotel_fssai,table_no,customer_name,phone,
           food_total,sgst,cgst,liquor_subtotal,vat,liquor_total,other_total,grand_total,payment)
           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (bill_no, hotel_name, HOTEL_PHONE, HOTEL_ADDRESS, HOTEL_GSTIN, HOTEL_FSSAI, table_no, customer_name, phone,
         food, sgst, cgst, liquor, vat, liquor + vat, other, grand, payment),
    )
    for it, qty, rate, amount in lines:
        execute(
            """INSERT INTO bill_items(bill_id,product_id,item_name,category,qty,rate,amount)
               VALUES(%s,%s,%s,%s,%s,%s,%s)""",
            (bill_id, it["product_id"], it["name"], it["category"], qty, rate, amount),
        )
        execute("UPDATE products SET stock = stock - %s WHERE id = %s", (qty, it["product_id"]))
    return bill_id


@app.route("/api/bill", methods=["POST"])
def api_create_bill():
    d = request.get_json(force=True)
    bill_id = _save_bill(
        d.get("hotel_name") or APP_NAME, d.get("table_no"), d.get("customer_name"),
        d.get("phone"), d.get("payment"), d.get("items", []),
    )
    if not bill_id:
        return jsonify({"error": "No items in bill"}), 400
    return jsonify({"ok": True, "bill_id": bill_id}), 201


@app.route("/api/bills")
def api_bills():
    rows = fetch_all("SELECT * FROM bills ORDER BY id DESC")
    return jsonify(json_safe_list(rows))


@app.route("/api/bills/<int:bill_id>")
def api_bill_detail(bill_id):
    b = fetch_one("SELECT * FROM bills WHERE id = %s", (bill_id,))
    if not b:
        return jsonify({"error": "not found"}), 404
    items = fetch_all("SELECT * FROM bill_items WHERE bill_id = %s", (bill_id,))
    return jsonify({"bill": json_safe(b), "items": json_safe_list(items)})


@app.route("/api/tables", methods=["GET", "POST"])
def api_tables():
    if request.method == "POST":
        next_no = fetch_one("SELECT COUNT(*) + 1 AS n FROM open_tables")["n"]
        execute("INSERT INTO open_tables(name) VALUES(%s)", (f"Table {next_no}",))
        return jsonify({"ok": True}), 201
    rows = fetch_all("""
        SELECT ot.id, ot.name,
        COALESCE(SUM(oti.qty), 0) AS item_count,
        COALESCE(SUM(oti.qty * p.rate), 0) AS total
        FROM open_tables ot
        LEFT JOIN open_table_items oti ON oti.table_id = ot.id AND oti.qty > 0
        LEFT JOIN products p ON p.id = oti.product_id
        GROUP BY ot.id, ot.name
        ORDER BY ot.id
    """)
    return jsonify(json_safe_list(rows))


@app.route("/api/tables/<int:table_id>", methods=["GET"])
def api_table_detail(table_id):
    tbl = fetch_one("SELECT * FROM open_tables WHERE id = %s", (table_id,))
    if not tbl:
        return jsonify({"error": "not found"}), 404
    cart = fetch_all("""
        SELECT oti.product_id, oti.qty, p.name, p.rate, p.category, p.stock
        FROM open_table_items oti
        JOIN products p ON p.id = oti.product_id
        WHERE oti.table_id = %s AND oti.qty > 0
        ORDER BY p.category, p.name
    """, (table_id,))
    total = sum(to_decimal(r["rate"]) * r["qty"] for r in cart)
    return jsonify({"table": json_safe(tbl), "cart": json_safe_list(cart), "cart_total": float(total)})


@app.route("/api/tables/<int:table_id>/add", methods=["POST"])
def api_table_add(table_id):
    product_id = request.get_json(force=True)["product_id"]
    existing = fetch_one(
        "SELECT * FROM open_table_items WHERE table_id = %s AND product_id = %s",
        (table_id, product_id),
    )
    if existing:
        execute("UPDATE open_table_items SET qty = qty + 1 WHERE id = %s", (existing["id"],))
    else:
        execute("INSERT INTO open_table_items(table_id, product_id, qty) VALUES(%s,%s,1)", (table_id, product_id))
    return jsonify({"ok": True})


@app.route("/api/tables/<int:table_id>/qty", methods=["POST"])
def api_table_qty(table_id):
    d = request.get_json(force=True)
    product_id = d["product_id"]
    delta = int(d["delta"])
    row = fetch_one(
        "SELECT * FROM open_table_items WHERE table_id = %s AND product_id = %s",
        (table_id, product_id),
    )
    if row:
        new_qty = row["qty"] + delta
        if new_qty <= 0:
            execute("DELETE FROM open_table_items WHERE id = %s", (row["id"],))
        else:
            execute("UPDATE open_table_items SET qty = %s WHERE id = %s", (new_qty, row["id"]))
    return jsonify({"ok": True})


@app.route("/api/tables/<int:table_id>/clear", methods=["POST"])
def api_table_clear(table_id):
    execute("DELETE FROM open_table_items WHERE table_id = %s", (table_id,))
    return jsonify({"ok": True})


@app.route("/api/tables/<int:table_id>/generate", methods=["POST"])
def api_table_generate(table_id):
    tbl = fetch_one("SELECT * FROM open_tables WHERE id = %s", (table_id,))
    if not tbl:
        return jsonify({"error": "not found"}), 404
    cart = fetch_all("""
        SELECT oti.product_id, oti.qty, p.name, p.rate, p.category
        FROM open_table_items oti
        JOIN products p ON p.id = oti.product_id
        WHERE oti.table_id = %s AND oti.qty > 0
    """, (table_id,))
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    d = request.get_json(silent=True) or {}
    bill_id = _save_bill(
        APP_NAME, tbl["name"], d.get("customer_name"), d.get("phone"),
        d.get("payment") or "Cash", cart,
    )
    # Clear the cart after saving the bill, but retain the table itself.
    execute("DELETE FROM open_table_items WHERE table_id = %s", (table_id,))
    return jsonify({"ok": True, "bill_id": bill_id, "table_id": table_id})


@app.route("/api/report")
def api_report():
    rows = fetch_all("""
        SELECT p.name, p.category, p.volume_value, p.volume_unit, p.min_stock, p.stock AS available_stock,
        COALESCE((SELECT SUM(pu.qty) FROM purchases pu WHERE pu.product_id = p.id), 0) AS stock_in,
        COALESCE((SELECT SUM(bi.qty) FROM bill_items bi WHERE bi.product_id = p.id), 0) AS stock_out,
        (SELECT MAX(pu.created_at) FROM purchases pu WHERE pu.product_id = p.id) AS last_stock_in_at,
        (SELECT MAX(b.created_at)
         FROM bill_items bi
         JOIN bills b ON b.id = bi.bill_id
         WHERE bi.product_id = p.id) AS last_sold_at
        FROM products p
        ORDER BY p.category, p.name
    """)
    return jsonify(json_safe_list(rows))


if __name__ == "__main__":
    _check_db_config()
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug_mode, port=port)
