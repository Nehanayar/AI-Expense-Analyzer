import streamlit as st
import pandas as pd
import plotly.express as px
from auth import login, register
from report import generate_pdf_report
from database import *
import os
from sentence_transformers import SentenceTransformer, util



# 🔥 ADDED: EMAIL IMPORTS
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
import re

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ---------------- EMAIL FUNCTION (ADDED) ---------------- #
def send_email(to_email, subject, message):
    try:
        sender_email = os.getenv("EMAIL_USER")
        app_password = os.getenv("EMAIL_PASS")

        if not sender_email or not app_password:
            st.error("❌ Email credentials not loaded")
            return

        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        st.success("Email sent successfully ✅")

    except Exception as e:
        st.error(f"Email error: {e}")

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="AI Expense Analyzer", layout="wide")

# 🎨 ---------------- UI STYLE ---------------- #
st.markdown("""
<style>
/* background */
.stApp {
    background-color: #f5f7fa;
}

/* ONLY ONE TITLE BOX */
.title-box {
    background-color: #00bcd4;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    color: black;
    margin-top: 10px;
    margin-bottom: 20px;
}



/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #0f9d8a, #1abc9c);
    color: white;
    border-radius: 12px;
    padding: 10px;
    font-weight: 600;
    width: 100%;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: translateY(-2px);
}

/* Inputs */
.stTextInput>div>div>input,
.stNumberInput input {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
}

/* Chat */
.chat-user {
    background: #e3f2fd;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 5px;
}
.chat-bot {
    background: #e8f5e9;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 5px;
}

/* AI box */
.success-box {
    background: linear-gradient(135deg, #1abc9c, #16a085);
    color: white;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box">💰 AI Expense Analyzer</div>', unsafe_allow_html=True)


# ---------------- DB INIT ---------------- #
create_tables()
insert_default_categories()

# ---------------- MODEL ---------------- #
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

ai_model = load_model()

# ---------------- AI ---------------- #
ai_categories = {
    "Food": "pizza burger restaurant food swiggy zomato meals",
    "Travel": "uber ola taxi bus train transport travel cab",
    "Bills": "electricity water rent internet recharge bills",
    "Shopping": "amazon flipkart clothes shoes electronics shopping",
    "Fitness": "gym workout yoga sports health fitness",
    "Insurance": "LIC insurance health policy premium life insurance"
}

@st.cache_resource
def load_embeddings():
    return {cat: ai_model.encode(text) for cat, text in ai_categories.items()}

ai_embeddings = load_embeddings()

def predict_category(text):
    text_emb = ai_model.encode(text.lower())
    scores = {}

    for cat, emb in ai_embeddings.items():
        scores[cat] = float((text_emb @ emb) /
                            ((text_emb @ text_emb)**0.5 * (emb @ emb)**0.5))

    best = max(scores, key=scores.get)
    confidence = scores[best]

    if confidence < 0.30:
        return "Uncategorized", confidence

    return best, confidence


# ---------------- SESSION ---------------- #
if "user" not in st.session_state:
    st.session_state.user = None

#st.title("💰 AI Expense Analyzer")



# ---------------- AUTH SYSTEM ---------------- #

if not st.session_state.user:
    menu = st.sidebar.selectbox(
        "Menu",
        ["Login", "Register"],
        key="auth_menu"
    )
    # if menu == "Login":
    #     pass
    # elif menu == "Register":
    #     pass




    # ---------------- REGISTER ---------------- #
    if menu == "Register":
        st.subheader("📝 Register")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        email = st.text_input("Email")

        if st.button("Register"):

            # 🔥 Email validation
            if not is_valid_email(email):
                st.error("❌ Invalid Email Format")

            elif not user or not pwd or not email:
                st.warning("Please fill all fields ⚠️")

            else:
                result = register(user, pwd, email)

                if result == "Success":
                    st.success("Account Created ✅")

                elif result == "Username Exists":
                    st.error("Username already exists ❌")

                elif result == "Email Exists":
                    st.error("Email already exists ❌")

                else:
                    st.error(result)



    # ---------------- LOGIN ---------------- #
    elif menu == "Login":
        st.subheader("🔐 Login")

        email = st.text_input("Email",  key="login_email")
        pwd = st.text_input("Password", type="password" , key="login_pwd")

        if st.button("Login" , key="login_btn"):
            result = login(email, pwd)

            if result:
                st.session_state.user = result
                st.session_state.alert_sent = False
                st.success("Login Successful 🎉")
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")






# ---------------- MAIN APP ---------------- #
else:

    user_id = st.session_state.user[0]

    page = st.sidebar.radio(
        "Navigation",
        ["Add Expense", "View Expenses", "Dashboard", "Chatbot", "Logout"]
    )

    # ================= LOGOUT ================= #
    if page == "Logout":
        st.session_state.user = None
        st.success("Logged out successfully 👋")
        st.rerun()

    # ================= ADD EXPENSE ================= #
    elif page == "Add Expense":
        st.subheader("➕ Add Expense")

        description = st.text_input("Expense Description")
        amount = st.number_input("Amount", min_value=0.0)
        date = st.date_input("Date")

        categories = view_categories()

        ai_category = None

        if description:
            ai_category, confidence = predict_category(description)
            st.info(f"🤖 AI Suggestion: {ai_category} ({round(confidence*100,2)}%)")

        use_ai = st.checkbox("Use AI Suggested Category", value=True)

        col1, col2 = st.columns(2)
        with col1:
            selected_cat = st.selectbox("Select Category", categories)
        with col2:
            new_cat = st.text_input("Or Add New Category")

        if st.button("Add Expense"):
            if ai_category and ai_category != "Uncategorized" and use_ai:
                final_category = ai_category
            elif new_cat.strip():
                final_category = new_cat.strip().title()
                if final_category not in categories:
                    add_category(final_category)
            else:
                final_category = selected_cat

            if description and amount > 0 and final_category:
                add_expense(user_id, amount, final_category, str(date))
                st.success(f"✅ Added in '{final_category}'")
                st.rerun()
            else:
                st.warning("Fill all fields")

        st.markdown("---")
        st.subheader("📌 Recent Expenses")

        data = view_expense(user_id)
        if data:
            df = pd.DataFrame(data, columns=["Amount", "Category", "Date"])
            st.dataframe(df.tail(5), use_container_width=True)
        else:
            st.info("No expenses yet")

    # ================= VIEW ================= #
    elif page == "View Expenses":
        st.subheader("📋 All Expenses")

        data = get_expenses(user_id)

        if data:
            df = pd.DataFrame(data, columns=["ID","User","Amount","Category","Date"])
            st.dataframe(df[["Amount","Category","Date"]], use_container_width=True)

            options = {
                f"{r['Category']} - ₹{r['Amount']} ({r['Date']})": r["ID"]
                for _, r in df.iterrows()
            }

            selected = st.selectbox("Select Expense", list(options.keys()))

            if st.button("Delete Expense"):
                delete_expense(options[selected])
                st.success("Deleted ✅")
                st.rerun()
        else:
            st.info("No expenses found")



    # ================= DASHBOARD ================= #

    elif page == "Dashboard":
        st.subheader("📊 Dashboard")

        data = get_expenses(user_id)

        if data:
            df = pd.DataFrame(data, columns=["ID", "User", "Amount", "Category", "Date"])
            df["Date"] = pd.to_datetime(df["Date"])

            # ================= ML MODEL ================= #
            from model import load_model, train_model, predict_next_month, get_forecast

            model = load_model()
            if model is None:
                model = train_model(df)

            # ---------------- BUDGET ---------------- #
            st.subheader("🎯 Set Budget")

            db_budget = get_budget(user_id)

            if "budget" not in st.session_state:
                st.session_state.budget = db_budget

            budget = st.number_input(
                "Enter Monthly Budget",
                key="budget_input",
                value=float(st.session_state.budget)
            )

            if st.button("Save Budget"):
                set_budget(user_id, budget)
                st.session_state.budget = budget
                st.session_state.alert_sent = False
                st.success("Budget Saved ✅")
                st.rerun()

            # ---------------- CALCULATIONS ---------------- #
            total = df["Amount"].sum()

            now = pd.Timestamp.now()
            this_month_df = df[
                (df["Date"].dt.month == now.month) &
                (df["Date"].dt.year == now.year)
                ]
            this_month_total = this_month_df["Amount"].sum()

            cat_sum = df.groupby("Category")["Amount"].sum()
            most_spent = cat_sum.idxmax()

            budget_val = st.session_state.budget

            # ================= ML PREDICTION ================= #
            monthly_check = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()

            if len(monthly_check) < 3:
                st.warning("⚠️ Need at least 3 months data for ML prediction")
                ml_prediction, lower, upper, insight = 0, 0, 0, "Not enough data"
            else:
                ml_prediction, lower, upper, insight = predict_next_month(model, df)

            # ---------------- METRICS ---------------- #
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total", total)
            col2.metric("🎯 Budget", budget_val)
            col3.metric("📅 This Month", f"₹{this_month_total}")

            # ---------------- STATUS ---------------- #
            if budget_val > 0 and this_month_total > budget_val:
                status = f"⚠️ You exceeded your monthly budget! (₹{this_month_total})"
                st.error(status)
            else:
                status = f"✅ You are within budget (₹{this_month_total})"
                st.success(status)

            # ---------------- GRAPHS ---------------- #
            left, right = st.columns(2)

            with left:
                fig = px.pie(values=cat_sum.values, names=cat_sum.index, hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

            with right:
                df_sorted = df.sort_values("Date")
                fig = px.line(df_sorted, x="Date", y="Amount")
                fig.update_traces(line=dict(width=3))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # ================= AI INSIGHT ================= #
            st.markdown("### 🧠 AI Insight")

            if ml_prediction > 0:
                st.subheader("🤖 Next Month Prediction")
                st.write(f"₹{ml_prediction:.2f}")

                st.info(f"📊 Expected Range: ₹{lower:.2f} - ₹{upper:.2f}")
                st.success(insight)

                if ml_prediction > budget_val:
                    st.error(f"⚠️ AI predicts next month will exceed budget (₹{ml_prediction:.2f})")
                else:
                    st.success(f"✅ AI predicts next month is safe (₹{ml_prediction:.2f})")

                st.warning(f"⚡ You mostly spend on {most_spent}, please reduce it")

            else:
                st.warning("⚠️ Prediction not available (need more data)")

            # ---------------- EMAIL ALERT ---------------- #
            user_email = st.session_state.user[3]

            if not st.session_state.get("alert_sent", False):
                message = f"""
    {status}

    💰 Total: ₹{this_month_total}
    🎯 Budget: ₹{budget_val}

    📊 Most Spending: {most_spent}
    🤖 ML Prediction: ₹{ml_prediction if ml_prediction else 'Not available'}

    ⚡ Reduce spending on {most_spent}
    """
                send_email(user_email, "📊 Expense Report", message)
                st.session_state.alert_sent = True

            st.markdown("---")

            # ---------------- MONTHLY BAR GRAPH (FIXED) ---------------- #
            monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
            monthly.index = monthly.index.astype(str)

            fig = px.bar(
                x=monthly.index,
                y=monthly.values,
                color_discrete_sequence=["#00bcd4"]
            )
            st.plotly_chart(fig, use_container_width=True)


            # ================= 📄 DOWNLOAD REPORT (LAST) ================= #
            st.markdown("---")

            st.subheader("📄 Download  Report")

            st.caption("Download your complete expense report with charts & prediction")

            if st.button("⬇️ Download Report"):
                file_path = generate_pdf_report(
                    st.session_state.user,
                    df,
                    total,
                    ml_prediction
                )

                with open(file_path, "rb") as f:
                    st.download_button(
                        label="📥 Click to Download PDF",
                        data=f,
                        file_name="AI_Expense_Report.pdf",
                        mime="application/pdf"
                    )

        else:
            st.warning("No data available")



    # ================= CHATBOT ================= #
    elif page == "Chatbot":
        st.subheader("🤖 Expense Chatbot")

        data = view_expense(user_id)

        if data:
            df = pd.DataFrame(data, columns=["Amount", "Category", "Date"])
            df["Date"] = pd.to_datetime(df["Date"])

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            if st.button("🧹 Clear Chat"):
                st.session_state.chat_history = []

            user_input = st.text_input("Ask something about your expenses:")

            if st.button("Ask") and user_input:

                # 🔥 AI LOGIC (NEW)
                intents = {
                    "total": ai_model.encode("total expense"),
                    "average": ai_model.encode("average spending"),
                    "most": ai_model.encode("highest spending category")
                }

                query_emb = ai_model.encode(user_input)

                scores = {
                    k: util.cos_sim(query_emb, v).item()
                    for k, v in intents.items()
                }

                best = max(scores, key=scores.get)

                if best == "total":
                    response = f"💰 Total ₹{df['Amount'].sum():.2f}"
                elif best == "average":
                    response = f"📊 Average ₹{df['Amount'].mean():.2f}"
                elif best == "most":
                    response = f"📈 Most spending on {df.groupby('Category')['Amount'].sum().idxmax()}"

                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("Bot", response))

            for s, m in st.session_state.chat_history:
                st.write(f"**{s}:** {m}")

        else:
            st.warning("No expense data found!")



