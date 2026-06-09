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
# CSS
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
# Component Options
# =========================================================
# Units are estimated:
# - Whey protein: scoops
# - Milk: oz
# - Peanut butter: tbsp
# - Trail mix/granola: servings
# - Most restaurant/packaged items: item count

COMPONENTS = {
    "Drink": [
        {
            "name": "None",
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0,
            "tags": "",
            "ingredients": {}
        },
        {
            "name": "Protein iced coffee",
            "calories": 380, "protein": 54, "carbs": 24, "fat": 10, "cost": 2.00,
            "tags": "home, high protein",
            "ingredients": {"Whey protein": 2, "Whole milk": 16, "Cold coffee": 1}
        },
        {
            "name": "Regular cold coffee",
            "calories": 40, "protein": 1, "carbs": 8, "fat": 1, "cost": 0.50,
            "tags": "low calorie",
            "ingredients": {"Cold coffee": 1}
        },
        {
            "name": "Whole milk",
            "calories": 150, "protein": 8, "carbs": 12, "fat": 8, "cost": 0.75,
            "tags": "mini-fridge",
            "ingredients": {"Whole milk": 8}
        },
        {
            "name": "Water",
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0,
            "tags": "hydration",
            "ingredients": {"Water": 1}
        }
    ],
    "Main": [
        {
            "name": "None",
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0,
            "tags": "",
            "ingredients": {}
        },
        {
            "name": "Peanut butter bagel",
            "calories": 470, "protein": 18, "carbs": 58, "fat": 19, "cost": 1.25,
            "tags": "budget, shelf-stable",
            "ingredients": {"Bagel": 1, "Peanut butter": 2}
        },
        {
            "name": "Greek yogurt + granola bowl",
            "calories": 350, "protein": 20, "carbs": 45, "fat": 8, "cost": 2.00,
            "tags": "mini-fridge",
            "ingredients": {"Greek yogurt": 1, "Granola": 1}
        },
        {
            "name": "Subway Footlong Turkey",
            "calories": 850, "protein": 60, "carbs": 95, "fat": 22, "cost": 12.00,
            "tags": "handheld, driving-friendly",
            "ingredients": {"Subway Footlong Turkey": 1}
        },
        {
            "name": "Subway Footlong Rotisserie Chicken",
            "calories": 900, "protein": 65, "carbs": 95, "fat": 25, "cost": 13.00,
            "tags": "handheld, driving-friendly",
            "ingredients": {"Subway Footlong Rotisserie Chicken": 1}
        },
        {
            "name": "Grocery store deli sandwich",
            "calories": 700, "protein": 35, "carbs": 75, "fat": 25, "cost": 7.00,
            "tags": "budget, handheld",
            "ingredients": {"Grocery store deli sandwich": 1}
        },
        {
            "name": "Vitality Bowl protein wrap",
            "calories": 700, "protein": 30, "carbs": 75, "fat": 24, "cost": 15.00,
            "tags": "client favorite, handheld",
            "ingredients": {"Vitality Bowl protein wrap": 1}
        },
        {
            "name": "Jersey Mike's Giant Turkey Sub",
            "calories": 1100, "protein": 70, "carbs": 120, "fat": 38, "cost": 15.00,
            "tags": "higher calorie, handheld",
            "ingredients": {"Jersey Mike's Giant Turkey Sub": 1}
        },
        {
            "name": "Rotisserie chicken portion",
            "calories": 550, "protein": 65, "carbs": 0, "fat": 30, "cost": 2.50,
            "tags": "home dinner, high protein",
            "ingredients": {"Rotisserie chicken portion": 1}
        }
    ],
    "Side": [
        {
            "name": "None",
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0,
            "tags": "",
            "ingredients": {}
        },
        {
            "name": "Banana",
            "calories": 120, "protein": 1, "carbs": 31, "fat": 0, "cost": 0.35,
            "tags": "fruit, portable",
            "ingredients": {"Banana": 1}
        },
        {
            "name": "2 boiled eggs",
            "calories": 140, "protein": 12, "carbs": 1, "fat": 10, "cost": 1.10,
            "tags": "mini-fridge, low sugar",
            "ingredients": {"Boiled eggs": 2}
        },
        {
            "name": "Protein bar",
            "calories": 200, "protein": 20, "carbs": 22, "fat": 6, "cost": 1.25,
            "tags": "backup snack",
            "ingredients": {"Protein bar": 1}
        },
        {
            "name": "Trail mix",
            "calories": 380, "protein": 9, "carbs": 35, "fat": 24, "cost": 1.15,
            "tags": "car snack, shelf-stable",
            "ingredients": {"Trail mix": 1}
        },
        {
            "name": "Rice cup",
            "calories": 220, "protein": 4, "carbs": 46, "fat": 2, "cost": 1.25,
            "tags": "easy carb, lower sugar",
            "ingredients": {"Rice cup": 1}
        },
        {
            "name": "Whole wheat bagel",
            "calories": 250, "protein": 10, "carbs": 48, "fat": 2, "cost": 0.75,
            "tags": "easy carb",
            "ingredients": {"Whole wheat bagel": 1}
        },
        {
            "name": "Whole wheat bread serving",
            "calories": 240, "protein": 8, "carbs": 44, "fat": 4, "cost": 0.75,
            "tags": "easy carb",
            "ingredients": {"Whole wheat bread serving": 1}
        }
    ],
    "Dessert/Treat": [
        {
            "name": "None",
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0,
            "tags": "lower sugar option",
            "ingredients": {}
        },
        {
            "name": "Greek yogurt",
            "calories": 150, "protein": 18, "carbs": 12, "fat": 3, "cost": 1.25,
            "tags": "higher protein dessert",
            "ingredients": {"Greek yogurt": 1}
        },
        {
            "name": "Granola serving",
            "calories": 200, "protein": 4, "carbs": 35, "fat": 5, "cost": 0.75,
            "tags": "sweet, moderate sugar",
            "ingredients": {"Granola": 1}
        },
        {
            "name": "Protein bar",
            "calories": 200, "protein": 20, "carbs": 22, "fat": 6, "cost": 1.25,
            "tags": "sweet, high protein",
            "ingredients": {"Protein bar": 1}
        },
        {
            "name": "Banana",
            "calories": 120, "protein": 1, "carbs": 31, "fat": 0, "cost": 0.35,
            "tags": "fruit",
            "ingredients": {"Banana": 1}
        }
    ]
}

