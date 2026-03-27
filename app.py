import streamlit as st
import pandas as pd
import json
import os
from scraper import search_web
from processor import build_prompt
from llm import generate_response

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="AI Market Research Assistant",
    layout="wide"
)

# ---------------- FILES ---------------- #
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"
LOGO_FILE = "logo.png"

# ---------------- STORAGE HELPERS ---------------- #
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"admin": "1234"}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# ---------------- CSS ---------------- #
st.markdown("""
<style>
.stApp {
    background-color: #f6f8fc;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem;
}

header { visibility: hidden; }
footer { visibility: hidden; }

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #17376e;
    margin-bottom: 2px;
    line-height: 1.15;
}

.subtitle {
    font-size: 17px;
    color: #4b5563;
    margin-bottom: 18px;
}

div[data-baseweb="input"] > div {
    background-color: white !important;
    border-radius: 12px !important;
    border: 1px solid #dbe3ef !important;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

.menu-btn button {
    font-size: 22px !important;
    font-weight: 700 !important;
    padding: 0.3rem 0.7rem !important;
    width: auto !important;
    min-width: 52px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"

if "current_report" not in st.session_state:
    st.session_state.current_report = None

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

for key in ["idea_input", "region_input", "segment_input"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ---------------- HELPERS ---------------- #
def show_logo(width=80):
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=width)

def render_header(subtitle_text):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<div class="main-title">AI-Powered Market Research Assistant</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="subtitle">{subtitle_text}</div>', unsafe_allow_html=True)
    with col2:
        show_logo(80)

def render_menu_toggle():
    col_btn, _ = st.columns([1, 20])
    with col_btn:
        st.markdown('<div class="menu-btn">', unsafe_allow_html=True)
        if st.button("≡", key="menu_toggle"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def planning_agent(idea, region, segment):
    return {
        "market_size": f"{idea} market size in {region}",
        "competitors": f"{idea} competitors in {region}",
        "pricing_models": f"{idea} pricing models in {region}",
        "pain_points": f"{idea} customer pain points in {region} for {segment}",
        "income": f"{idea} revenue model income opportunities in {region}",
        "investment": f"{idea} startup investment needs in {region}"
    }

def search_agent(query_dict):
    all_results = []
    for _, query in query_dict.items():
        all_results.extend(search_web(query))
    return all_results

def analysis_agent(data, idea, region, segment):
    return build_prompt(data, idea, region, segment)

def reasoning_agent(prompt):
    return generate_response(prompt)

def safe_parse_json(result_text):
    cleaned = result_text.strip().replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        return {
            "market_overview": parsed.get("market_overview", ""),
            "competitors": parsed.get("competitors", []),
            "pricing_models": parsed.get("pricing_models", []),
            "customer_pain_points": parsed.get("customer_pain_points", []),
            "entry_strategy": parsed.get("entry_strategy", []),
            "income_opportunities": parsed.get("income_opportunities", []),
            "investment_needs": parsed.get("investment_needs", [])
        }
    except Exception:
        return {
            "market_overview": cleaned,
            "competitors": [],
            "pricing_models": [],
            "customer_pain_points": [],
            "entry_strategy": [],
            "income_opportunities": [],
            "investment_needs": []
        }

def save_search_history(username, idea, region, segment, report):
    history = load_history()
    if username not in history:
        history[username] = []

    item = {
        "title": idea,
        "region": region,
        "segment": segment,
        "report": report
    }

    if not history[username] or history[username][0] != item:
        history[username].insert(0, item)

    history[username] = history[username][:10]
    save_history(history)

def get_user_history(username):
    return load_history().get(username, [])

def start_new_chat():
    st.session_state.current_report = None
    st.session_state.idea_input = ""
    st.session_state.region_input = ""
    st.session_state.segment_input = ""

def load_history_item(item):
    st.session_state.current_report = item["report"]
    st.session_state.idea_input = item["title"]
    st.session_state.region_input = item["region"]
    st.session_state.segment_input = item["segment"]

def score_df(items, label_col):
    if not items:
        return None
    return pd.DataFrame({
        label_col: items,
        "Score": list(range(len(items), 0, -1))
    })

# ---------------- PURE STREAMLIT SIDEBAR PANEL ---------------- #
def render_left_panel(username):
    user_history = get_user_history(username)

    st.title("AI Research")

    if st.button("➕ New Chat", key="new_chat_btn"):
        start_new_chat()
        st.rerun()

    st.divider()
    st.write(f"**Account:** {username}")

    st.divider()
    st.subheader("Previous Searches")

    if user_history:
        for i, item in enumerate(user_history):
            label = f"{item['title']} ({item['region']})"
            if st.button(label, key=f"hist_{i}"):
                load_history_item(item)
                st.rerun()
    else:
        st.caption("No previous searches yet.")

    st.divider()

    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_report = None
        st.session_state.auth_view = "login"
        st.rerun()

# ---------------- AUTH PAGE ---------------- #
def show_auth_page():
    render_menu_toggle()
    render_header("Login or register to access your dashboard")

    left, center, right = st.columns([2, 3, 2])

    with center:
        c1, c2 = st.columns(2)

        with c1:
            if st.button("Login View"):
                st.session_state.auth_view = "login"

        with c2:
            if st.button("Register View"):
                st.session_state.auth_view = "register"

        st.write("")

        if st.session_state.auth_view == "login":
            st.subheader("Login")
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", key="login_pass", type="password", placeholder="Enter password")

            if st.button("Login", key="login_btn"):
                users = load_users()
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        else:
            st.subheader("Register")
            new_username = st.text_input("Create Username", key="reg_user", placeholder="Choose username")
            new_password = st.text_input("Create Password", key="reg_pass", type="password", placeholder="Choose password")
            confirm_password = st.text_input("Confirm Password", key="reg_confirm", type="password", placeholder="Re-enter password")

            if st.button("Register", key="register_btn"):
                users = load_users()
                if not new_username or not new_password or not confirm_password:
                    st.warning("Please fill all fields.")
                elif new_username in users:
                    st.error("Username already exists.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    users[new_username] = new_password
                    save_users(users)
                    st.success("Registration successful. Now login.")

# ---------------- DASHBOARD ---------------- #
def show_dashboard():
    username = st.session_state.current_user
    render_menu_toggle()

    if st.session_state.sidebar_open:
        sidebar_col, main_col = st.columns([1.3, 4.7], gap="medium")
        with sidebar_col:
            render_left_panel(username)
        with main_col:
            render_dashboard_main(username)
    else:
        render_dashboard_main(username)

def render_dashboard_main(username):
    render_header("Generate structured market insights with AI")

    # ---------------- INPUT SECTION ---------------- #
    st.subheader("Startup Inputs")

    st.text_input("Startup Idea", key="idea_input", placeholder="e.g. Food Delivery Startup")
    st.text_input("Target Region", key="region_input", placeholder="e.g. India")
    st.text_input("Customer Segment", key="segment_input", placeholder="e.g. Students")

    if st.button("Generate Report"):
        idea = st.session_state.idea_input.strip()
        region = st.session_state.region_input.strip()
        segment = st.session_state.segment_input.strip()

        if not idea or not region or not segment:
            st.warning("Please fill all fields.")
        else:
            with st.spinner("Generating market research report..."):
                queries = planning_agent(idea, region, segment)
                scraped_data = search_agent(queries)
                prompt = analysis_agent(scraped_data, idea, region, segment)
                result = reasoning_agent(prompt)
                parsed = safe_parse_json(result)

                st.session_state.current_report = parsed
                save_search_history(username, idea, region, segment, parsed)
                st.rerun()

    report = st.session_state.current_report

    # ---------------- REPORT SECTION ---------------- #
    if report:
        st.markdown("---")

        # ---------- METRICS ---------- #
        col1, col2 = st.columns(2)
        col1.metric("💰 Income Opportunities", len(report.get("income_opportunities", [])))
        col2.metric("📈 Investment Needs", len(report.get("investment_needs", [])))

        st.markdown("---")

        # ---------- MARKET OVERVIEW ---------- #
        st.subheader("1. Market Overview")
        st.info(report.get("market_overview", "Not available"))

        st.markdown("---")

        # ---------- COMPETITOR GRAPH ---------- #
        st.subheader("2. Competitor Landscape")
        competitors = report.get("competitors", [])

        if competitors:
            comp_df = pd.DataFrame({
                "Competitor": competitors,
                "Score": list(range(len(competitors), 0, -1))
            })
            st.bar_chart(comp_df.set_index("Competitor"))
        else:
            st.write("No competitor data available.")

        st.markdown("---")

        # ---------- MARKET SUMMARY ---------- #
        st.subheader("3. Market Summary")
        st.write(report.get("market_overview", "Not available"))

        st.markdown("---")

        # ---------- LIST SECTIONS ---------- #
        def render_list(title, items):
            st.subheader(title)
            if items:
                for item in items:
                    st.markdown(f"- {item}")
            else:
                st.write("No data available.")
            st.markdown("---")

        render_list("4. Competitors", competitors)
        render_list("5. Pricing Models", report.get("pricing_models", []))
        render_list("6. Customer Pain Points", report.get("customer_pain_points", []))
        render_list("7. Entry Strategy", report.get("entry_strategy", []))
        render_list("8. Income Opportunities", report.get("income_opportunities", []))
        render_list("9. Investment Needs", report.get("investment_needs", []))

        # ---------- GRAPHS ---------- #
        st.subheader("Income vs Investment Analysis")

        g1, g2 = st.columns(2)

        income_df = score_df(report.get("income_opportunities", []), "Income")
        invest_df = score_df(report.get("investment_needs", []), "Investment")

        with g1:
            st.markdown("**Income Opportunities**")
            if income_df is not None:
                st.bar_chart(income_df.set_index("Income"))
            else:
                st.write("No data")

        with g2:
            st.markdown("**Investment Needs**")
            if invest_df is not None:
                st.bar_chart(invest_df.set_index("Investment"))
            else:
                st.write("No data")

# ---------------- MAIN ---------------- #
if st.session_state.logged_in:
    show_dashboard()
else:
    show_auth_page()