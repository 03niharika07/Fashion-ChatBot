import streamlit as st
import pandas as pd

# -----------------------------
# Load CSV files
# -----------------------------
products = pd.read_csv("products.csv")
faq = pd.read_csv("faq.csv")
sales = pd.read_csv("sales_summary.csv")

# -----------------------------
# Page settings
# -----------------------------
st.set_page_config(page_title="Fashion Store AI Chatbot", layout="wide")
st.title("Fashion Store AI Chatbot")
st.write("Ask me about products, returns, shipping, payment, store location, or trends.")

# -----------------------------
# Store chat history
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Detect user intent
# -----------------------------
def detect_intent(query):
    query = query.lower().strip()

    if query in ["hi", "hello", "hey", "hii", "helo"]:
        return "greeting"

    if any(word in query for word in ["trend", "trending", "forecast", "sales", "growth", "popular"]):
        return "sales"

    if any(word in query for word in ["return", "refund", "shipping", "delivery", "payment", "location", "store", "exchange"]):
        return "faq"

    if any(word in query for word in [
        "recommend", "show", "suggest", "find", "under", "price", "color",
        "category", "tops", "top", "shirt", "bag", "accessories", "footwear",
        "clothing", "outerwear", "stock", "black", "white", "blue", "pink"
    ]):
        return "product"

    return "unknown"

# -----------------------------
# Product response
# -----------------------------
def product_response(query):
    q = query.lower()
    filtered = products.copy()

    # Gender filter
    if "women" in q:
        filtered = filtered[filtered["gender"].astype(str).str.lower().str.contains("women", na=False)]
    elif "men" in q:
        filtered = filtered[filtered["gender"].astype(str).str.lower().str.contains("men", na=False)]
    elif "unisex" in q:
        filtered = filtered[filtered["gender"].astype(str).str.lower().str.contains("unisex", na=False)]

    # Category filter
    if "accessories" in q:
        filtered = filtered[filtered["category"].astype(str).str.lower().str.contains("accessorie", na=False)]
    elif "clothing" in q:
        filtered = filtered[filtered["category"].astype(str).str.lower().str.contains("clothing", na=False)]
    elif "outerwear" in q:
        filtered = filtered[filtered["category"].astype(str).str.lower().str.contains("outerwear", na=False)]
    elif "footwear" in q:
        filtered = filtered[filtered["category"].astype(str).str.lower().str.contains("footwear", na=False)]

    # Subcategory filter
    if "bag" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("bag", na=False)]
    elif "shirt" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("shirt", na=False)]
    elif "jeans" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("jeans", na=False)]
    elif "kurta" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("kurta", na=False)]
    elif "shorts" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("shorts", na=False)]
    elif "trousers" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("trouser", na=False)]
    elif "tops" in q or "top" in q:
        filtered = filtered[filtered["sub_category"].astype(str).str.lower().str.contains("shirt|kurta|top", na=False)]

    # Color filter
    if "black" in q:
        filtered = filtered[filtered["color"].astype(str).str.lower().str.contains("black", na=False)]
    elif "white" in q:
        filtered = filtered[filtered["color"].astype(str).str.lower().str.contains("white", na=False)]
    elif "blue" in q:
        filtered = filtered[filtered["color"].astype(str).str.lower().str.contains("blue", na=False)]
    elif "pink" in q:
        filtered = filtered[filtered["color"].astype(str).str.lower().str.contains("pink", na=False)]
    elif "red" in q:
        filtered = filtered[filtered["color"].astype(str).str.lower().str.contains("red", na=False)]

    # Season filter
    if "summer" in q:
        filtered = filtered[filtered["season"].astype(str).str.lower().str.contains("summer", na=False)]
    elif "winter" in q:
        filtered = filtered[filtered["season"].astype(str).str.lower().str.contains("winter", na=False)]
    elif "spring" in q:
        filtered = filtered[filtered["season"].astype(str).str.lower().str.contains("spring", na=False)]
    elif "fall" in q:
        filtered = filtered[filtered["season"].astype(str).str.lower().str.contains("fall", na=False)]

    # Stock filter
    if "in stock" in q:
        filtered = filtered[filtered["stock_status"].astype(str).str.lower().str.contains("in stock", na=False)]
    elif "low stock" in q:
        filtered = filtered[filtered["stock_status"].astype(str).str.lower().str.contains("low stock", na=False)]
    elif "out of stock" in q:
        filtered = filtered[filtered["stock_status"].astype(str).str.lower().str.contains("out of stock", na=False)]

    # Price filter
    words = q.split()
    for i, word in enumerate(words):
        if word == "under" and i + 1 < len(words):
            try:
                price_limit = float(words[i + 1])
                filtered = filtered[filtered["price(INR)"] <= price_limit]
            except ValueError:
                pass

    # Best rated / cheapest sorting
    if "top rated" in q or "best rated" in q:
        filtered = filtered.sort_values(by="rating", ascending=False)

    if "cheapest" in q or "lowest price" in q:
        filtered = filtered.sort_values(by="price(INR)", ascending=True)

    if filtered.empty:
        return "Sorry, I could not find matching products."

    result = filtered.head(5)

    reply = "Here are some matching products:\n\n"
    for _, row in result.iterrows():
        reply += (
            f"- {row['product_name']} | Brand: {row['product_brand']} | "
            f"₹{row['price(INR)']} | Color: {row['color']} | "
            f"Rating: {row['rating']} | Stock: {row['stock_status']}\n"
        )

    return reply

# -----------------------------
# FAQ response
# -----------------------------
def faq_response(query):
    q = query.lower()

    for _, row in faq.iterrows():
        topic = str(row["topic"]).lower()
        question = str(row["question"]).lower()
        answer = str(row["answer"])

        if topic in q or any(word in question for word in q.split()):
            return answer

    return "Sorry, I could not find an FAQ answer for that."

# -----------------------------
# Sales response
# -----------------------------
def sales_response(query):
    q = query.lower()

    if "trending" in q or "trend" in q:
        top_row = sales.sort_values(by="forecast_sales", ascending=False).iloc[0]
        return f"The top trending category is {top_row['category']} with forecast sales of {top_row['forecast_sales']}."

    elif "growth" in q:
        top_row = sales.sort_values(by="growth_percent", ascending=False).iloc[0]
        return f"The category with the highest growth is {top_row['category']} with growth of {top_row['growth_percent']}%."

    elif "decline" in q:
        low_row = sales.sort_values(by="growth_percent", ascending=True).iloc[0]
        return f"The category with the biggest decline is {low_row['category']} with growth of {low_row['growth_percent']}%."

    return "Sales insights are available for trends, forecast sales, growth, and decline."

# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    intent = detect_intent(user_input)

    if intent == "greeting":
        response = "Hello! I can help you with product recommendations, return or shipping questions, and sales trends."
    elif intent == "product":
        response = product_response(user_input)
    elif intent == "faq":
        response = faq_response(user_input)
    elif intent == "sales":
        response = sales_response(user_input)
    else:
        response = "I can help with product recommendations, customer support, and fashion sales trends. Try asking about products, returns, payment, or trending categories."

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})