MEAL_SLOTS = ["Breakfast", "Lunch", "Snack", "Dinner"]
COMPONENT_SLOTS = ["Drink", "Main", "Side", "Dessert/Treat"]


# =========================================================
# Default Example Plan
# =========================================================
DEFAULT_DAY_PLAN = {
    "Breakfast": {
        "Drink": "Protein iced coffee",
        "Main": "Peanut butter bagel",
        "Side": "2 boiled eggs",
        "Dessert/Treat": "Banana"
    },
    "Lunch": {
        "Drink": "Water",
        "Main": "Subway Footlong Turkey",
        "Side": "Protein bar",
        "Dessert/Treat": "None"
    },
    "Snack": {
        "Drink": "Water",
        "Main": "Greek yogurt + granola bowl",
        "Side": "Trail mix",
        "Dessert/Treat": "None"
    },
    "Dinner": {
        "Drink": "Water",
        "Main": "Rotisserie chicken portion",
        "Side": "Whole wheat bagel",
        "Dessert/Treat": "Greek yogurt"
    }
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
# Google Sheets
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
        worksheet = spreadsheet.add_worksheet(title=title, rows=2000, cols=max(20, len(headers)))
        worksheet.append_row(headers)
        return worksheet

    values = worksheet.get_all_values()
    if len(values) == 0:
        worksheet.append_row(headers)
    return worksheet

def daily_log_headers():
    return [
        "saved_at", "plan_date", "meal_slot", "component_slot", "component_name",
        "calories", "protein", "carbs", "fat", "cost", "ingredients_json"
    ]

def read_logs():
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return pd.DataFrame(columns=daily_log_headers())

    worksheet = get_or_create_worksheet(spreadsheet, "Daily_Logs", daily_log_headers())
    records = worksheet.get_all_records()

    if not records:
        return pd.DataFrame(columns=daily_log_headers())

    df = pd.DataFrame(records)
    for col in ["calories", "protein", "carbs", "fat", "cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def clean_for_google_sheets(df):
    """
    Google Sheets API does not like NaN/None/numpy values.
    This converts the dataframe into clean JSON-safe rows.
    """
    if df.empty:
        return []

    df = df.copy()

    # Ensure all expected columns exist
    headers = daily_log_headers()
    for col in headers:
        if col not in df.columns:
            df[col] = ""

    df = df[headers]

    # Replace pandas/numpy missing values with empty strings
    df = df.fillna("")

    # Convert each value into a JSON-safe Python value
    clean_rows = []
    for _, row in df.iterrows():
        clean_row = []
        for value in row.tolist():
            if pd.isna(value):
                clean_row.append("")
            elif isinstance(value, (int, float, str, bool)):
                clean_row.append(value)
            else:
                clean_row.append(str(value))
        clean_rows.append(clean_row)

    return clean_rows


def save_day_to_sheets(plan_date, rows):
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False, "Google Sheets is not connected yet."

    headers = daily_log_headers()
    worksheet = get_or_create_worksheet(spreadsheet, "Daily_Logs", headers)

    existing = worksheet.get_all_records()
    existing_df = pd.DataFrame(existing)

    date_str = str(plan_date)

    # Remove previously saved rows for this same date, then replace them
    if not existing_df.empty and "plan_date" in existing_df.columns:
        existing_df = existing_df[existing_df["plan_date"].astype(str) != date_str]

    new_df = pd.DataFrame(rows)

    if existing_df.empty:
        combined = new_df
    elif new_df.empty:
        combined = existing_df
    else:
        combined = pd.concat([existing_df, new_df], ignore_index=True)

    worksheet.clear()
    worksheet.append_row(headers)

    clean_rows = clean_for_google_sheets(combined)

    if clean_rows:
        worksheet.append_rows(clean_rows, value_input_option="USER_ENTERED")

    return True, f"Saved meals for {date_str}."

def load_saved_day(plan_date):
    logs = read_logs()
    if logs.empty:
        return {}

    date_str = str(plan_date)
    day_logs = logs[logs["plan_date"].astype(str) == date_str]

    saved = {}
    for _, row in day_logs.iterrows():
        saved[(row["meal_slot"], row["component_slot"])] = row["component_name"]

    return saved


# =========================================================
# Helpers
# =========================================================
def component_names(component_slot):
    return [item["name"] for item in COMPONENTS[component_slot]]

def get_component(component_slot, name):
    for item in COMPONENTS[component_slot]:
        if item["name"] == name:
            return item
    return COMPONENTS[component_slot][0]

def calculate_totals(selected_components):
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0}
    for comp in selected_components:
        totals["calories"] += comp["calories"]
        totals["protein"] += comp["protein"]
        totals["carbs"] += comp["carbs"]
        totals["fat"] += comp["fat"]
        totals["cost"] += comp["cost"]
    return totals

def rows_from_selections(plan_date, selections):
    rows = []
    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for meal_slot, meal_data in selections.items():
        if not meal_data.get("include", False):
            continue

        components = meal_data.get("components", {})
        for component_slot, component in components.items():
            if component["name"] != "None":
                rows.append({
                    "saved_at": saved_at,
                    "plan_date": str(plan_date),
                    "meal_slot": meal_slot,
                    "component_slot": component_slot,
                    "component_name": component["name"],
                    "calories": component["calories"],
                    "protein": component["protein"],
                    "carbs": component["carbs"],
                    "fat": component["fat"],
                    "cost": component["cost"],
                    "ingredients_json": json.dumps(component["ingredients"])
                })
    return rows

def build_dynamic_grocery(selections):
    groceries = {}

    for meal_data in selections.values():
        if not meal_data.get("include", False):
            continue

        for component in meal_data.get("components", {}).values():
            for ingredient, qty in component["ingredients"].items():
                groceries[ingredient] = groceries.get(ingredient, 0) + qty

    rows = [{"Item": item, "Estimated Amount": qty} for item, qty in groceries.items()]
    return pd.DataFrame(rows).sort_values("Item") if rows else pd.DataFrame(columns=["Item", "Estimated Amount"])

def summarize_day_from_logs(logs_df, plan_date):
    date_str = str(plan_date)
    day_logs = logs_df[logs_df["plan_date"].astype(str) == date_str].copy()
    if day_logs.empty:
        return None, pd.DataFrame()

    totals = day_logs[["calories", "protein", "carbs", "fat", "cost"]].sum()
    return totals, day_logs

def get_recent_dates(logs_df):
    if logs_df.empty:
        return []

    dates = sorted(logs_df["plan_date"].astype(str).unique(), reverse=True)
    return dates


# =========================================================
# Header
# =========================================================
st.markdown('<p class="main-title">🐻 Pooh Bear Yum Yum Tracker</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Dynamic client meal tracker with editable meal components, macros, grocery list, budget, and daily history.</p>',
    unsafe_allow_html=True
)


# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("🐝 Client Controls")

selected_date = st.sidebar.date_input("Select day/date", value=date.today())

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

st.sidebar.info("🍯 Pick the foods. The tracker does the math.")


# =========================================================
# Load saved day if available
# =========================================================
saved_day = {}
if google_sheets_is_configured():
    try:
        saved_day = load_saved_day(selected_date)
    except Exception as e:
        st.sidebar.error("Could not load saved day.")
        st.sidebar.caption(str(e))


# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "✅ Daily Meal Builder",
    "📊 Daily Summary",
    "🛒 Grocery List",
    "📅 History"
])


