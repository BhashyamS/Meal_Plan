import random
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pooh Bear Yum Yum Tracker",
    page_icon="🐻",
    layout="wide"
)

# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 46px;
        font-weight: 900;
        color: #F4C542;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #E8D8B8;
        margin-top: 0px;
        margin-bottom: 25px;
    }

    .section-card {
        background: linear-gradient(135deg, #FFF7E6, #FCEFCB);
        color: #3B2A1A;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #F4D28A;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 16px;
        font-size: 17px;
        line-height: 1.7;
    }

    .section-card h3 {
        color: #5C3B1E;
        margin-top: 0;
    }

    .meal-card {
        background: #FFF7E6;
        color: #3B2A1A;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #F4D28A;
        margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .meal-card h4 {
        margin-top: 0;
        color: #5C3B1E;
    }

    .note-box {
        background: #1E1E1E;
        border-left: 5px solid #F4C542;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    .small-muted {
        color: #B8B8B8;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Client Data
# ---------------------------------------------------------
client = {
    "name": "Pooh Bear",
    "prepared_by": "Srija Bhashyam",
    "plan_type": "Lean Bulk",
    "age": 27,
    "height": "6'0",
    "weight": "180 lb",
    "calorie_target": "3,600–4,000/day",
    "protein_target": "180–220g/day",
    "weekly_budget": 150,
    "lifestyle": "Driving job, mini fridge only, no kitchen, low-prep meals",
    "nutrition_focus": "High protein, balanced calories, lower sugar, lower sodium where possible"
}

meal_plan = [
    {
        "Day": "Monday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Subway Footlong Turkey",
        "Snack": "Greek yogurt + granola + trail mix",
        "Dinner": "Rotisserie chicken + whole wheat bagel",
        "Calories": 3650,
        "Protein_g": 225,
        "Carbs_g": 360,
        "Fat_g": 120,
        "Cost": 21.00
    },
    {
        "Day": "Tuesday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Grocery store deli sandwich + protein bar",
        "Snack": "Trail mix + banana",
        "Dinner": "Rotisserie chicken + rice cup",
        "Calories": 3550,
        "Protein_g": 210,
        "Carbs_g": 350,
        "Fat_g": 115,
        "Cost": 18.50
    },
    {
        "Day": "Wednesday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Vitality Bowl protein wrap + protein bar",
        "Snack": "Greek yogurt + granola",
        "Dinner": "Rotisserie chicken + whole wheat bread",
        "Calories": 3600,
        "Protein_g": 205,
        "Carbs_g": 370,
        "Fat_g": 110,
        "Cost": 24.00
    },
    {
        "Day": "Thursday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Subway Footlong Rotisserie Chicken",
        "Snack": "Trail mix + banana",
        "Dinner": "Rotisserie chicken + whole wheat bagel",
        "Calories": 3750,
        "Protein_g": 230,
        "Carbs_g": 380,
        "Fat_g": 120,
        "Cost": 22.00
    },
    {
        "Day": "Friday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Grocery store turkey sandwich + protein bar",
        "Snack": "Greek yogurt + granola",
        "Dinner": "Rotisserie chicken + rice cup",
        "Calories": 3500,
        "Protein_g": 210,
        "Carbs_g": 345,
        "Fat_g": 105,
        "Cost": 18.00
    },
    {
        "Day": "Saturday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Jersey Mike's Giant Turkey Sub",
        "Snack": "Trail mix + banana",
        "Dinner": "Rotisserie chicken + whole wheat bagel",
        "Calories": 3900,
        "Protein_g": 235,
        "Carbs_g": 410,
        "Fat_g": 125,
        "Cost": 25.00
    },
    {
        "Day": "Sunday",
        "Breakfast": "Protein iced coffee + peanut butter bagel + banana + 2 boiled eggs",
        "Lunch": "Grocery store sandwich + protein bar",
        "Snack": "Greek yogurt + granola + trail mix",
        "Dinner": "Rotisserie chicken + whole wheat bread",
        "Calories": 3550,
        "Protein_g": 215,
        "Carbs_g": 355,
        "Fat_g": 110,
        "Cost": 19.00
    },
]

monthly_grocery = [
    {"Item": "Whey protein", "Quantity": "1 large Costco tub", "Storage": "Room temp", "Estimated Cost": 60},
    {"Item": "Peanut butter", "Quantity": "1–2 large jars", "Storage": "Room temp", "Estimated Cost": 10},
    {"Item": "Trail mix", "Quantity": "1 large bag", "Storage": "Room temp", "Estimated Cost": 15},
    {"Item": "Protein bars", "Quantity": "1 box", "Storage": "Room temp", "Estimated Cost": 20},
    {"Item": "Granola", "Quantity": "1 large bag", "Storage": "Room temp", "Estimated Cost": 8},
]

weekly_grocery = [
    {"Item": "Whole milk", "Quantity": "1–2 gallons", "Storage": "Mini fridge", "Estimated Cost": 8},
    {"Item": "Bagels", "Quantity": "2 packs", "Storage": "Room temp", "Estimated Cost": 8},
    {"Item": "Bananas", "Quantity": "10–14", "Storage": "Room temp", "Estimated Cost": 4},
    {"Item": "Greek yogurt", "Quantity": "1 pack/tub", "Storage": "Mini fridge", "Estimated Cost": 8},
    {"Item": "Pre-boiled eggs", "Quantity": "1 pack", "Storage": "Mini fridge", "Estimated Cost": 7},
    {"Item": "Rotisserie chicken", "Quantity": "2 chickens; buy every 2–3 days", "Storage": "Mini fridge", "Estimated Cost": 10},
    {"Item": "Rice cups / whole wheat bread", "Quantity": "1 pack", "Storage": "Room temp", "Estimated Cost": 5},
]

swap_options = [
    {"Swap": "Replace Jersey Mike's with grocery sandwich", "Savings": 8, "Impact": "Lower cost, slightly less protein"},
    {"Swap": "Replace Vitality Bowl with Subway", "Savings": 1, "Impact": "More protein, similar cost"},
    {"Swap": "Replace protein bar with boiled eggs", "Savings": 0.50, "Impact": "Less processed, lower sugar"},
    {"Swap": "Use rice cup instead of bread", "Savings": 0, "Impact": "Lower sodium option"},
]

df = pd.DataFrame(meal_plan)
monthly_df = pd.DataFrame(monthly_grocery)
weekly_df = pd.DataFrame(weekly_grocery)
swap_df = pd.DataFrame(swap_options)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("🐻 Pooh Controls")

selected_day = st.sidebar.selectbox("Select Day", df["Day"].tolist())

budget_limit = st.sidebar.number_input(
    "Weekly Budget Goal ($)",
    min_value=50,
    max_value=500,
    value=client["weekly_budget"],
    step=5
)

quotes = [
    "🍯 When in doubt, eat the bagel.",
    "💪 A bear who skips protein skips gains.",
    "🐻 Small fridge. Big goals.",
    "🥜 Peanut butter is the budget bulk king.",
    "🚗 Road meals can still build muscle."
]
st.sidebar.info(random.choice(quotes))

st.sidebar.markdown("---")
st.sidebar.write("**Goal:** Lean Bulk")
st.sidebar.write("**Budget:** $150/week")
st.sidebar.write("**Setup:** Mini fridge only")

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown('<p class="main-title">🐻 Pooh Bear Yum Yum Tracker</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Dynamic client meal plan report for lean bulking on the road, with mini-fridge-friendly groceries and budget tracking.</p>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "📅 Weekly Plan",
    "🍽️ Day Details",
    "🛒 Grocery List",
    "💰 Budget"
])

# ---------------------------------------------------------
# Overview
# ---------------------------------------------------------
with tab1:
    st.subheader("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Goal", client["plan_type"])
    col2.metric("Calories", client["calorie_target"])
    col3.metric("Protein", client["protein_target"])
    col4.metric("Budget", f"${budget_limit}/week")

    st.markdown(f"""
    <div class="section-card">
        <h3>🐻 Client Information</h3>
        <b>Name:</b> {client['name']}<br>
        <b>Age:</b> {client['age']}<br>
        <b>Height:</b> {client['height']}<br>
        <b>Weight:</b> {client['weight']}<br>
        <b>Prepared By:</b> {client['prepared_by']}<br>
        <b>Lifestyle:</b> {client['lifestyle']}<br>
        <b>Nutrition Focus:</b> {client['nutrition_focus']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Plan Strategy")
    st.markdown("""
    <div class="note-box">
    This plan is built around a consistent high-protein breakfast, handheld road-friendly lunches,
    portable snacks, and easy dinners based around rotisserie chicken. The grocery strategy protects
    mini-fridge space by keeping most items shelf-stable: whey, bagels, peanut butter, bananas,
    trail mix, granola, and protein bars.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Nutrition Guardrails")
    st.write(
        "The plan avoids making high-sugar foods the foundation. Hawaiian rolls and pizza are not used as daily staples. "
        "Sodium is managed by rotating restaurant meals with grocery sandwiches, rice cups, whole wheat bread, and rotisserie chicken."
    )

# ---------------------------------------------------------
# Weekly Plan
# ---------------------------------------------------------
with tab2:
    st.subheader("Weekly Meal Plan")

    display_df = df[[
        "Day", "Breakfast", "Lunch", "Snack", "Dinner",
        "Calories", "Protein_g", "Carbs_g", "Fat_g", "Cost"
    ]]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("### Weekly Nutrition Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Calories", f"{df['Calories'].sum():,}")
    col2.metric("Protein", f"{df['Protein_g'].sum():,}g")
    col3.metric("Carbs", f"{df['Carbs_g'].sum():,}g")
    col4.metric("Fat", f"{df['Fat_g'].sum():,}g")
    col5.metric("Cost", f"${df['Cost'].sum():.2f}")

    st.markdown("### Average Per Day")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Calories", f"{df['Calories'].mean():,.0f}")
    col2.metric("Avg Protein", f"{df['Protein_g'].mean():.0f}g")
    col3.metric("Avg Cost", f"${df['Cost'].mean():.2f}")

# ---------------------------------------------------------
# Day Details
# ---------------------------------------------------------
with tab3:
    day_data = df[df["Day"] == selected_day].iloc[0]

    st.subheader(f"{selected_day} Meal Details")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Calories", f"{day_data['Calories']:,}")
    col2.metric("Protein", f"{day_data['Protein_g']}g")
    col3.metric("Carbs", f"{day_data['Carbs_g']}g")
    col4.metric("Fat", f"{day_data['Fat_g']}g")
    col5.metric("Cost", f"${day_data['Cost']:.2f}")

    meal_notes = {
        "Breakfast": "High-protein, high-calorie start with whey, milk, peanut butter, eggs, and fruit.",
        "Lunch": "Designed to be road-friendly, handheld, and less messy than rice bowls.",
        "Snack": "Portable calories to prevent under-eating during a driving shift.",
        "Dinner": "Rotisserie chicken is saved for dinner because it is easier to eat at home."
    }

    for meal_name in ["Breakfast", "Lunch", "Snack", "Dinner"]:
        st.markdown(f"""
        <div class="meal-card">
            <h4>{meal_name}</h4>
            <b>{day_data[meal_name]}</b><br><br>
            {meal_notes[meal_name]}
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Grocery List
# ---------------------------------------------------------
with tab4:
    st.subheader("Monthly Costco Buy — 1st of the Month")
    st.dataframe(monthly_df, use_container_width=True, hide_index=True)

    monthly_total = monthly_df["Estimated Cost"].sum()
    st.metric("Estimated Monthly Bulk Purchase", f"${monthly_total:.2f}")

    st.subheader("Weekly Refill List")
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)

    weekly_total = weekly_df["Estimated Cost"].sum()
    st.metric("Estimated Weekly Grocery Refill", f"${weekly_total:.2f}")

    st.markdown("### Mini Fridge Storage Plan")
    st.markdown("""
    <div class="section-card">
        <h3>🧊 What Goes in the Mini Fridge</h3>
        <b>Priority Items:</b> milk, Greek yogurt, boiled eggs, and the current rotisserie chicken.<br>
        <b>Do Not Waste Fridge Space On:</b> bagels, peanut butter, bananas, whey, trail mix, granola, protein bars, rice cups, or bread.<br>
        <b>Rotisserie Chicken Strategy:</b> Buy one chicken every 2–3 days instead of storing multiple chickens.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Budget
# ---------------------------------------------------------
with tab5:
    st.subheader("Honey Pot Budget Tracker 🍯")

    weekly_cost = df["Cost"].sum()
    remaining = budget_limit - weekly_cost
    progress = min(weekly_cost / budget_limit, 1.0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Projected Weekly Cost", f"${weekly_cost:.2f}")
    col2.metric("Budget Goal", f"${budget_limit:.2f}")
    col3.metric("Remaining", f"${remaining:.2f}")

    st.progress(progress)

    if weekly_cost <= budget_limit:
        st.success("Plan is within budget. Pooh Bear's honey pot is safe. 🍯")
    else:
        st.error("Plan is over budget. Use the swaps below to reduce weekly cost.")

    st.markdown("### Budget-Friendly Swaps")
    st.dataframe(swap_df, use_container_width=True, hide_index=True)

    st.markdown("### Cost Notes")
    st.write(
        "The biggest savings come from using whey protein instead of ready-to-drink shakes, "
        "buying peanut butter and trail mix in bulk, and limiting premium lunches like Jersey Mike's or Vitality Bowls."
    )

st.markdown("---")
st.caption("Pooh Bear Yum Yum Tracker • Dynamic meal plan report • Built with Streamlit")