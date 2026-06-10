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
# PAGE SETUP
# =========================================================
st.set_page_config(
    page_title="Pooh Bear Yum Yum Tracker",
    page_icon="🐻",
    layout="wide"
)

# =========================================================
# MOBILE-FRIENDLY CSS
# =========================================================
st.markdown("""
<style>
    :root {
        --app-bg: #ffffff;
        --app-text: #1f2933;
        --app-muted: #5f6b7a;

        --honey: #C47F00;
        --honey-bright: #B96B00;
        --honey-soft: #FFF4CC;
        --honey-border: #E8B64B;

        --bear: #5C3B1E;
        --bear-soft: #FFF7E6;

        --card-bg: #ffffff;
        --card-border: #E5E7EB;
        --dark-card-bg: #ffffff;

        --kpi-bg: #ffffff;
        --kpi-border: #D6DCE5;
        --kpi-text: #1f2933;

        --success-bg: #EAF7EF;
        --success-border: #6BCB88;
        --success-text: #14532D;

        --warning-bg: #FFF7E6;
        --warning-border: #E8B64B;
        --warning-text: #5C3B1E;

        --button-bg: #FFF7E6;
        --button-text: #5C3B1E;
        --button-hover: #FFE8A3;

        --shadow: rgba(15, 23, 42, 0.10);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --app-bg: #0E1117;
            --app-text: #F8FAFC;
            --app-muted: #B8C0CC;

            --honey: #FFD95A;
            --honey-bright: #F4C542;
            --honey-soft: #2B1A0B;
            --honey-border: #F4C542;

            --bear: #FFD95A;
            --bear-soft: #21170C;

            --card-bg: #16191f;
            --card-border: #30343d;
            --dark-card-bg: #11151c;

            --kpi-bg: #11151c;
            --kpi-border: #30343d;
            --kpi-text: #F8FAFC;

            --success-bg: #102318;
            --success-border: #245c35;
            --success-text: #D1FAE5;

            --warning-bg: #3a2411;
            --warning-border: #cc8a22;
            --warning-text: #FFF7E6;

            --button-bg: #17120A;
            --button-text: #FFD95A;
            --button-hover: #2B1A0B;

            --shadow: rgba(0, 0, 0, 0.25);
        }
    }

    .stApp {
        color: var(--app-text);
    }

    .hero-wrap {
        text-align: center;
        background:
            radial-gradient(circle at top, rgba(255,217,90,0.38) 0%, rgba(255,217,90,0.12) 34%, transparent 70%),
            linear-gradient(135deg, var(--honey-soft), var(--card-bg));
        border: 1px solid var(--honey-border);
        border-radius: 28px;
        padding: 28px 18px;
        margin-bottom: 22px;
        box-shadow: 0 0 25px var(--shadow);
    }

    .hero-title {
        font-size: 44px;
        font-weight: 950;
        color: var(--honey);
        margin-bottom: 6px;
        line-height: 1.05;
        text-shadow: 0 2px 0 rgba(92,59,30,0.35);
    }

    .hero-subtitle {
        font-size: 17px;
        color: var(--app-text);
        margin-bottom: 0px;
    }

    .honey-pill {
        display: inline-block;
        background: var(--honey);
        color: #3B2A1A;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 800;
        margin-bottom: 10px;
        font-size: 14px;
    }

    .section-card {
        background: linear-gradient(135deg, var(--bear-soft), var(--card-bg));
        color: var(--app-text);
        padding: 18px;
        border-radius: 18px;
        border: 1px solid var(--honey-border);
        box-shadow: 0 4px 15px var(--shadow);
        margin-bottom: 16px;
        font-size: 15px;
        line-height: 1.6;
    }

    .section-card h3 {
        color: var(--bear);
        margin-top: 0;
        margin-bottom: 8px;
    }

    .dark-card,
    .component-block {
        background: var(--card-bg);
        color: var(--app-text);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px var(--shadow);
    }

    .meal-total,
    .grocery-cost-note {
        background: var(--success-bg);
        color: var(--success-text);
        border: 1px solid var(--success-border);
        padding: 12px;
        border-radius: 12px;
        margin-top: 8px;
        margin-bottom: 14px;
    }

    .warning-card {
        background: var(--warning-bg);
        color: var(--warning-text);
        border: 1px solid var(--warning-border);
        padding: 14px;
        border-radius: 14px;
        margin-bottom: 12px;
    }

    .kpi-card {
        background: var(--kpi-bg);
        color: var(--kpi-text);
        border: 1px solid var(--kpi-border);
        border-radius: 16px;
        padding: 14px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .kpi-card b {
        color: var(--honey);
    }

    .component-full-name {
        color: var(--app-text);
        font-weight: 800;
        font-size: 15px;
        margin: 6px 0 8px 0;
        word-break: break-word;
        overflow-wrap: anywhere;
    }

    div[data-testid="stMetric"] {
        background: var(--kpi-bg);
        color: var(--kpi-text);
        border: 1px solid var(--kpi-border);
        padding: 14px;
        border-radius: 14px;
        box-shadow: 0 2px 8px var(--shadow);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div {
        color: var(--kpi-text) !important;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 999px;
        border: 1px solid var(--honey-border);
        background: var(--button-bg);
        color: var(--button-text);
        font-weight: 800;
        padding: 0.7rem 1rem;
    }

    div.stButton > button:hover {
        border-color: var(--honey);
        background: var(--button-hover);
        color: var(--button-text);
    }

    .footer-honey {
        text-align: center;
        color: var(--honey);
        font-weight: 800;
        padding: 18px;
        margin-top: 28px;
    }

    /* Dataframes / editors */
    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        border-radius: 14px;
        overflow: hidden;
    }

    @media (max-width: 768px) {
        .hero-title {
            font-size: 30px;
        }
        .hero-subtitle {
            font-size: 14px;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }

    .compact-kpi {
        background: var(--kpi-bg);
        color: var(--kpi-text);
        border: 1px solid var(--kpi-border);
        border-radius: 14px;
        padding: 10px 12px;
        margin-top: 8px;
        min-height: 112px;
    }

    .compact-kpi b {
        color: var(--honey);
        font-size: 14px;
    }

    .compact-name {
        color: var(--app-text);
        font-weight: 750;
        font-size: 13px;
        line-height: 1.25;
        margin: 5px 0 7px 0;
        white-space: normal;
        overflow-wrap: anywhere;
    }

    .compact-macro {
        font-size: 13px;
        line-height: 1.45;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# CLIENT + TARGETS
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
    "daily_budget": 150 / 7,
    "lifestyle": "Driving job, mini fridge only, no kitchen, low-prep meals",
    "focus": "High protein, budget-conscious, lower sugar, lower sodium where possible"
}


# =========================================================
# FOOD COMPONENTS
# =========================================================
COMPONENTS = {
    "Drink": [
        {"name": "None", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0, "ingredients": {}},
        {"name": "Protein iced coffee", "calories": 380, "protein": 54, "carbs": 24, "fat": 10, "cost": 2.00,
         "ingredients": {"Whey protein": 2, "Whole milk": 16, "Cold coffee": 1}},
        {"name": "Regular cold coffee", "calories": 40, "protein": 1, "carbs": 8, "fat": 1, "cost": 0.50,
         "ingredients": {"Cold coffee": 1}},
        {"name": "Whole milk", "calories": 150, "protein": 8, "carbs": 12, "fat": 8, "cost": 0.75,
         "ingredients": {"Whole milk": 8}},
        {"name": "Water", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0,
         "ingredients": {}},
    ],
    "Main": [
        {"name": "None", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0, "ingredients": {}},
        {"name": "Peanut butter bagel", "calories": 470, "protein": 18, "carbs": 58, "fat": 19, "cost": 1.25,
         "ingredients": {"Bagel": 1, "Peanut butter": 2}},
        {"name": "Greek yogurt + granola bowl", "calories": 350, "protein": 20, "carbs": 45, "fat": 8, "cost": 2.00,
         "ingredients": {"Greek yogurt": 1, "Granola": 1}},
        {"name": "Subway Footlong Turkey", "calories": 850, "protein": 60, "carbs": 95, "fat": 22, "cost": 12.00,
         "ingredients": {"Subway Footlong Turkey": 1}},
        {"name": "Subway Footlong Rotisserie Chicken", "calories": 900, "protein": 65, "carbs": 95, "fat": 25, "cost": 13.00,
         "ingredients": {"Subway Footlong Rotisserie Chicken": 1}},
        {"name": "Grocery store deli sandwich", "calories": 700, "protein": 35, "carbs": 75, "fat": 25, "cost": 7.00,
         "ingredients": {"Grocery store deli sandwich": 1}},
        {"name": "Vitality Bowl protein wrap", "calories": 700, "protein": 30, "carbs": 75, "fat": 24, "cost": 15.00,
         "ingredients": {"Vitality Bowl protein wrap": 1}},
        {"name": "Jersey Mike's Giant Turkey Sub", "calories": 1100, "protein": 70, "carbs": 120, "fat": 38, "cost": 15.00,
         "ingredients": {"Jersey Mike's Giant Turkey Sub": 1}},
        {"name": "Rotisserie chicken portion", "calories": 550, "protein": 65, "carbs": 0, "fat": 30, "cost": 2.50,
         "ingredients": {"Rotisserie chicken portion": 1}},
    ],
    "Side": [
        {"name": "None", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0, "ingredients": {}},
        {"name": "Banana", "calories": 120, "protein": 1, "carbs": 31, "fat": 0, "cost": 0.35,
         "ingredients": {"Banana": 1}},
        {"name": "2 boiled eggs", "calories": 140, "protein": 12, "carbs": 1, "fat": 10, "cost": 1.10,
         "ingredients": {"Boiled eggs": 2}},
        {"name": "Protein bar", "calories": 200, "protein": 20, "carbs": 22, "fat": 6, "cost": 1.25,
         "ingredients": {"Protein bar": 1}},
        {"name": "Trail mix", "calories": 380, "protein": 9, "carbs": 35, "fat": 24, "cost": 1.15,
         "ingredients": {"Trail mix": 1}},
        {"name": "Rice cup", "calories": 220, "protein": 4, "carbs": 46, "fat": 2, "cost": 1.25,
         "ingredients": {"Rice cup": 1}},
        {"name": "Whole wheat bagel", "calories": 250, "protein": 10, "carbs": 48, "fat": 2, "cost": 0.75,
         "ingredients": {"Whole wheat bagel": 1}},
        {"name": "Whole wheat bread serving", "calories": 240, "protein": 8, "carbs": 44, "fat": 4, "cost": 0.75,
         "ingredients": {"Whole wheat bread serving": 1}},
    ],
    "Dessert/Treat": [
        {"name": "None", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0, "ingredients": {}},
        {"name": "Greek yogurt", "calories": 150, "protein": 18, "carbs": 12, "fat": 3, "cost": 1.25,
         "ingredients": {"Greek yogurt": 1}},
        {"name": "Granola serving", "calories": 200, "protein": 4, "carbs": 35, "fat": 5, "cost": 0.75,
         "ingredients": {"Granola": 1}},
        {"name": "Protein bar", "calories": 200, "protein": 20, "carbs": 22, "fat": 6, "cost": 1.25,
         "ingredients": {"Protein bar": 1}},
        {"name": "Banana", "calories": 120, "protein": 1, "carbs": 31, "fat": 0, "cost": 0.35,
         "ingredients": {"Banana": 1}},
    ],
}

MEAL_SLOTS = ["Breakfast", "Lunch", "Snack", "Dinner"]
COMPONENT_SLOTS = ["Drink", "Main", "Side", "Dessert/Treat"]

DEFAULT_DAY_PLAN = {
    "Breakfast": {"Drink": "Protein iced coffee", "Main": "Peanut butter bagel", "Side": "2 boiled eggs", "Dessert/Treat": "Banana"},
    "Lunch": {"Drink": "Water", "Main": "Subway Footlong Turkey", "Side": "Protein bar", "Dessert/Treat": "None"},
    "Snack": {"Drink": "Water", "Main": "Greek yogurt + granola bowl", "Side": "Trail mix", "Dessert/Treat": "None"},
    "Dinner": {"Drink": "Water", "Main": "Rotisserie chicken portion", "Side": "Whole wheat bagel", "Dessert/Treat": "Greek yogurt"},
}

# Meal-specific dropdown rules.
# This prevents breakfast from showing lunch/dinner foods and keeps the app cleaner for the client.
MEAL_ALLOWED_OPTIONS = {
    "Breakfast": {
        "Drink": ["None", "Protein iced coffee", "Regular cold coffee", "Whole milk", "Water"],
        "Main": ["None", "Peanut butter bagel", "Greek yogurt + granola bowl"],
        "Side": ["None", "Banana", "2 boiled eggs", "Protein bar"],
        "Dessert/Treat": ["None", "Greek yogurt", "Granola serving", "Protein bar", "Banana"],
    },
    "Lunch": {
        "Drink": ["None", "Water", "Regular cold coffee"],
        "Main": [
            "None",
            "Subway Footlong Turkey",
            "Subway Footlong Rotisserie Chicken",
            "Grocery store deli sandwich",
            "Vitality Bowl protein wrap",
            "Jersey Mike's Giant Turkey Sub",
        ],
        "Side": ["None", "Protein bar", "Banana", "Trail mix"],
        "Dessert/Treat": ["None", "Greek yogurt", "Protein bar", "Banana"],
    },
    "Snack": {
        "Drink": ["None", "Water", "Whole milk", "Regular cold coffee"],
        "Main": ["None", "Greek yogurt + granola bowl", "Peanut butter bagel"],
        "Side": ["None", "Trail mix", "Banana", "Protein bar", "2 boiled eggs"],
        "Dessert/Treat": ["None", "Greek yogurt", "Granola serving", "Protein bar", "Banana"],
    },
    "Dinner": {
        "Drink": ["None", "Water", "Whole milk"],
        "Main": ["None", "Rotisserie chicken portion", "Grocery store deli sandwich", "Vitality Bowl protein wrap"],
        "Side": ["None", "Whole wheat bagel", "Rice cup", "Whole wheat bread serving", "2 boiled eggs"],
        "Dessert/Treat": ["None", "Greek yogurt", "Protein bar", "Banana"],
    },
}

GENERAL_MONTHLY = [
    {"Item": "Whey protein", "Category": "Monthly", "Suggested Qty": 1, "Unit": "tub", "Default Price": 60.00, "Storage": "Room temp", "Low Stock At": 10},
    {"Item": "Peanut butter", "Category": "Monthly", "Suggested Qty": 1, "Unit": "large jar", "Default Price": 10.00, "Storage": "Room temp", "Low Stock At": 4},
    {"Item": "Trail mix", "Category": "Monthly", "Suggested Qty": 1, "Unit": "bag", "Default Price": 15.00, "Storage": "Room temp", "Low Stock At": 3},
    {"Item": "Protein bar", "Category": "Monthly", "Suggested Qty": 12, "Unit": "bars", "Default Price": 20.00, "Storage": "Room temp", "Low Stock At": 3},
    {"Item": "Granola", "Category": "Monthly", "Suggested Qty": 1, "Unit": "bag", "Default Price": 8.00, "Storage": "Room temp", "Low Stock At": 3},
]

GENERAL_WEEKLY = [
    {"Item": "Whole milk", "Category": "Weekly", "Suggested Qty": 128, "Unit": "oz", "Default Price": 8.00, "Storage": "Mini fridge", "Low Stock At": 32},
    {"Item": "Bagel", "Category": "Weekly", "Suggested Qty": 12, "Unit": "bagels", "Default Price": 8.00, "Storage": "Room temp", "Low Stock At": 3},
    {"Item": "Whole wheat bagel", "Category": "Weekly", "Suggested Qty": 6, "Unit": "bagels", "Default Price": 5.00, "Storage": "Room temp", "Low Stock At": 2},
    {"Item": "Banana", "Category": "Weekly", "Suggested Qty": 14, "Unit": "bananas", "Default Price": 4.00, "Storage": "Room temp", "Low Stock At": 3},
    {"Item": "Greek yogurt", "Category": "Weekly", "Suggested Qty": 8, "Unit": "servings", "Default Price": 8.00, "Storage": "Mini fridge", "Low Stock At": 2},
    {"Item": "Boiled eggs", "Category": "Weekly", "Suggested Qty": 12, "Unit": "eggs", "Default Price": 7.00, "Storage": "Mini fridge", "Low Stock At": 2},
    {"Item": "Rotisserie chicken portion", "Category": "Weekly", "Suggested Qty": 6, "Unit": "portions", "Default Price": 10.00, "Storage": "Mini fridge", "Low Stock At": 1},
    {"Item": "Rice cup", "Category": "Weekly", "Suggested Qty": 4, "Unit": "cups", "Default Price": 5.00, "Storage": "Room temp", "Low Stock At": 1},
    {"Item": "Whole wheat bread serving", "Category": "Weekly", "Suggested Qty": 6, "Unit": "servings", "Default Price": 5.00, "Storage": "Room temp", "Low Stock At": 2},
    {"Item": "Cold coffee", "Category": "Weekly", "Suggested Qty": 7, "Unit": "servings", "Default Price": 5.00, "Storage": "Room temp/fridge", "Low Stock At": 2},
]

RESTAURANT_ITEMS = [
    {"Item": "Subway Footlong Turkey", "Category": "Restaurant", "Suggested Qty": 1, "Unit": "meal", "Default Price": 12.00, "Storage": "Buy fresh", "Low Stock At": 0},
    {"Item": "Subway Footlong Rotisserie Chicken", "Category": "Restaurant", "Suggested Qty": 1, "Unit": "meal", "Default Price": 13.00, "Storage": "Buy fresh", "Low Stock At": 0},
    {"Item": "Grocery store deli sandwich", "Category": "Restaurant", "Suggested Qty": 1, "Unit": "meal", "Default Price": 7.00, "Storage": "Buy fresh", "Low Stock At": 0},
    {"Item": "Vitality Bowl protein wrap", "Category": "Restaurant", "Suggested Qty": 1, "Unit": "meal", "Default Price": 15.00, "Storage": "Buy fresh", "Low Stock At": 0},
    {"Item": "Jersey Mike's Giant Turkey Sub", "Category": "Restaurant", "Suggested Qty": 1, "Unit": "meal", "Default Price": 15.00, "Storage": "Buy fresh", "Low Stock At": 0},
]

GENERAL_GROCERY = GENERAL_MONTHLY + GENERAL_WEEKLY


# =========================================================
# GOOGLE SHEETS HELPERS
# =========================================================
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

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
    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPE)
    client = gspread.authorize(creds)
    name = st.secrets["spreadsheet_name"]
    try:
        return client.open(name)
    except gspread.SpreadsheetNotFound:
        return client.create(name)

def get_or_create_worksheet(spreadsheet, title, headers):
    """
    Safely gets or creates a worksheet.
    Uses a small starting size to avoid Google Sheets API/cell limit issues.
    """
    try:
        worksheet = spreadsheet.worksheet(title)
    except Exception:
        try:
            worksheet = spreadsheet.add_worksheet(
                title=title,
                rows=100,
                cols=max(12, len(headers))
            )
            worksheet.append_row(headers)
            return worksheet
        except Exception as e:
            st.error(f"Could not create the Google Sheet tab: {title}")
            st.caption(str(e))
            return None

    # Try to make sure the header row exists without crashing the app
    try:
        first_row = worksheet.row_values(1)
        if not first_row:
            worksheet.append_row(headers)
    except Exception as e:
        st.warning(f"Could not verify headers for tab: {title}")
        st.caption(str(e))

    return worksheet

def clean_df_for_sheets(df, headers):
    if df.empty:
        return []
    df = df.copy()
    for col in headers:
        if col not in df.columns:
            df[col] = ""
    df = df[headers].fillna("")
    rows = []
    for _, row in df.iterrows():
        clean = []
        for value in row.tolist():
            if pd.isna(value):
                clean.append("")
            elif isinstance(value, (int, float, str, bool)):
                clean.append(value)
            else:
                clean.append(str(value))
        rows.append(clean)
    return rows

def rewrite_sheet(title, headers, df):
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False, "Google Sheets is not connected."

    worksheet = get_or_create_worksheet(spreadsheet, title, headers)
    if worksheet is None:
        return False, f"Could not access tab: {title}"

    try:
        worksheet.clear()
        worksheet.append_row(headers)
        rows = clean_df_for_sheets(df, headers)
        if rows:
            worksheet.append_rows(rows, value_input_option="USER_ENTERED")
        return True, f"{title} updated."
    except Exception as e:
        st.error(f"Could not write to tab: {title}")
        st.caption(str(e))
        return False, str(e)

def append_sheet(title, headers, df):
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False, "Google Sheets is not connected."

    worksheet = get_or_create_worksheet(spreadsheet, title, headers)
    if worksheet is None:
        return False, f"Could not access tab: {title}"

    try:
        rows = clean_df_for_sheets(df, headers)
        if rows:
            worksheet.append_rows(rows, value_input_option="USER_ENTERED")
        return True, f"{title} saved."
    except Exception as e:
        st.error(f"Could not append to tab: {title}")
        st.caption(str(e))
        return False, str(e)

def read_sheet(title, headers):
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return pd.DataFrame(columns=headers)

    worksheet = get_or_create_worksheet(spreadsheet, title, headers)
    if worksheet is None:
        return pd.DataFrame(columns=headers)

    try:
        records = worksheet.get_all_records()
    except Exception as e:
        st.warning(f"Could not read tab: {title}")
        st.caption(str(e))
        return pd.DataFrame(columns=headers)

    if not records:
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(records)
    for col in headers:
        if col not in df.columns:
            df[col] = ""
    return df[headers]


# =========================================================
# SHEET SCHEMAS
# =========================================================
def daily_headers():
    return ["saved_at", "plan_date", "meal_slot", "component_slot", "component_name", "calories", "protein", "carbs", "fat", "cost", "ingredients_json"]

def shopping_headers():
    return ["shopping_id", "saved_at", "item", "category", "qty_bought", "unit", "unit_price", "total_cost", "storage"]

def inventory_headers():
    return ["item", "category", "qty_on_hand", "unit", "last_unit_price", "storage", "low_stock_at", "last_updated"]

def budget_headers():
    return ["date", "type", "description", "amount"]

def food_coach_headers():
    return ["item", "category", "suggested_qty", "unit", "default_price", "storage", "low_stock_at", "notes"]


# =========================================================
# DATA READ / WRITE
# =========================================================
def read_daily_logs():
    df = read_sheet("Daily_Logs", daily_headers())
    for col in ["calories", "protein", "carbs", "fat", "cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def read_shopping_trips():
    df = read_sheet("Shopping_Trips", shopping_headers())
    for col in ["qty_bought", "unit_price", "total_cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def read_inventory():
    df = read_sheet("Inventory", inventory_headers())
    for col in ["qty_on_hand", "last_unit_price", "low_stock_at"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def read_budget_logs():
    df = read_sheet("Budget_Log", budget_headers())
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    return df

def read_food_coach_input():
    df = read_sheet("Food_Coach_Input", food_coach_headers())
    for col in ["suggested_qty", "default_price", "low_stock_at"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def append_food_coach_item(item, category, qty, unit, price, storage, low_stock_at, notes):
    df = pd.DataFrame([{
        "item": item,
        "category": category,
        "suggested_qty": float(qty),
        "unit": unit,
        "default_price": float(price),
        "storage": storage,
        "low_stock_at": float(low_stock_at),
        "notes": notes,
    }])
    return append_sheet("Food_Coach_Input", food_coach_headers(), df)

def setup_required_tabs():
    """
    Optional setup button helper. Creates all required tabs cleanly.
    """
    if not google_sheets_is_configured():
        return False, "Google Sheets is not connected."

    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False, "Could not open spreadsheet."

    required = [
        ("Daily_Logs", daily_headers()),
        ("Shopping_Trips", shopping_headers()),
        ("Inventory", inventory_headers()),
        ("Budget_Log", budget_headers()),
    ]

    for title, headers in required:
        ws = get_or_create_worksheet(spreadsheet, title, headers)
        if ws is None:
            return False, f"Could not create/access {title}"

    return True, "Required Google Sheets tabs are ready."

def save_budget_entry(entry_date, entry_type, description, amount):
    df = pd.DataFrame([{
        "date": str(entry_date),
        "type": entry_type,
        "description": description,
        "amount": float(amount)
    }])
    return append_sheet("Budget_Log", budget_headers(), df)

def update_inventory_with_purchase(shopping_df):
    inventory = read_inventory()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if inventory.empty:
        inventory = pd.DataFrame(columns=inventory_headers())

    for _, row in shopping_df.iterrows():
        item = str(row["item"])
        qty = float(row["qty_bought"])
        if qty <= 0:
            continue

        category = str(row.get("category", ""))
        unit = str(row.get("unit", ""))
        unit_price = float(row.get("unit_price", 0))
        storage = str(row.get("storage", ""))
        low_stock_at = float(row.get("low_stock_at", 0)) if "low_stock_at" in row else 0

        match = inventory["item"].astype(str) == item if not inventory.empty else pd.Series(dtype=bool)

        if not inventory.empty and match.any():
            idx = inventory[match].index[0]
            inventory.loc[idx, "qty_on_hand"] = float(inventory.loc[idx, "qty_on_hand"]) + qty
            inventory.loc[idx, "last_unit_price"] = unit_price
            inventory.loc[idx, "last_updated"] = now
        else:
            inventory = pd.concat([inventory, pd.DataFrame([{
                "item": item,
                "category": category,
                "qty_on_hand": qty,
                "unit": unit,
                "last_unit_price": unit_price,
                "storage": storage,
                "low_stock_at": low_stock_at,
                "last_updated": now
            }])], ignore_index=True)

    rewrite_sheet("Inventory", inventory_headers(), inventory)
    return inventory

def deduct_inventory(ingredients):
    inventory = read_inventory()
    if inventory.empty:
        return False, "No inventory found yet. Use Shopping Mode first."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item, qty_used in ingredients.items():
        match = inventory["item"].astype(str) == str(item)
        if match.any():
            idx = inventory[match].index[0]
            inventory.loc[idx, "qty_on_hand"] = max(float(inventory.loc[idx, "qty_on_hand"]) - float(qty_used), 0)
            inventory.loc[idx, "last_updated"] = now

    rewrite_sheet("Inventory", inventory_headers(), inventory)
    return True, "Inventory deducted based on saved meals."

def save_day(plan_date, selections, deduct=True):
    rows = []
    ingredients_used = {}
    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for meal_slot, meal_data in selections.items():
        if not meal_data["include"]:
            continue
        for component_slot, comp in meal_data["components"].items():
            if comp["name"] == "None":
                continue
            rows.append({
                "saved_at": saved_at,
                "plan_date": str(plan_date),
                "meal_slot": meal_slot,
                "component_slot": component_slot,
                "component_name": comp["name"],
                "calories": comp["calories"],
                "protein": comp["protein"],
                "carbs": comp["carbs"],
                "fat": comp["fat"],
                "cost": comp["cost"],
                "ingredients_json": json.dumps(comp["ingredients"]),
            })
            for item, qty in comp["ingredients"].items():
                ingredients_used[item] = ingredients_used.get(item, 0) + qty

    if not rows:
        return False, "No included meals to save."

    existing = read_daily_logs()
    if not existing.empty:
        existing = existing[existing["plan_date"].astype(str) != str(plan_date)]
    new_df = pd.DataFrame(rows)
    combined = pd.concat([existing, new_df], ignore_index=True) if not existing.empty else new_df
    rewrite_sheet("Daily_Logs", daily_headers(), combined)

    if deduct:
        deduct_inventory(ingredients_used)

    meal_cost = float(new_df["cost"].sum())
    save_budget_entry(plan_date, "Meal Plan Estimated Cost", "Included meal components", meal_cost)

    return True, f"Saved {len(rows)} items for {plan_date}."


# =========================================================
# APP HELPERS
# =========================================================
def component_names(slot, meal_slot=None):
    if meal_slot and meal_slot in MEAL_ALLOWED_OPTIONS:
        allowed = MEAL_ALLOWED_OPTIONS[meal_slot].get(slot, [])
        return allowed + ["Other / Custom"]
    return [x["name"] for x in COMPONENTS[slot]] + ["Other / Custom"]

def get_component(slot, name):
    for x in COMPONENTS[slot]:
        if x["name"] == name:
            return x
    return COMPONENTS[slot][0]

def make_custom_component(name, calories, protein, carbs, fat, cost):
    return {
        "name": name if name else "Custom item",
        "calories": float(calories),
        "protein": float(protein),
        "carbs": float(carbs),
        "fat": float(fat),
        "cost": float(cost),
        "ingredients": {name if name else "Custom item": 1}
    }

def totals_from_components(components):
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0}
    for comp in components:
        totals["calories"] += float(comp["calories"])
        totals["protein"] += float(comp["protein"])
        totals["carbs"] += float(comp["carbs"])
        totals["fat"] += float(comp["fat"])
        totals["cost"] += float(comp["cost"])
    return totals

def load_saved_day_defaults(plan_date):
    logs = read_daily_logs()
    if logs.empty:
        return {}
    d = logs[logs["plan_date"].astype(str) == str(plan_date)]
    defaults = {}
    for _, row in d.iterrows():
        defaults[(row["meal_slot"], row["component_slot"])] = row["component_name"]
    return defaults

def grocery_from_selections(selections):
    items = {}
    for meal_data in selections.values():
        if not meal_data["include"]:
            continue
        for comp in meal_data["components"].values():
            for item, qty in comp["ingredients"].items():
                items[item] = items.get(item, 0) + qty

    if not items:
        return pd.DataFrame(columns=["Item", "Estimated Used", "Unit Cost", "Estimated Cost Used"])

    prices = item_unit_price_lookup()
    rows = []
    for item, qty in items.items():
        unit_cost = float(prices.get(item, 0))
        rows.append({
            "Item": item,
            "Estimated Used": qty,
            "Unit Cost": round(unit_cost, 2),
            "Estimated Cost Used": round(unit_cost * float(qty), 2)
        })
    return pd.DataFrame(rows).sort_values("Item")

def low_stock_alerts():
    inv = read_inventory()
    if inv.empty:
        return pd.DataFrame(columns=inventory_headers())
    return inv[(inv["low_stock_at"] > 0) & (inv["qty_on_hand"] <= inv["low_stock_at"])].copy()

def week_start(d):
    d = pd.to_datetime(d).date()
    return d - timedelta(days=d.weekday())

def spending_summary():
    shopping = read_shopping_trips()
    budget = read_budget_logs()

    rows = []
    if not shopping.empty:
        for _, r in shopping.iterrows():
            rows.append({
                "date": str(r["saved_at"])[:10],
                "source": "Shopping",
                "amount": float(r["total_cost"])
            })
    if not budget.empty:
        for _, r in budget.iterrows():
            rows.append({
                "date": str(r["date"]),
                "source": str(r["type"]),
                "amount": float(r["amount"])
            })

    if not rows:
        return pd.DataFrame(columns=["date", "source", "amount"])

    return pd.DataFrame(rows)

def get_recommended_grocery_items():
    coach_df = read_food_coach_input()
    if not coach_df.empty and coach_df["item"].astype(str).str.strip().ne("").any():
        df = coach_df.copy()
        df = df[df["item"].astype(str).str.strip() != ""]
        df = df.rename(columns={
            "item": "Item",
            "category": "Category",
            "suggested_qty": "Suggested Qty",
            "unit": "Unit",
            "default_price": "Default Price",
            "storage": "Storage",
            "low_stock_at": "Low Stock At",
        })
        return df[["Item", "Category", "Suggested Qty", "Unit", "Default Price", "Storage", "Low Stock At"]]
    return pd.DataFrame(GENERAL_GROCERY)

def make_shopping_base_list():
    base = get_recommended_grocery_items()
    base["Buy"] = True
    base["Suggested Qty"] = pd.to_numeric(base["Suggested Qty"], errors="coerce").fillna(0)
    base["Default Price"] = pd.to_numeric(base["Default Price"], errors="coerce").fillna(0)
    base["Qty Bought"] = base["Suggested Qty"]
    base["Unit Price"] = base.apply(lambda r: round(float(r["Default Price"]) / float(r["Suggested Qty"]), 2) if float(r["Suggested Qty"]) > 0 else 0, axis=1)
    base["Total Cost"] = base["Default Price"]
    return base[["Buy", "Item", "Category", "Suggested Qty", "Qty Bought", "Unit", "Unit Price", "Total Cost", "Storage", "Low Stock At"]]

def item_unit_price_lookup():
    lookup = {}
    grocery_df = get_recommended_grocery_items()
    for _, r in grocery_df.iterrows():
        item = str(r["Item"])
        qty = float(pd.to_numeric(r["Suggested Qty"], errors="coerce") or 0)
        price = float(pd.to_numeric(r["Default Price"], errors="coerce") or 0)
        lookup[item] = price / qty if qty > 0 else price
    for r in RESTAURANT_ITEMS:
        lookup[r["Item"]] = float(r["Default Price"])
    return lookup


# =========================================================
# HEADER + TOP NAV
# =========================================================
st.markdown("""
<div class="hero-wrap">
    <div class="honey-pill">🍯 Client Fuel Portal</div>
    <div class="hero-title">🐻 Pooh Bear Yum Yum Tracker 🐝</div>
    <div class="hero-subtitle">Honey-powered meals, groceries, inventory, and budget tracking.</div>
</div>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "🏠 Overview"

nav_cols = st.columns(4)
with nav_cols[0]:
    if st.button("🏠 Overview"):
        st.session_state.page = "🏠 Overview"
with nav_cols[1]:
    if st.button("🍽️ Meal Builder"):
        st.session_state.page = "🍽️ Meal Builder"
with nav_cols[2]:
    if st.button("🛒 Grocery + Shopping"):
        st.session_state.page = "🛒 Grocery + Shopping"
with nav_cols[3]:
    if st.button("📊 History + Budget"):
        st.session_state.page = "📊 History + Budget"

page = st.session_state.page

st.markdown("---")

if not google_sheets_is_configured():
    st.warning("Google Sheets is not connected yet. The app layout works, but saving/inventory/history need Google Sheets.")

# =========================================================
# PAGE 1: OVERVIEW
# =========================================================
if page == "🏠 Overview":
    st.subheader("Overview")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="section-card">
            <h3>🐻 Client Details</h3>
            <b>Name:</b> {CLIENT['name']}<br>
            <b>Goal:</b> {CLIENT['goal']}<br>
            <b>Age:</b> {CLIENT['age']}<br>
            <b>Height:</b> {CLIENT['height']}<br>
            <b>Weight:</b> {CLIENT['weight']}
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="section-card">
            <h3>🎯 Plan Targets</h3>
            <b>Calories:</b> {CLIENT['calorie_target']}<br>
            <b>Protein:</b> {CLIENT['protein_target']}<br>
            <b>Budget:</b> ${CLIENT['weekly_budget']}/week<br>
            <b>Lifestyle:</b> {CLIENT['lifestyle']}
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Cost + Budget Snapshot")

    shopping = read_shopping_trips()
    meals = read_daily_logs()
    budget_logs = read_budget_logs()

    total_shopping = float(shopping["total_cost"].sum()) if not shopping.empty else 0
    total_meal_estimate = float(meals["cost"].sum()) if not meals.empty else 0
    total_extra_budget = float(budget_logs["amount"].sum()) if not budget_logs.empty else 0

    today = date.today()
    week = week_start(today)
    week_end = week + timedelta(days=6)

    spend_df = spending_summary()
    if not spend_df.empty:
        spend_df["date_dt"] = pd.to_datetime(spend_df["date"], errors="coerce")
        week_spend = spend_df[(spend_df["date_dt"].dt.date >= week) & (spend_df["date_dt"].dt.date <= week_end)]["amount"].sum()
    else:
        week_spend = 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Shopping Spend", f"${total_shopping:.2f}")
    m2.metric("Meal Cost So Far", f"${total_meal_estimate:.2f}")
    m3.metric("Logged Budget Total", f"${total_extra_budget:.2f}")
    m4.metric("This Week Spend", f"${week_spend:.2f}", delta=f"${CLIENT['weekly_budget'] - week_spend:.2f} left")

    st.subheader("Low Stock Notifications")
    alerts = low_stock_alerts()
    if alerts.empty:
        st.success("No low-stock alerts right now.")
    else:
        st.warning("Some items are running low.")
        st.dataframe(alerts[["item", "qty_on_hand", "unit", "low_stock_at", "storage"]], use_container_width=True, hide_index=True)

    st.subheader("Spending Trend")
    if spend_df.empty:
        st.info("No spending history yet. Use Shopping Mode or save meal days first.")
    else:
        daily = spend_df.groupby("date", as_index=False)["amount"].sum()
        daily["daily_budget"] = CLIENT["weekly_budget"] / 7
        daily["difference"] = daily["daily_budget"] - daily["amount"]
        st.dataframe(daily, use_container_width=True, hide_index=True)
        st.line_chart(daily.set_index("date")[["amount", "daily_budget"]])


# =========================================================
# PAGE 2: MEAL BUILDER
# =========================================================
elif page == "🍽️ Meal Builder":
    selected_date = st.date_input("Select day/date", value=date.today(), key="meal_date")
    st.subheader(f"Meal Builder — {selected_date.strftime('%A, %b %d, %Y')}")

    saved_defaults = {}
    if google_sheets_is_configured():
        try:
            saved_defaults = load_saved_day_defaults(selected_date)
        except Exception as e:
            st.error("Could not load saved meal defaults.")
            st.caption(str(e))

    selections = {}

    for meal_slot in MEAL_SLOTS:
        selections[meal_slot] = {"include": False, "components": {}}

        with st.expander(meal_slot, expanded=True):
            include_meal = st.checkbox(
                f"Include {meal_slot}",
                value=True,
                key=f"{selected_date}_{meal_slot}_include"
            )
            selections[meal_slot]["include"] = include_meal

            cols = st.columns(4)
            for i, component_slot in enumerate(COMPONENT_SLOTS):
                with cols[i]:
                    options = component_names(component_slot, meal_slot)
                    default_name = saved_defaults.get((meal_slot, component_slot), DEFAULT_DAY_PLAN[meal_slot][component_slot])
                    default_index = options.index(default_name) if default_name in options else 0

                    chosen = st.selectbox(
                        component_slot,
                        options,
                        index=default_index,
                        key=f"{selected_date}_{meal_slot}_{component_slot}"
                    )

                    if chosen == "Other / Custom":
                        st.caption("Custom values")
                        custom_name = st.text_input("Name", key=f"{selected_date}_{meal_slot}_{component_slot}_custom_name")
                        custom_cal = st.number_input("Cal", min_value=0.0, value=0.0, step=10.0, key=f"{selected_date}_{meal_slot}_{component_slot}_custom_cal")
                        custom_pro = st.number_input("Protein", min_value=0.0, value=0.0, step=1.0, key=f"{selected_date}_{meal_slot}_{component_slot}_custom_pro")
                        custom_carbs = st.number_input("Carbs", min_value=0.0, value=0.0, step=1.0, key=f"{selected_date}_{meal_slot}_{component_slot}_custom_carbs")
                        custom_fat = st.number_input("Fat", min_value=0.0, value=0.0, step=1.0, key=f"{selected_date}_{meal_slot}_{component_slot}_custom_fat")
                        custom_cost = st.number_input("Cost", min_value=0.0, value=0.0, step=0.25, key=f"{selected_date}_{meal_slot}_{component_slot}_custom_cost")
                        comp = make_custom_component(custom_name, custom_cal, custom_pro, custom_carbs, custom_fat, custom_cost)
                    else:
                        comp = get_component(component_slot, chosen)

                    selections[meal_slot]["components"][component_slot] = comp

                    st.markdown(
                        f"""
                        <div class="compact-kpi">
                            <div class="compact-name">{comp['name']}</div>
                            <div class="compact-macro">
                                {comp['calories']:.0f} cal<br>
                                {comp['protein']:.0f}g protein<br>
                                ${comp['cost']:.2f}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            if include_meal:
                totals = totals_from_components(list(selections[meal_slot]["components"].values()))
                st.markdown(
                    f"<div class='meal-total'><b>{meal_slot} Total:</b> "
                    f"{totals['calories']:.0f} cal | {totals['protein']:.0f}g protein | "
                    f"{totals['carbs']:.0f}g carbs | {totals['fat']:.0f}g fat | ${totals['cost']:.2f}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.warning(f"{meal_slot} is skipped. It will not be saved or deducted from inventory.")

    all_components = []
    for meal_slot, meal_data in selections.items():
        if meal_data["include"]:
            all_components.extend(list(meal_data["components"].values()))

    daily_totals = totals_from_components(all_components)

    st.subheader("Live Daily Total")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Calories", f"{daily_totals['calories']:.0f}")
    c2.metric("Protein", f"{daily_totals['protein']:.0f}g")
    c3.metric("Carbs", f"{daily_totals['carbs']:.0f}g")
    c4.metric("Fat", f"{daily_totals['fat']:.0f}g")
    c5.metric("Cost", f"${daily_totals['cost']:.2f}")

    deduct = st.checkbox("Deduct used grocery inventory when saving", value=True)

    if st.button("💾 Save Included Meals + Update Inventory", use_container_width=True):
        ok, msg = save_day(selected_date, selections, deduct=deduct)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

    st.subheader("Grocery Use From This Day")
    grocery_used_df = grocery_from_selections(selections)
    st.dataframe(grocery_used_df, use_container_width=True, hide_index=True)
    used_cost = float(grocery_used_df["Estimated Cost Used"].sum()) if not grocery_used_df.empty and "Estimated Cost Used" in grocery_used_df.columns else 0
    st.markdown(
        f"<div class='grocery-cost-note'><b>Estimated grocery value used today:</b> ${used_cost:.2f}</div>",
        unsafe_allow_html=True
    )


# =========================================================
# PAGE 3: GROCERY + SHOPPING
# =========================================================
elif page == "🛒 Grocery + Shopping":
    st.subheader("General Grocery Lists")
    weekly_budget = st.number_input("Weekly budget", min_value=50, max_value=500, value=CLIENT["weekly_budget"], step=5, key="grocery_budget")
    st.metric("Daily Budget Target", f"${weekly_budget / 7:.2f}")

    st.markdown("### Food Coach Recommended Grocery Plan")
    coach_items_df = get_recommended_grocery_items()
    st.dataframe(coach_items_df, use_container_width=True, hide_index=True)

    st.markdown("### Monthly Buy")
    monthly_df = coach_items_df[coach_items_df["Category"].astype(str).str.lower() == "monthly"] if not coach_items_df.empty else pd.DataFrame(GENERAL_MONTHLY)
    st.dataframe(monthly_df, use_container_width=True, hide_index=True)

    st.markdown("### Weekly Refill")
    weekly_df = coach_items_df[coach_items_df["Category"].astype(str).str.lower() == "weekly"] if not coach_items_df.empty else pd.DataFrame(GENERAL_WEEKLY)
    st.dataframe(weekly_df, use_container_width=True, hide_index=True)

    st.markdown("### Add Item to Food Coach Input")
    with st.expander("➕ Add custom grocery item", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            new_item = st.text_input("Item name")
            new_category = st.selectbox("Category", ["Weekly", "Monthly", "Restaurant", "Custom"])
            new_qty = st.number_input("Suggested quantity", min_value=0.0, value=1.0, step=1.0)
            new_unit = st.text_input("Unit", value="serving")
        with c2:
            new_price = st.number_input("Default total price", min_value=0.0, value=0.0, step=0.25)
            new_storage = st.text_input("Storage", value="Room temp")
            new_low = st.number_input("Low stock alert at", min_value=0.0, value=1.0, step=1.0)
            new_notes = st.text_input("Notes", value="")

        if st.button("Save Item to Food Coach Input"):
            if not new_item.strip():
                st.warning("Add an item name first.")
            else:
                ok, msg = append_food_coach_item(new_item, new_category, new_qty, new_unit, new_price, new_storage, new_low, new_notes)
                if ok:
                    st.success("Item saved to Food_Coach_Input. Refresh the app to see it in the list.")
                else:
                    st.warning(msg)

    st.markdown("---")
    shopping_mode = st.toggle("🛒 Turn On Shopping Mode", value=False)

    if shopping_mode:
        st.subheader("Shopping Mode")
        st.caption("Check what you are buying, edit quantity and price, then save. This updates inventory and shopping spend.")

        shopping_base = make_shopping_base_list()

        edited = st.data_editor(
            shopping_base,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Buy": st.column_config.CheckboxColumn("Buy"),
                "Qty Bought": st.column_config.NumberColumn("Qty Bought", min_value=0.0, step=1.0),
                "Unit Price": st.column_config.NumberColumn("Unit Price", min_value=0.0, step=0.25, format="$%.2f"),
                "Total Cost": st.column_config.NumberColumn("Total Cost", min_value=0.0, step=0.25, format="$%.2f"),
            },
            key="shopping_editor"
        )

        edited["Qty Bought"] = pd.to_numeric(edited["Qty Bought"], errors="coerce").fillna(0)
        edited["Unit Price"] = pd.to_numeric(edited["Unit Price"], errors="coerce").fillna(0)

        # Recalculate total cost from qty and unit price
        edited["Total Cost"] = (edited["Qty Bought"] * edited["Unit Price"]).round(2)

        selected = edited[(edited["Buy"] == True) & (edited["Qty Bought"] > 0)].copy()
        shopping_total = float(selected["Total Cost"].sum()) if not selected.empty else 0

        st.metric("Shopping Total", f"${shopping_total:.2f}")

        st.markdown("### Add Custom Items")
        custom_text = st.text_area(
            "Optional: add custom items, one per line as: item, qty, unit, unit_price",
            placeholder="Example:\nApples, 6, apples, 0.50\nLow sodium bread, 1, loaf, 4.99"
        )

        custom_rows = []
        if custom_text.strip():
            for line in custom_text.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 4:
                    try:
                        custom_rows.append({
                            "Buy": True,
                            "Item": parts[0],
                            "Category": "Custom",
                            "Suggested Qty": float(parts[1]),
                            "Qty Bought": float(parts[1]),
                            "Unit": parts[2],
                            "Unit Price": float(parts[3]),
                            "Total Cost": float(parts[1]) * float(parts[3]),
                            "Storage": "",
                            "Low Stock At": 1
                        })
                    except ValueError:
                        st.warning(f"Could not read custom item line: {line}")

        if custom_rows:
            custom_df = pd.DataFrame(custom_rows)
            st.dataframe(custom_df, use_container_width=True, hide_index=True)
            shopping_total += float(custom_df["Total Cost"].sum())
            st.metric("Updated Total with Custom Items", f"${shopping_total:.2f}")

        if st.button("✅ End Shopping Mode + Save Purchases", use_container_width=True):
            if selected.empty and not custom_rows:
                st.warning("No purchased items selected.")
            else:
                save_df = selected.copy()
                if custom_rows:
                    save_df = pd.concat([save_df, pd.DataFrame(custom_rows)], ignore_index=True)

                shopping_id = datetime.now().strftime("%Y%m%d%H%M%S")
                saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                trip_df = pd.DataFrame([{
                    "shopping_id": shopping_id,
                    "saved_at": saved_at,
                    "item": row["Item"],
                    "category": row["Category"],
                    "qty_bought": row["Qty Bought"],
                    "unit": row["Unit"],
                    "unit_price": row["Unit Price"],
                    "total_cost": row["Total Cost"],
                    "storage": row["Storage"],
                } for _, row in save_df.iterrows()])

                ok, msg = append_sheet("Shopping_Trips", shopping_headers(), trip_df)
                if ok:
                    inv_update_df = save_df.rename(columns={
                        "Item": "item",
                        "Category": "category",
                        "Qty Bought": "qty_bought",
                        "Unit": "unit",
                        "Unit Price": "unit_price",
                        "Storage": "storage",
                        "Low Stock At": "low_stock_at"
                    })
                    update_inventory_with_purchase(inv_update_df)
                    save_budget_entry(date.today(), "Shopping Trip", "Shopping mode purchase", shopping_total)
                    st.success("Shopping trip saved and inventory updated.")
                else:
                    st.warning(msg)

    st.markdown("---")
    st.subheader("Current Inventory")
    inv = read_inventory()
    if inv.empty:
        st.info("No inventory yet. Use Shopping Mode to add purchased groceries.")
    else:
        st.dataframe(inv, use_container_width=True, hide_index=True)


# =========================================================
# PAGE 4: HISTORY + BUDGET
# =========================================================
elif page == "📊 History + Budget":
    st.subheader("Previous Days + Budget Tracking")

    if google_sheets_is_configured():
        with st.expander("Google Sheets Setup / Repair", expanded=False):
            st.caption("Use this only if Google Sheets tabs are missing or broken.")
            if st.button("Create / Repair Required Google Sheet Tabs"):
                ok, msg = setup_required_tabs()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


    logs = read_daily_logs()

    if logs.empty:
        st.info("No saved meal days yet.")
    else:
        saved_dates = sorted(logs["plan_date"].astype(str).unique(), reverse=True)
        selected_history_date = st.selectbox("Click/select a saved day", saved_dates)

        day_df = logs[logs["plan_date"].astype(str) == selected_history_date].copy()
        totals = day_df[["calories", "protein", "carbs", "fat", "cost"]].sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Calories", f"{totals['calories']:.0f}")
        c2.metric("Protein", f"{totals['protein']:.0f}g")
        c3.metric("Carbs", f"{totals['carbs']:.0f}g")
        c4.metric("Fat", f"{totals['fat']:.0f}g")
        c5.metric("Cost", f"${totals['cost']:.2f}")

        st.dataframe(
            day_df[["meal_slot", "component_slot", "component_name", "calories", "protein", "carbs", "fat", "cost"]],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.subheader("Spending Tracking Graph")

    weekly_budget = st.number_input("Weekly budget for graph", min_value=50, max_value=500, value=CLIENT["weekly_budget"], step=5, key="budget_graph")
    daily_budget = weekly_budget / 7

    spend_df = spending_summary()
    if spend_df.empty:
        st.info("No spending data yet.")
    else:
        daily = spend_df.groupby("date", as_index=False)["amount"].sum()
        daily["daily_budget"] = daily_budget
        daily["above_below_budget"] = daily["daily_budget"] - daily["amount"]

        st.dataframe(daily, use_container_width=True, hide_index=True)

        chart_df = daily.set_index("date")[["amount", "daily_budget"]]
        st.line_chart(chart_df)

        st.markdown("### Above / Below Budget")
        st.bar_chart(daily.set_index("date")[["above_below_budget"]])

    st.markdown("---")
    st.subheader("Shopping History")
    trips = read_shopping_trips()
    if trips.empty:
        st.info("No shopping trips saved yet.")
    else:
        st.dataframe(trips, use_container_width=True, hide_index=True)


st.markdown("---")
st.markdown("<div class='footer-honey'>🍯 Made by Honey</div>", unsafe_allow_html=True)