# =========================================================
# Overview
# =========================================================
with tab1:
    st.subheader("Client Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Goal", CLIENT["goal"])
    c2.metric("Calories", CLIENT["calorie_target"])
    c3.metric("Protein", CLIENT["protein_target"])
    c4.metric("Budget", f"${budget_limit}/week")

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

    st.markdown("### New Meal Builder Logic")
    st.write(
        "Each meal is split into components: drink, main food, side, and dessert/treat. "
        "The client starts from a default example day, edits the choices, then saves the selected date. "
        "Google Sheets stores each date so previous meals can be reviewed later."
    )


# =========================================================
# Daily Meal Builder
# =========================================================
selections = {}

with tab2:
    st.subheader(f"Daily Meal Builder — {selected_date.strftime('%A, %b %d, %Y')}")
    st.caption(
        "Use the dropdowns to edit each meal. Check the meal box only if that meal should count "
        "toward macros, grocery list, budget, and Google Sheets saving."
    )

    for meal_slot in MEAL_SLOTS:
        selections[meal_slot] = {
            "include": False,
            "components": {}
        }

        with st.expander(meal_slot, expanded=True):
            include_meal = st.checkbox(
                f"Include {meal_slot} in saved plan",
                value=True,
                key=f"{selected_date}_{meal_slot}_include_meal"
            )

            selections[meal_slot]["include"] = include_meal

            cols = st.columns(4)

            for idx, component_slot in enumerate(COMPONENT_SLOTS):
                with cols[idx]:
                    default_name = saved_day.get(
                        (meal_slot, component_slot),
                        DEFAULT_DAY_PLAN[meal_slot][component_slot]
                    )

                    options = component_names(component_slot)
                    default_index = options.index(default_name) if default_name in options else 0

                    chosen_name = st.selectbox(
                        component_slot,
                        options,
                        index=default_index,
                        key=f"{selected_date}_{meal_slot}_{component_slot}"
                    )

                    component = get_component(component_slot, chosen_name)
                    selections[meal_slot]["components"][component_slot] = component

                    if component["name"] != "None":
                        st.caption(
                            f"{component['calories']} cal | "
                            f"{component['protein']}g protein | "
                            f"${component['cost']:.2f}"
                        )

            if include_meal:
                meal_totals = calculate_totals(list(selections[meal_slot]["components"].values()))
                st.markdown(
                    f"**{meal_slot} Total:** "
                    f"{meal_totals['calories']} cal | "
                    f"{meal_totals['protein']}g protein | "
                    f"{meal_totals['carbs']}g carbs | "
                    f"{meal_totals['fat']}g fat | "
                    f"${meal_totals['cost']:.2f}"
                )
            else:
                st.warning(f"{meal_slot} is skipped. It will not be saved or counted.")

    all_components = []
    for meal_slot in MEAL_SLOTS:
        if selections[meal_slot]["include"]:
            all_components.extend(list(selections[meal_slot]["components"].values()))

    daily_totals = calculate_totals(all_components)

    st.markdown("---")
    st.subheader("Live Daily Total")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Calories", f"{daily_totals['calories']:,}")
    c2.metric("Protein", f"{daily_totals['protein']}g")
    c3.metric("Carbs", f"{daily_totals['carbs']}g")
    c4.metric("Fat", f"{daily_totals['fat']}g")
    c5.metric("Cost", f"${daily_totals['cost']:.2f}")

    rows = rows_from_selections(selected_date, selections)

    if st.button("💾 Save Included Meals to Google Sheets", use_container_width=True):
        if not rows:
            st.warning("No meals are included, so nothing was saved.")
        else:
            ok, msg = save_day_to_sheets(selected_date, rows)
            if ok:
                st.success(msg)
            else:
                st.warning(msg)


