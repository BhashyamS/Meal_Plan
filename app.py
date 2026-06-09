import streamlit as st
import pandas as pd

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="Pooh Bear Yum Yum Tracker",
    page_icon="🐻",
    layout="wide"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #5C3B1E;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 18px;
        color: #7A5A32;
        margin-top: 0px;
    }
    .section-card {
        background-color: #FFF7E6;
        padding: 18px;
        border-radius: 18px;
        border: 1px solid #F4D28A;
        margin-bottom: 15px;
    }
    .meal-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 15px;
        border: 1px solid #E8D8B8;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
client = {
    "name": "Pooh Bear",
    "goal": "Lean Bulk",
    "height": "6'0",
    "weight": "180 lb",
    "age": 27,
    "daily_calorie_target": "3,600–4,000",
    "daily_protein_target": "180–220g",
    "weekly_budget": 150,
    "constraints": "Driving job, mini fridge only, low prep, lower sugar/sodium"
}

meal_plan = [
    {
        "Day": "Monday",
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
        "Breakfast": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
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
    {"Item": "Rotisserie chicken", "Quantity": "2 chickens, buy every 2–3 days", "Storage": "Mini fridge", "Estimated Cost": 10},
    {"Item": "Rice cups or whole wheat bread", "Quantity": "1 pack", "Storage": "Room temp", "Estimated Cost": 5},
]

df = pd.DataFrame(meal_plan)
monthly_df = pd.DataFrame(monthly_grocery)
weekly_df = pd.DataFrame(weekly_grocery)

# -----------------------------
# Header
# -----------------------------
st.markdown('<p class="main-title">🐻 Pooh Bear Yum Yum Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">A dynamic lean-bulk meal plan dashboard for a busy client on the road.</p>', unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🐝 Client Controls")

selected_day = st.sidebar.selectbox(
    "Choose a day",
    df["Day"].tolist()
)

budget_limit = st.sidebar.number_input(
    "Weekly Budget Goal ($)",
    min_value=50,
    max_value=500,
    value=client["weekly_budget"],
    step=5
)

st.sidebar.markdown("---")
st.sidebar.write("**Client Goal:**", client["goal"])
st.sidebar.write("**Constraint:** Mini fridge only")
st.sidebar.write("**Priority:** Budget + convenience")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "📅 Weekly Plan",
    "🍽️ Day Details",
    "🛒 Grocery List",
    "💰 Budget"
])

# -----------------------------
# Overview Tab
# -----------------------------
with tab1:
    st.subheader("Client Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Goal", client["goal"])
    col2.metric("Calories", client["daily_calorie_target"])
    col3.metric("Protein", client["daily_protein_target"])
    col4.metric("Budget", f"${budget_limit}/week")

    st.markdown("### Client Profile")
    st.markdown(f"""
    <div class="section-card">
    <b>Name:</b> {client['name']}<br>
    <b>Age:</b> {client['age']}<br>
    <b>Height:</b> {client['height']}<br>
    <b>Weight:</b> {client['weight']}<br>
    <b>Notes:</b> {client['constraints']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Plan Strategy")
    st.write(
        "This plan uses low-prep, road-friendly meals with high-calorie breakfast, "
        "handheld lunches, compact mini-fridge groceries, and easy dinners based around "
        "rotisserie chicken. The plan avoids relying heavily on high-sugar foods and tries "
        "to reduce sodium by limiting deli meats, fast food, and processed sides."
    )

# -----------------------------
# Weekly Plan Tab
# -----------------------------
with tab2:
    st.subheader("Weekly Meal Plan")

    display_df = df[["Day", "Breakfast", "Lunch", "Snack", "Dinner", "Calories", "Protein_g", "Cost"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("### Weekly Totals")
    col1, col2, col3 = st.columns(3)
    col1.metric("Weekly Calories", f"{df['Calories'].sum():,}")
    col2.metric("Weekly Protein", f"{df['Protein_g'].sum():,}g")
    col3.metric("Weekly Cost", f"${df['Cost'].sum():.2f}")

# -----------------------------
# Day Details Tab
# -----------------------------
with tab3:
    st.subheader(f"{selected_day} Meal Details")

    day_data = df[df["Day"] == selected_day].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{day_data['Calories']:,}")
    col2.metric("Protein", f"{day_data['Protein_g']}g")
    col3.metric("Carbs", f"{day_data['Carbs_g']}g")
    col4.metric("Fat", f"{day_data['Fat_g']}g")

    st.metric("Estimated Cost", f"${day_data['Cost']:.2f}")

    meals = {
        "Breakfast": day_data["Breakfast"],
        "Lunch": day_data["Lunch"],
        "Snack": day_data["Snack"],
        "Dinner": day_data["Dinner"]
    }

    for meal_name, meal_text in meals.items():
        with st.expander(f"{meal_name}: {meal_text}", expanded=True):
            if meal_name == "Breakfast":
                st.write("Built around protein coffee, peanut butter bagel, banana, and boiled eggs.")
                st.write("Purpose: high-calorie start, strong protein, low prep.")
            elif meal_name == "Lunch":
                st.write("Road-friendly and handheld where possible.")
                st.write("Purpose: easy to eat while driving or during a short break.")
            elif meal_name == "Snack":
                st.write("Portable calories to prevent under-eating.")
                st.write("Purpose: help hit calorie goal without a messy meal.")
            else:
                st.write("Dinner uses rotisserie chicken because it is easier to eat at home.")
                st.write("Purpose: cheap high-protein meal with simple carbs.")

# -----------------------------
# Grocery List Tab
# -----------------------------
with tab4:
    st.subheader("Monthly Costco Purchase")
    st.dataframe(monthly_df, use_container_width=True, hide_index=True)

    st.subheader("Weekly Grocery Refill")
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)

    st.markdown("### Mini Fridge Priority")
    st.write(
        "Keep fridge space for milk, Greek yogurt, boiled eggs, and the current rotisserie chicken. "
        "Store whey, bagels, peanut butter, bananas, granola, trail mix, protein bars, rice cups, "
        "and bread outside the fridge."
    )

# -----------------------------
# Budget Tab
# -----------------------------
with tab5:
    st.subheader("Budget Summary")

    weekly_food_cost = df["Cost"].sum()
    remaining = budget_limit - weekly_food_cost
    progress = min(weekly_food_cost / budget_limit, 1.0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Weekly Meal Cost", f"${weekly_food_cost:.2f}")
    col2.metric("Budget Goal", f"${budget_limit:.2f}")
    col3.metric("Remaining", f"${remaining:.2f}")

    st.progress(progress)

    if weekly_food_cost <= budget_limit:
        st.success("The plan is within the weekly budget. Pooh Bear's honey pot is safe. 🍯")
    else:
        st.error("The plan is over budget. Swap one restaurant lunch for a grocery sandwich or rotisserie chicken meal.")

    st.markdown("### Budget Notes")
    st.write("""
    To lower the weekly cost:
    - Replace Jersey Mike's with a grocery store deli sandwich.
    - Replace Vitality Bowl with Subway or a grocery sandwich.
    - Use whey protein instead of ready-to-drink shakes.
    - Buy rotisserie chicken every 2–3 days instead of storing multiple chickens.
    """)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Pooh Bear Yum Yum Tracker • Lean bulk meal planning dashboard • Built with Streamlit")