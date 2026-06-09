import json
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None


# =========================================================
# Page Setup
# =========================================================
st.set_page_config(
    page_title="Pooh Bear Yum Yum Tracker",
    page_icon="🐻",
    layout="wide"
)

# =========================================================
# Styling
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 44px;
        font-weight: 900;
        color: #F4C542;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #E8D8B8;
        margin-top: 0px;
        margin-bottom: 24px;
    }

    .section-card {
        background: linear-gradient(135deg, #FFF7E6, #FCEFCB);
        color: #3B2A1A;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #F4D28A;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 16px;
        font-size: 16px;
        line-height: 1.7;
    }

    .section-card h3 {
        color: #5C3B1E;
        margin-top: 0;
    }

    .meal-card {
        background: #FFF7E6;
        color: #3B2A1A;
        padding: 16px;
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
</style>
""", unsafe_allow_html=True)


# =========================================================
# Client Profile
# =========================================================
CLIENT = {
    "name": "Pooh Bear",
    "prepared_by": "Srija Bhashyam",
    "goal": "Lean Bulk",
    "age": 27,
    "height": "6'0",
    "weight": "180 lb",
    "calorie_target": "3,600–4,000/day",
    "protein_target": "180–220g/day",
    "weekly_budget": 150,
    "lifestyle": "Driving job, mini fridge only, no kitchen, low-prep meals",
    "focus": "High protein, budget-conscious, lower sugar, lower sodium where possible"
}


# =========================================================
# Meal Option Data
# =========================================================
MEAL_OPTIONS = {
    "Breakfast": [
        {
            "name": "Protein iced coffee + PB bagel + banana + 2 boiled eggs",
            "calories": 1000,
            "protein": 75,
            "carbs": 95,
            "fat": 38,
            "cost": 4.50,
            "tags": "home, mini-fridge, lower sugar",
            "ingredients": {
                "Whey protein": 2,
                "Whole milk": 16,
                "Bagel": 1,
                "Peanut butter": 2,
                "Banana": 1,
                "Boiled eggs": 2
            }
        },
        {
            "name": "Protein iced coffee + PB bagel + banana",
            "calories": 850,
            "protein": 63,
            "carbs": 90,
            "fat": 30,
            "cost": 3.40,
            "tags": "home, fastest option",
            "ingredients": {
                "Whey protein": 2,
                "Whole milk": 16,
                "Bagel": 1,
                "Peanut butter": 2,
                "Banana": 1
            }
        },
        {
            "name": "Greek yogurt + granola + banana + protein coffee",
            "calories": 900,
            "protein": 72,
            "carbs": 105,
            "fat": 22,
            "cost": 4.80,
            "tags": "balanced, easy",
            "ingredients": {
                "Whey protein": 2,
                "Whole milk": 16,
                "Greek yogurt": 1,
                "Granola": 1,
                "Banana": 1
            }
        }
    ],
    "Lunch": [
        {
            "name": "Subway Footlong Turkey",
            "calories": 850,
            "protein": 60,
            "carbs": 95,
            "fat": 22,
            "cost": 12.00,
            "tags": "handheld, driving-friendly",
            "ingredients": {
                "Subway Footlong Turkey": 1
            }
        },
        {
            "name": "Subway Footlong Rotisserie Chicken",
            "calories": 900,
            "protein": 65,
            "carbs": 95,
            "fat": 25,
            "cost": 13.00,
            "tags": "handheld, driving-friendly",
            "ingredients": {
                "Subway Footlong Rotisserie Chicken": 1
            }
        },
        {
            "name": "Grocery store deli sandwich + protein bar",
            "calories": 900,
            "protein": 55,
            "carbs": 95,
            "fat": 30,
            "cost": 8.25,
            "tags": "budget, handheld",
            "ingredients": {
                "Grocery store deli sandwich": 1,
                "Protein bar": 1
            }
        },
        {
            "name": "Vitality Bowl protein wrap + protein bar",
            "calories": 900,
            "protein": 50,
            "carbs": 95,
            "fat": 28,
            "cost": 16.25,
            "tags": "client favorite, handheld",
            "ingredients": {
                "Vitality Bowl protein wrap": 1,
                "Protein bar": 1
            }
        },
        {
            "name": "Jersey Mike's Giant Turkey Sub",
            "calories": 1100,
            "protein": 70,
            "carbs": 120,
            "fat": 38,
            "cost": 15.00,
            "tags": "higher calorie, handheld",
            "ingredients": {
                "Jersey Mike's Giant Turkey Sub": 1
            }
        }
    ],
    "Snack": [
        {
            "name": "Greek yogurt + granola",
            "calories": 350,
            "protein": 20,
            "carbs": 45,
            "fat": 8,
            "cost": 2.00,
            "tags": "mini-fridge, lower sodium",
            "ingredients": {
                "Greek yogurt": 1,
                "Granola": 1
            }
        },
        {
            "name": "Trail mix + banana",
            "calories": 500,
            "protein": 10,
            "carbs": 65,
            "fat": 25,
            "cost": 1.50,
            "tags": "car snack, shelf-stable",
            "ingredients": {
                "Trail mix": 1,
                "Banana": 1
            }
        },
        {
            "name": "Protein bar",
            "calories": 200,
            "protein": 20,
            "carbs": 22,
            "fat": 6,
            "cost": 1.25,
            "tags": "backup snack",
            "ingredients": {
                "Protein bar": 1
            }
        },
        {
            "name": "Boiled eggs + banana",
            "calories": 300,
            "protein": 16,
            "carbs": 30,
            "fat": 11,
            "cost": 2.00,
            "tags": "lower sugar, mini-fridge",
            "ingredients": {
                "Boiled eggs": 2,
                "Banana": 1
            }
        }
    ],
    "Dinner": [
        {
            "name": "Rotisserie chicken + whole wheat bagel",
            "calories": 900,
            "protein": 75,
            "carbs": 70,
            "fat": 30,
            "cost": 4.00,
            "tags": "home, budget, high protein",
            "ingredients": {
                "Rotisserie chicken portion": 1,
                "Whole wheat bagel": 1
            }
        },
        {
            "name": "Rotisserie chicken + rice cup",
            "calories": 750,
            "protein": 70,
            "carbs": 55,
            "fat": 25,
            "cost": 4.00,
            "tags": "home, lower sodium carb option",
            "ingredients": {
                "Rotisserie chicken portion": 1,
                "Rice cup": 1
            }
        },
        {
            "name": "Rotisserie chicken + whole wheat bread",
            "calories": 850,
            "protein": 72,
            "carbs": 70,
            "fat": 28,
            "cost": 4.00,
            "tags": "home, simple",
            "ingredients": {
                "Rotisserie chicken portion": 1,
                "Whole wheat bread serving": 1
            }
        },
        {
            "name": "Grocery store wrap + boiled eggs",
            "calories": 850,
            "protein": 55,
            "carbs": 85,
            "fat": 30,
            "cost": 9.00,
            "tags": "backup dinner",
            "ingredients": {
                "Grocery store wrap": 1,
                "Boiled eggs": 2
            }
        }
    ]
}


MONTHLY_ITEMS = [
    {"Item": "Whey protein", "Quantity": "1 large Costco tub", "Storage": "Room temp", "Estimated Cost": 60},
    {"Item": "Peanut butter", "Quantity": "1–2 large jars", "Storage": "Room temp", "Estimated Cost": 10},
    {"Item": "Trail mix", "Quantity": "1 large Costco bag", "Storage": "Room temp", "Estimated Cost": 15},
    {"Item": "Protein bars", "Quantity": "1 box", "Storage": "Room temp", "Estimated Cost": 20},
    {"Item": "Granola", "Quantity": "1 large bag", "Storage": "Room temp", "Estimated Cost": 8},
]

WEEKLY_REFILL_ITEMS = [
    {"Item": "Whole milk", "Quantity": "1–2 gallons", "Storage": "Mini fridge", "Estimated Cost": 8},
    {"Item": "Bagels", "Quantity": "2 packs", "Storage": "Room temp", "Estimated Cost": 8},
    {"Item": "Bananas", "Quantity": "10–14", "Storage": "Room temp", "Estimated Cost": 4},
    {"Item": "Greek yogurt", "Quantity": "1 pack/tub", "Storage": "Mini fridge", "Estimated Cost": 8},
    {"Item": "Pre-boiled eggs", "Quantity": "1 pack", "Storage": "Mini fridge", "Estimated Cost": 7},
    {"Item": "Rotisserie chicken", "Quantity": "Buy one every 2–3 days", "Storage": "Mini fridge", "Estimated Cost": 10},
    {"Item": "Rice cups / whole wheat bread", "Quantity": "1 pack", "Storage": "Room temp", "Estimated Cost": 5},
]


# =========================================================
# Google Sheets Helpers
# =========================================================
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def google_sheets_is_configured():
    return (
        gspread is not None
        and Credentials is not None
        and "gcp_service_account" in st.secrets
        and "spreadsheet_name" in st.secrets
    )

@st.cache_resource(show_spinner=False)
def get_spreadsheet():
    if not google_sheets_is_configured():
        return None

    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    client = gspread.authorize(credentials)

    spreadsheet_name = st.secrets["spreadsheet_name"]

    try:
        return client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        return client.create(spreadsheet_name)

def get_or_create_worksheet(spreadsheet, title, headers):
    try:
        worksheet = spreadsheet.worksheet(title)
    except Exception:
        worksheet = spreadsheet.add_worksheet(title=title, rows=1000, cols=max(20, len(headers)))
        worksheet.append_row(headers)
        return worksheet

    existing_values = worksheet.get_all_values()
    if len(existing_values) == 0:
        worksheet.append_row(headers)
    return worksheet

def read_saved_logs():
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return pd.DataFrame()

    headers = [
        "saved_at", "week_start", "day", "meal_slot", "meal_name",
        "calories", "protein", "carbs", "fat", "cost", "ingredients_json"
    ]
    worksheet = get_or_create_worksheet(spreadsheet, "Daily_Logs", headers)
    records = worksheet.get_all_records()

    if not records:
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(records)
    for col in ["calories", "protein", "carbs", "fat", "cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def save_week_to_sheets(week_start, selected_rows):
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False, "Google Sheets is not connected yet."

    headers = [
        "saved_at", "week_start", "day", "meal_slot", "meal_name",
        "calories", "protein", "carbs", "fat", "cost", "ingredients_json"
    ]
    worksheet = get_or_create_worksheet(spreadsheet, "Daily_Logs", headers)

    existing = worksheet.get_all_records()
    existing_df = pd.DataFrame(existing)

    week_start_str = str(week_start)

    if not existing_df.empty and "week_start" in existing_df.columns:
        existing_df = existing_df[existing_df["week_start"].astype(str) != week_start_str]

    new_df = pd.DataFrame(selected_rows)
    combined = pd.concat([existing_df, new_df], ignore_index=True) if not existing_df.empty else new_df

    worksheet.clear()
    worksheet.append_row(headers)

    if not combined.empty:
        rows = combined[headers].values.tolist()
        worksheet.append_rows(rows)

    return True, "Weekly plan saved to Google Sheets."


# =========================================================
# Calculation Helpers
# =========================================================
def week_start_for(selected_date):
    selected_date = pd.to_datetime(selected_date).date()
    return selected_date - timedelta(days=selected_date.weekday())

def get_week_days(week_start_date):
    return [week_start_date + timedelta(days=i) for i in range(7)]

def flatten_selection(selections, week_start):
    rows = []
    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for day_name, day_data in selections.items():
        for meal_slot, meal in day_data.items():
            if meal:
                rows.append({
                    "saved_at": saved_at,
                    "week_start": str(week_start),
                    "day": day_name,
                    "meal_slot": meal_slot,
                    "meal_name": meal["name"],
                    "calories": meal["calories"],
                    "protein": meal["protein"],
                    "carbs": meal["carbs"],
                    "fat": meal["fat"],
                    "cost": meal["cost"],
                    "ingredients_json": json.dumps(meal["ingredients"])
                })
    return rows

def calculate_day_totals(day_data):
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0}
    for meal in day_data.values():
        if meal:
            totals["calories"] += meal["calories"]
            totals["protein"] += meal["protein"]
            totals["carbs"] += meal["carbs"]
            totals["fat"] += meal["fat"]
            totals["cost"] += meal["cost"]
    return totals

def calculate_week_totals(selections):
    daily_rows = []
    for day_name, day_data in selections.items():
        totals = calculate_day_totals(day_data)
        daily_rows.append({
            "Day": day_name,
            "Calories": totals["calories"],
            "Protein": totals["protein"],
            "Carbs": totals["carbs"],
            "Fat": totals["fat"],
            "Cost": totals["cost"]
        })
    return pd.DataFrame(daily_rows)

def build_grocery_list(selections):
    grocery = {}

    for day_data in selections.values():
        for meal in day_data.values():
            if meal:
                for ingredient, qty in meal["ingredients"].items():
                    grocery[ingredient] = grocery.get(ingredient, 0) + qty

    grocery_rows = []
    for ingredient, qty in grocery.items():
        grocery_rows.append({
            "Item": ingredient,
            "Estimated Weekly Amount": qty
        })

    return pd.DataFrame(grocery_rows).sort_values("Item") if grocery_rows else pd.DataFrame(columns=["Item", "Estimated Weekly Amount"])

def meal_by_name(slot, meal_name):
    for meal in MEAL_OPTIONS[slot]:
        if meal["name"] == meal_name:
            return meal
    return None

def load_saved_week_defaults(week_start):
    saved = read_saved_logs()
    if saved.empty:
        return {}

    week_df = saved[saved["week_start"].astype(str) == str(week_start)]
    defaults = {}

    for _, row in week_df.iterrows():
        defaults[(row["day"], row["meal_slot"])] = row["meal_name"]

    return defaults


# =========================================================
# Header
# =========================================================
st.markdown('<p class="main-title">🐻 Pooh Bear Yum Yum Tracker</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Client meal plan tracker with dynamic macros, budget, grocery list, and Google Sheets history.</p>',
    unsafe_allow_html=True
)


# =========================================================
# Sidebar Controls
# =========================================================
st.sidebar.title("🐝 Client Controls")

selected_date = st.sidebar.date_input("Choose week", value=date.today())
week_start = week_start_for(selected_date)
week_days = get_week_days(week_start)

budget_limit = st.sidebar.number_input(
    "Weekly Budget Goal ($)",
    min_value=50,
    max_value=500,
    value=CLIENT["weekly_budget"],
    step=5
)

st.sidebar.markdown("---")
if google_sheets_is_configured():
    st.sidebar.success("Google Sheets connected")
else:
    st.sidebar.warning("Google Sheets not connected yet")
    st.sidebar.caption("The app still works, but saved data will not persist after refresh/deploy restart.")

st.sidebar.markdown("---")
st.sidebar.info("🍯 When in doubt, eat the bagel.")


# =========================================================
# Load Saved Defaults
# =========================================================
saved_defaults = {}
if google_sheets_is_configured():
    try:
        saved_defaults = load_saved_week_defaults(week_start)
    except Exception as e:
        st.sidebar.error("Could not load saved Google Sheets data.")
        st.sidebar.caption(str(e))


# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "✅ Meal Picker",
    "📊 Weekly Summary",
    "🛒 Grocery List",
    "📅 30-Day History"
])


# =========================================================
# Overview
# =========================================================
with tab1:
    st.subheader("Client Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Goal", CLIENT["goal"])
    col2.metric("Calories", CLIENT["calorie_target"])
    col3.metric("Protein", CLIENT["protein_target"])
    col4.metric("Budget", f"${budget_limit}/week")

    st.markdown(f"""
    <div class="section-card">
        <h3>🐻 Client Information</h3>
        <b>Name:</b> {CLIENT['name']}<br>
        <b>Age:</b> {CLIENT['age']}<br>
        <b>Height:</b> {CLIENT['height']}<br>
        <b>Weight:</b> {CLIENT['weight']}<br>
        <b>Prepared By:</b> {CLIENT['prepared_by']}<br>
        <b>Lifestyle:</b> {CLIENT['lifestyle']}<br>
        <b>Nutrition Focus:</b> {CLIENT['focus']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### How This Tracker Works")
    st.write(
        "The client chooses meal options for each day. The app updates calories, protein, carbs, fats, cost, "
        "weekly averages, grocery needs, and budget remaining automatically. When Google Sheets is connected, "
        "the weekly plan can be saved and reviewed later."
    )


# =========================================================
# Meal Picker
# =========================================================
selections = {}

with tab2:
    st.subheader(f"Meal Picker: Week of {week_start.strftime('%b %d, %Y')}")
    st.caption("Pick one option per meal. Totals update automatically.")

    for i, day_date in enumerate(week_days):
        day_name = day_date.strftime("%A")
        display_label = f"{day_name} — {day_date.strftime('%b %d')}"
        selections[day_name] = {}

        with st.expander(display_label, expanded=(i == 0)):
            for slot in ["Breakfast", "Lunch", "Snack", "Dinner"]:
                options = ["None"] + [m["name"] for m in MEAL_OPTIONS[slot]]

                default_meal_name = saved_defaults.get((day_name, slot), "None")
                default_index = options.index(default_meal_name) if default_meal_name in options else 0

                chosen_name = st.radio(
                    f"{slot}",
                    options,
                    index=default_index,
                    key=f"{week_start}_{day_name}_{slot}",
                    horizontal=False
                )

                chosen_meal = None if chosen_name == "None" else meal_by_name(slot, chosen_name)
                selections[day_name][slot] = chosen_meal

                if chosen_meal:
                    st.caption(
                        f"Calories: {chosen_meal['calories']} | "
                        f"Protein: {chosen_meal['protein']}g | "
                        f"Carbs: {chosen_meal['carbs']}g | "
                        f"Fat: {chosen_meal['fat']}g | "
                        f"Cost: ${chosen_meal['cost']:.2f} | "
                        f"{chosen_meal['tags']}"
                    )

            day_totals = calculate_day_totals(selections[day_name])
            st.markdown(
                f"**Daily Total:** {day_totals['calories']} cal | "
                f"{day_totals['protein']}g protein | "
                f"${day_totals['cost']:.2f}"
            )

    selected_rows = flatten_selection(selections, week_start)

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("💾 Save Week to Google Sheets", use_container_width=True):
            ok, message = save_week_to_sheets(week_start, selected_rows)
            if ok:
                st.success(message)
            else:
                st.warning(message)

    with col2:
        st.info("Saving replaces the existing saved plan for this selected week.")


# =========================================================
# Weekly Summary
# =========================================================
with tab3:
    st.subheader("Weekly Nutrition + Budget Summary")

    summary_df = calculate_week_totals(selections)

    weekly_calories = summary_df["Calories"].sum()
    weekly_protein = summary_df["Protein"].sum()
    weekly_cost = summary_df["Cost"].sum()
    avg_calories = summary_df["Calories"].mean()
    avg_protein = summary_df["Protein"].mean()
    avg_cost = summary_df["Cost"].mean()
    remaining = budget_limit - weekly_cost

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Weekly Calories", f"{weekly_calories:,.0f}")
    col2.metric("Weekly Protein", f"{weekly_protein:,.0f}g")
    col3.metric("Weekly Cost", f"${weekly_cost:.2f}")
    col4.metric("Remaining", f"${remaining:.2f}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Calories / Day", f"{avg_calories:,.0f}")
    col2.metric("Avg Protein / Day", f"{avg_protein:,.0f}g")
    col3.metric("Avg Cost / Day", f"${avg_cost:.2f}")

    st.progress(min(weekly_cost / budget_limit, 1.0))
    if weekly_cost <= budget_limit:
        st.success("Within weekly budget. Honey pot protected. 🍯")
    else:
        st.error("Over weekly budget. Swap a premium lunch for a grocery sandwich or lower-cost option.")

    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Macro Trend by Day")
    chart_df = summary_df.set_index("Day")[["Calories", "Protein", "Cost"]]
    st.line_chart(chart_df)


# =========================================================
# Grocery List
# =========================================================
with tab4:
    st.subheader("Dynamic Grocery List Based on Selected Meals")

    dynamic_grocery_df = build_grocery_list(selections)

    if dynamic_grocery_df.empty:
        st.warning("No meals selected yet.")
    else:
        st.dataframe(dynamic_grocery_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Monthly Buy — 1st of the Month")
    monthly_df = pd.DataFrame(MONTHLY_ITEMS)
    st.dataframe(monthly_df, use_container_width=True, hide_index=True)
    st.metric("Estimated Monthly Bulk Buy", f"${monthly_df['Estimated Cost'].sum():.2f}")

    st.subheader("Weekly Refill")
    weekly_df = pd.DataFrame(WEEKLY_REFILL_ITEMS)
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)
    st.metric("Estimated Weekly Refill", f"${weekly_df['Estimated Cost'].sum():.2f}")

    st.markdown("""
    <div class="section-card">
        <h3>🧊 Mini Fridge Rule</h3>
        Save mini fridge space for milk, Greek yogurt, boiled eggs, and the current rotisserie chicken.
        Keep whey, peanut butter, bagels, bananas, trail mix, granola, protein bars, rice cups,
        and bread outside the fridge.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 30-Day History
# =========================================================
with tab5:
    st.subheader("30-Day History")

    if not google_sheets_is_configured():
        st.warning("Connect Google Sheets to store and view 30-day history.")
    else:
        try:
            logs_df = read_saved_logs()

            if logs_df.empty:
                st.info("No saved history yet. Save a weekly plan first.")
            else:
                logs_df["saved_at_dt"] = pd.to_datetime(logs_df["saved_at"], errors="coerce")
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
                recent = logs_df[logs_df["saved_at_dt"] >= cutoff].copy()

                st.caption("Showing meal selections saved in the last 30 days.")
                st.dataframe(
                    recent.drop(columns=["saved_at_dt"], errors="ignore"),
                    use_container_width=True,
                    hide_index=True
                )

                if not recent.empty:
                    daily_history = recent.groupby(["week_start", "day"], as_index=False).agg({
                        "calories": "sum",
                        "protein": "sum",
                        "cost": "sum"
                    })

                    st.subheader("Recent Daily Totals")
                    st.dataframe(daily_history, use_container_width=True, hide_index=True)
                    st.line_chart(daily_history[["calories", "protein", "cost"]])

        except Exception as e:
            st.error("Could not read history from Google Sheets.")
            st.caption(str(e))


st.markdown("---")
st.caption("Pooh Bear Yum Yum Tracker • Streamlit + Google Sheets • Dynamic client meal plan tracker")