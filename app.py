import streamlit as st
from datetime import datetime
import uuid

st.set_page_config(
    page_title="ShopEase | Online Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Demo product catalogue
# -----------------------------
PRODUCTS = [
    {"id": 1, "name": "Classic T-Shirt", "category": "Fashion", "price": 499, "emoji": "👕", "description": "Comfortable everyday cotton-style tee."},
    {"id": 2, "name": "Running Sneakers", "category": "Fashion", "price": 1499, "emoji": "👟", "description": "Lightweight sneakers for everyday movement."},
    {"id": 3, "name": "Wireless Headphones", "category": "Electronics", "price": 1999, "emoji": "🎧", "description": "Enjoy music and podcasts without wires."},
    {"id": 4, "name": "Smart Watch", "category": "Electronics", "price": 2499, "emoji": "⌚", "description": "A simple smartwatch-style accessory."},
    {"id": 5, "name": "Travel Backpack", "category": "Accessories", "price": 899, "emoji": "🎒", "description": "A practical bag for college and travel."},
    {"id": 6, "name": "Water Bottle", "category": "Accessories", "price": 299, "emoji": "🧴", "description": "Reusable bottle for daily hydration."},
    {"id": 7, "name": "Desk Lamp", "category": "Home", "price": 699, "emoji": "💡", "description": "A neat lamp for your study table."},
    {"id": 8, "name": "Coffee Mug", "category": "Home", "price": 199, "emoji": "☕", "description": "A simple mug for tea or coffee."},
]

CURRENCY = "₹"

def money(value):
    return f"{CURRENCY}{value:,.2f}"

def init_state():
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    if "orders" not in st.session_state:
        st.session_state.orders = []
    if "last_order" not in st.session_state:
        st.session_state.last_order = None
    if "page" not in st.session_state:
        st.session_state.page = "Shop"

init_state()

# -----------------------------
# Sidebar navigation and filters
# -----------------------------
st.sidebar.title("🛍️ ShopEase")
st.sidebar.caption("A student e-commerce project built with Python + Streamlit.")
page = st.sidebar.radio("Navigation", ["Shop", "Shopping Cart", "Checkout", "Order History"], index=["Shop", "Shopping Cart", "Checkout", "Order History"].index(st.session_state.page))
st.session_state.page = page
st.sidebar.divider()
st.sidebar.metric("Items in cart", sum(st.session_state.cart.values()))
st.sidebar.caption("Demo project only — no real payment is collected.")

st.title("🛍️ ShopEase")
st.write("Discover everyday products at student-friendly prices.")

# -----------------------------
# Shop page
# -----------------------------
if page == "Shop":
    top1, top2 = st.columns([2, 1])
    with top1:
        search = st.text_input("🔎 Search products", placeholder="Try headphones, bottle, fashion...")
    with top2:
        categories = ["All"] + sorted({p["category"] for p in PRODUCTS})
        category = st.selectbox("Category", categories)

    filtered = [
        p for p in PRODUCTS
        if (search.strip().lower() in p["name"].lower()
            or search.strip().lower() in p["description"].lower()
            or search.strip().lower() in p["category"].lower())
        and (category == "All" or p["category"] == category)
    ]

    st.caption(f"{len(filtered)} product(s) found")
    if not filtered:
        st.info("No products match your search. Try another keyword or category.")
    else:
        cols = st.columns(3)
        for i, product in enumerate(filtered):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:56px;text-align:center'>{product['emoji']}</div>", unsafe_allow_html=True)
                    st.subheader(product["name"])
                    st.caption(product["category"])
                    st.write(product["description"])
                    st.markdown(f"### {money(product['price'])}")
                    if st.button("➕ Add to cart", key=f"add_{product['id']}", use_container_width=True):
                        st.session_state.cart[product["id"]] = st.session_state.cart.get(product["id"], 0) + 1
                        st.toast(f"{product['name']} added to cart")
                        st.rerun()

# -----------------------------
# Shopping cart page
# -----------------------------
elif page == "Shopping Cart":
    st.header("🛒 Your Shopping Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty. Open Shop and add a product first.")
        if st.button("Browse products"):
            st.session_state.page = "Shop"
            st.rerun()
    else:
        subtotal = 0
        for product_id in list(st.session_state.cart.keys()):
            product = next((p for p in PRODUCTS if p["id"] == product_id), None)
            if not product:
                continue
            qty = st.session_state.cart[product_id]
            row1, row2, row3, row4 = st.columns([3, 1, 1, 1])
            with row1:
                st.write(f"**{product['emoji']} {product['name']}**")
                st.caption(money(product["price"]) + " each")
            with row2:
                new_qty = st.number_input("Qty", min_value=1, max_value=99, value=qty, key=f"qty_{product_id}")
                if new_qty != qty:
                    st.session_state.cart[product_id] = int(new_qty)
                    st.rerun()
            with row3:
                line_total = product["price"] * qty
                st.write("**Line total**")
                st.write(money(line_total))
            with row4:
                st.write("")
                if st.button("Remove", key=f"remove_{product_id}"):
                    del st.session_state.cart[product_id]
                    st.rerun()
            subtotal += product["price"] * qty
            st.divider()

        st.subheader(f"Subtotal: {money(subtotal)}")
        st.caption("Shipping: Free | Taxes: included for this demo")
        left, right = st.columns(2)
        with left:
            if st.button("Continue shopping", use_container_width=True):
                st.session_state.page = "Shop"
                st.rerun()
        with right:
            if st.button("Proceed to checkout", type="primary", use_container_width=True):
                st.session_state.page = "Checkout"
                st.rerun()

# -----------------------------
# Checkout page
# -----------------------------
elif page == "Checkout":
    st.header("✅ Checkout")
    if not st.session_state.cart:
        st.info("Your cart is empty. Add products before checkout.")
        if st.button("Go to Shop"):
            st.session_state.page = "Shop"
            st.rerun()
    else:
        subtotal = sum(
            next(p["price"] for p in PRODUCTS if p["id"] == pid) * qty
            for pid, qty in st.session_state.cart.items()
        )
        st.subheader("Order summary")
        for pid, qty in st.session_state.cart.items():
            product = next(p for p in PRODUCTS if p["id"] == pid)
            st.write(f"- {product['name']} × {qty}: **{money(product['price'] * qty)}**")
        st.markdown(f"### Total: {money(subtotal)}")
        st.caption("This is a demo checkout. Do not enter real payment details.")

        with st.form("checkout_form"):
            name = st.text_input("Full name *", placeholder="Enter your name")
            email = st.text_input("Email address *", placeholder="you@example.com")
            phone = st.text_input("Mobile number *", placeholder="10-digit mobile number")
            address = st.text_area("Delivery address *", placeholder="House/flat, street, area, city, PIN code")
            payment = st.selectbox("Demo payment method", ["Cash on Delivery (Demo)", "UPI (Demo — no payment taken)"])
            submitted = st.form_submit_button("Place demo order", type="primary", use_container_width=True)

        if submitted:
            if not all([name.strip(), email.strip(), phone.strip(), address.strip()]):
                st.error("Please complete all required fields.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            elif not phone.isdigit() or len(phone) != 10:
                st.error("Please enter a 10-digit mobile number.")
            else:
                order = {
                    "order_id": "SE-" + uuid.uuid4().hex[:8].upper(),
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "customer": name.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "address": address.strip(),
                    "payment": payment,
                    "items": [
                        {
                            "name": next(p["name"] for p in PRODUCTS if p["id"] == pid),
                            "quantity": qty,
                            "price": next(p["price"] for p in PRODUCTS if p["id"] == pid),
                        }
                        for pid, qty in st.session_state.cart.items()
                    ],
                    "total": subtotal,
                }
                st.session_state.orders.insert(0, order)
                st.session_state.last_order = order
                st.session_state.cart = {}
                st.session_state.page = "Order History"
                st.rerun()

# -----------------------------
# Order history / confirmation
# -----------------------------
elif page == "Order History":
    st.header("📦 Orders & Confirmation")
    if st.session_state.last_order:
        order = st.session_state.last_order
        st.success("Your demo order was placed successfully!")
        st.markdown(f"## Order ID: `{order['order_id']}`")
        st.write(f"**Order date:** {order['date']}")
        st.write(f"**Customer:** {order['customer']}")
        st.write(f"**Payment:** {order['payment']}")
        st.write(f"**Delivery address:** {order['address']}")
        st.write("**Items:**")
        for item in order["items"]:
            st.write(f"- {item['name']} × {item['quantity']} — {money(item['price'] * item['quantity'])}")
        st.markdown(f"### Order total: {money(order['total'])}")
        st.caption("Orders are kept in memory during the current app session. They are not saved to a permanent database.")
    else:
        st.info("No orders have been placed in this session yet.")

    if len(st.session_state.orders) > 1:
        st.subheader("Previous orders in this session")
        for order in st.session_state.orders[1:]:
            st.write(f"**{order['order_id']}** — {order['customer']} — {money(order['total'])} — {order['date']}")

st.divider()
st.caption("ShopEase FP Project • Built with Python and Streamlit • Demo store, not a real payment service")