# =========================================================
# Daily Summary
# =========================================================
with tab3:
    st.subheader("Daily Meal Summary")

    summary_rows = []
    for meal_slot in MEAL_SLOTS:
        meal_data = selections[meal_slot]
        components = meal_data["components"]

        if meal_data["include"]:
            totals = calculate_totals(list(components.values()))
            status = "Included"
        else:
            totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0}
            status = "Skipped"

        summary_rows.append({
            "Status": status,
            "Meal": meal_slot,
            "Drink": components["Drink"]["name"],
            "Main": components["Main"]["name"],
            "Side": components["Side"]["name"],
            "Dessert/Treat": components["Dessert/Treat"]["name"],
            "Calories": totals["calories"],
            "Protein": totals["protein"],
            "Carbs": totals["carbs"],
            "Fat": totals["fat"],
            "Cost": totals["cost"]
        })

    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Daily Totals")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Calories", f"{daily_totals['calories']:,}")
    c2.metric("Protein", f"{daily_totals['protein']}g")
    c3.metric("Carbs", f"{daily_totals['carbs']}g")
    c4.metric("Fat", f"{daily_totals['fat']}g")
    c5.metric("Cost", f"${daily_totals['cost']:.2f}")

    st.markdown("### Daily Goal Check")
    if daily_totals["calories"] < 3400:
        st.warning("Calories are low for a 4,000-calorie bulk day. Add trail mix, milk, or another bagel.")
    elif daily_totals["calories"] <= 4200:
        st.success("Calories are in a strong lean-bulk range.")
    else:
        st.info("Calories are high. This may be fine for a heavy activity day, but monitor weight gain.")

    if daily_totals["protein"] < 180:
        st.warning("Protein is below target. Add protein coffee, eggs, chicken, or a protein bar.")
    else:
        st.success("Protein target is met.")


# =========================================================
# Grocery List
# =========================================================
with tab4:
    st.subheader("Dynamic Grocery List for Selected Day")

    grocery_df = build_dynamic_grocery(selections)
    st.dataframe(grocery_df, use_container_width=True, hide_index=True)

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
        Fridge priority: milk, Greek yogurt, boiled eggs, and the current rotisserie chicken.
        Keep whey, peanut butter, bagels, bananas, trail mix, granola, protein bars, rice cups,
        and bread outside the fridge.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# History
# =========================================================
with tab5:
    st.subheader("Previous Days / Calendar History")

    if not google_sheets_is_configured():
        st.warning("Connect Google Sheets to save and view previous days.")
    else:
        try:
            logs_df = read_logs()

            if logs_df.empty:
                st.info("No saved days yet.")
            else:
                recent_dates = get_recent_dates(logs_df)

                selected_history_date = st.selectbox(
                    "Select a saved date",
                    recent_dates,
                    index=0
                )

                totals, day_logs = summarize_day_from_logs(logs_df, selected_history_date)

                if totals is not None:
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Calories", f"{totals['calories']:,.0f}")
                    c2.metric("Protein", f"{totals['protein']:,.0f}g")
                    c3.metric("Carbs", f"{totals['carbs']:,.0f}g")
                    c4.metric("Fat", f"{totals['fat']:,.0f}g")
                    c5.metric("Cost", f"${totals['cost']:.2f}")

                    st.markdown("### Meals Saved for This Day")
                    display = day_logs[[
                        "meal_slot", "component_slot", "component_name",
                        "calories", "protein", "carbs", "fat", "cost"
                    ]].copy()

                    st.dataframe(display, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("Last 30 Days Summary")

                logs_df["plan_date_dt"] = pd.to_datetime(logs_df["plan_date"], errors="coerce")
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
                recent = logs_df[logs_df["plan_date_dt"] >= cutoff].copy()

                daily_history = recent.groupby("plan_date", as_index=False).agg({
                    "calories": "sum",
                    "protein": "sum",
                    "carbs": "sum",
                    "fat": "sum",
                    "cost": "sum"
                }).sort_values("plan_date", ascending=False)

                st.dataframe(daily_history, use_container_width=True, hide_index=True)

                chart_df = daily_history.sort_values("plan_date").set_index("plan_date")[["calories", "protein", "cost"]]
                st.line_chart(chart_df)

        except Exception as e:
            st.error("Could not load history.")
            st.caption(str(e))


st.markdown("---")
st.caption("Pooh Bear Yum Yum Tracker • Component-based meal planner • Streamlit + Google Sheets")