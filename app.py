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
# THEME-AWARE CSS
# =========================================================
st.markdown("""
<style>
    :root {
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
        --kpi-bg: #ffffff;
        --kpi-border: #D6DCE5;
        --kpi-text: #1f2933;
        --success-bg: #EAF7EF;
        --success-border: #6BCB88;
        --success-text: #14532D;
        --warn-bg: #FFF7E6;
        --warn-border: #E8B64B;
        --warn-text: #5C3B1E;
        --button-bg: #FFF7E6;
        --button-text: #5C3B1E;
        --button-hover: #FFE8A3;
        --shadow: rgba(15, 23, 42, 0.10);
    }

    @media (prefers-color-scheme: dark) {
        :root {
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
            --kpi-bg: #11151c;
            --kpi-border: #30343d;
            --kpi-text: #F8FAFC;
            --success-bg: #102318;
            --success-border: #245c35;
            --success-text: #D1FAE5;
            --warn-bg: #3a2411;
            --warn-border: #cc8a22;
            --warn-text: #FFF7E6;
            --button-bg: #17120A;
            --button-text: #FFD95A;
            --button-hover: #2B1A0B;
            --shadow: rgba(0, 0, 0, 0.25);
        }
    }

    .hero-wrap {
        text-align: center;
        background:
            radial-gradient(circle at top, rgba(255,217,90,0.38) 0%, rgba(255,217,90,0.12) 34%, transparent 70%),
            linear-gradient(135deg, var(--honey-soft), var(--card-bg));
        border: 1px solid var(--honey-border);
        border-radius: 28px;
        padding: 26px 18px;
        margin-bottom: 18px;
        box-shadow: 0 0 25px var(--shadow);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 950;
        color: var(--honey);
        margin-bottom: 6px;
        line-height: 1.05;
        text-shadow: 0 2px 0 rgba(92,59,30,0.35);
    }

    .hero-subtitle {
        font-size: 16px;
        color: var(--app-text);
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

    .compact-kpi {
        background: var(--kpi-bg);
        color: var(--kpi-text);
        border: 1px solid var(--kpi-border);
        border-radius: 14px;
        padding: 10px 12px;
        margin-top: 8px;
        min-height: 96px;
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

    .meal-total,
    .cost-box {
        background: var(--success-bg);
        color: var(--success-text);
        border: 1px solid var(--success-border);
        padding: 12px;
        border-radius: 12px;
        margin-top: 10px;
        margin-bottom: 14px;
    }

    .soft-warning {
        background: var(--warn-bg);
        color: var(--warn-text);
        border: 1px solid var(--warn-border);
        padding: 12px;
        border-radius: 12px;
        margin-top: 10px;
        margin-bottom: 14px;
    }

    .footer-honey {
        text-align: center;
        color: var(--honey);
        font-weight: 800;
        padding: 18px;
        margin-top: 28px;
    }

    @media (max-width: 768px) {
        .hero-title { font-size: 30px; }
        .hero-subtitle { font-size: 14px; }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }

    .shopping-card {
        background: var(--kpi-bg);
        color: var(--kpi-text);
        border: 1px solid var(--kpi-border);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px var(--shadow);
    }
    .shopping-title {
        font-size: 16px;
        font-weight: 850;
        color: var(--honey);
        margin-bottom: 6px;
    }
    .shopping-meta {
        font-size: 13px;
        line-height: 1.45;
        color: var(--app-text);
        margin-bottom: 8px;
    }
    .cart-card {
        background: var(--success-bg);
        color: var(--success-text);
        border: 1px solid var(--success-border);
        border-radius: 16px;
        padding: 16px;
        margin-top: 16px;
        margin-bottom: 16px;
        font-weight: 800;
    }


    .filter-status {
        background: var(--warn-bg);
        color: var(--warn-text);
        border: 1px solid var(--warn-border);
        border-radius: 14px;
        padding: 12px;
        margin: 10px 0 14px 0;
        font-size: 14px;
        line-height: 1.5;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# CLIENT TARGETS
# =========================================================
CLIENT = {
    "name": "Pooh Bear",
    "goal": "Lean Bulk",
    "age": 27,
    "height": "6'0",
    "weight": "180 lb",
    "calorie_target": "3,600–4,000/day",
    "protein_target": "180–220g/day",
    "weekly_budget": 150,
    "lifestyle": "Driving job, mini fridge only, no kitchen, low-prep meals",
}


# =========================================================
# GOOGLE SHEETS
# =========================================================
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def google_sheets_is_configured():
    return (
        gspread is not None
        and Credentials is not None
        and "gcp_service_account" in st.secrets
        and ("spreadsheet_name" in st.secrets or "spreadsheet_id" in st.secrets)
    )

@st.cache_resource(show_spinner=False)
def get_spreadsheet():
    """
    Connects to the exact Google Sheet.
    Preferred: add spreadsheet_id to Streamlit secrets.
    Fallback: spreadsheet_name.
    """
    if not google_sheets_is_configured():
        return None

    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPE)
    client = gspread.authorize(creds)

    # BEST OPTION: exact file ID from the Google Sheet URL
    spreadsheet_id = st.secrets.get("spreadsheet_id", "")
    if spreadsheet_id:
        try:
            return client.open_by_key(spreadsheet_id)
        except Exception:
            return None

    # Fallback: spreadsheet name. This can accidentally open/create the wrong file
    # if there are duplicates or the service account cannot access the intended sheet.
    sheet_name = st.secrets.get("spreadsheet_name", "")
    if not sheet_name:
        return None

    try:
        return client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        try:
            return client.create(sheet_name)
        except Exception:
            return None

def visible_worksheet_titles(spreadsheet):
    try:
        return [ws.title for ws in spreadsheet.worksheets()]
    except Exception:
        return []

def find_worksheet(spreadsheet, title):
    """
    Finds a worksheet by exact title or by trimmed/lowercase title.
    This helps if Google Sheets has accidental spaces in the tab name.
    """
    try:
        return spreadsheet.worksheet(title)
    except Exception:
        pass

    wanted = str(title).strip().lower()
    try:
        for ws in spreadsheet.worksheets():
            if str(ws.title).strip().lower() == wanted:
                return ws
    except Exception:
        return None

    return None

def get_or_create_worksheet(spreadsheet, title, headers):
    if spreadsheet is None:
        return None

    ws = find_worksheet(spreadsheet, title)

    if ws is None:
        try:
            ws = spreadsheet.add_worksheet(title=title, rows=100, cols=max(12, len(headers)))
            ws.update("A1", [headers])
            return ws
        except Exception:
            return None

    try:
        first_row = ws.row_values(1)
        if not first_row:
            ws.update("A1", [headers])
    except Exception:
        pass

    return ws

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
        clean_row = []
        for value in row.tolist():
            if pd.isna(value):
                clean_row.append("")
            elif isinstance(value, (int, float, str, bool)):
                clean_row.append(value)
            else:
                clean_row.append(str(value))
        rows.append(clean_row)

    return rows

def normalize_header(value):
    return str(value).strip().replace(" ", "_").lower()

def read_sheet(title, headers):
    """
    Robust Google Sheets reader.
    Reads raw values instead of relying on get_all_records(), which can fail
    with formatted/table-style Google Sheet uploads.
    """
    ss = get_spreadsheet()
    if ss is None:
        return pd.DataFrame(columns=headers)

    ws = get_or_create_worksheet(ss, title, headers)
    if ws is None:
        st.info(f"Google Sheet tab '{title}' is not ready yet.")
        try:
            st.caption(f"Connected spreadsheet: {ss.title} | ID: {ss.id}")
            st.caption("Tabs visible to the app: " + ", ".join(visible_worksheet_titles(ss)))
        except Exception:
            pass
        return pd.DataFrame(columns=headers)

    try:
        values = ws.get_all_values()
    except Exception as e:
        st.warning(f"Could not read values from tab: {title}")
        st.caption(str(e))
        return pd.DataFrame(columns=headers)

    if not values or len(values) < 2:
        return pd.DataFrame(columns=headers)

    expected = [normalize_header(h) for h in headers]
    header_row_idx = None
    header_values = None

    for i, row in enumerate(values[:10]):
        normalized = [normalize_header(x) for x in row]
        matches = sum(1 for h in expected if h in normalized)
        if matches >= min(3, len(expected)):
            header_row_idx = i
            header_values = row
            break

    if header_row_idx is None:
        st.warning(f"Could not find expected headers in tab: {title}")
        st.caption("First row found: " + str(values[0]))
        return pd.DataFrame(columns=headers)

    normalized_headers = [normalize_header(x) for x in header_values]
    col_map = {}
    for expected_col in headers:
        norm_expected = normalize_header(expected_col)
        if norm_expected in normalized_headers:
            col_map[expected_col] = normalized_headers.index(norm_expected)

    data_rows = values[header_row_idx + 1:]
    parsed_rows = []

    for row in data_rows:
        if not any(str(x).strip() for x in row):
            continue

        parsed = {}
        for col in headers:
            idx = col_map.get(col)
            parsed[col] = row[idx] if idx is not None and idx < len(row) else ""

        parsed_rows.append(parsed)

    if not parsed_rows:
        return pd.DataFrame(columns=headers)

    return pd.DataFrame(parsed_rows)[headers]

def rewrite_sheet(title, headers, df):
    ss = get_spreadsheet()
    if ss is None:
        return False, "Google Sheets is not connected."

    ws = get_or_create_worksheet(ss, title, headers)
    if ws is None:
        return False, f"Could not access tab: {title}"

    try:
        ws.clear()
        ws.update("A1", [headers])
        rows = clean_df_for_sheets(df, headers)
        if rows:
            ws.append_rows(rows, value_input_option="USER_ENTERED")
        return True, f"{title} updated."
    except Exception as e:
        return False, str(e)

def append_sheet(title, headers, df):
    ss = get_spreadsheet()
    if ss is None:
        return False, "Google Sheets is not connected."

    ws = get_or_create_worksheet(ss, title, headers)
    if ws is None:
        return False, f"Could not access tab: {title}"

    try:
        rows = clean_df_for_sheets(df, headers)
        if rows:
            ws.append_rows(rows, value_input_option="USER_ENTERED")
        return True, f"{title} saved."
    except Exception as e:
        return False, str(e)


# =========================================================
# SHEET HEADERS
# =========================================================
def food_options_headers():
    return [
        "meal_slot", "component_slot", "option_name",
        "calories", "protein", "carbs", "fat",
        "cost_estimate", "is_outside_meal",
        "ingredient_name", "ingredient_qty", "ingredient_unit",
        "active", "default_choice"
    ]

def grocery_headers():
    return ["item", "category", "suggested_qty", "unit", "default_price", "storage", "low_stock_at", "suggested_buy", "where_to_buy", "notes"]

def daily_headers():
    return [
        "saved_at", "plan_date", "meal_slot", "component_slot", "component_name",
        "calories", "protein", "carbs", "fat", "cost",
        "cost_type", "ingredients_json"
    ]

def shopping_headers():
    return ["shopping_id", "saved_at", "item", "category", "qty_bought", "unit", "unit_price", "total_cost", "storage"]

def inventory_headers():
    return ["item", "category", "qty_on_hand", "unit", "last_unit_price", "storage", "low_stock_at", "last_updated"]

def budget_headers():
    return ["date", "type", "description", "amount"]


# =========================================================
# EMPTY DEFAULTS
# =========================================================
# The real source of truth should be the Google Sheet tabs:
# Food_Options and Food_Coach_Input.
DEFAULT_FOOD_OPTIONS = []
DEFAULT_GROCERY = []


# =========================================================
# READ DATA
# =========================================================
@st.cache_data(ttl=60)
def read_food_options():
    df = read_sheet("Food_Options", food_options_headers())

    if df.empty or df["option_name"].astype(str).str.strip().eq("").all():
        return pd.DataFrame(DEFAULT_FOOD_OPTIONS, columns=food_options_headers())

    for col in ["calories", "protein", "carbs", "fat", "cost_estimate", "ingredient_qty"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["active"] = df["active"].astype(str).str.lower().isin(["true", "yes", "1", "y"])
    df["default_choice"] = df["default_choice"].astype(str).str.lower().isin(["true", "yes", "1", "y"])
    df["is_outside_meal"] = df["is_outside_meal"].astype(str).str.lower().isin(["true", "yes", "1", "y"])

    df["meal_slot"] = df["meal_slot"].astype(str).str.strip()
    df["component_slot"] = df["component_slot"].astype(str).str.strip()
    df["option_name"] = df["option_name"].astype(str).str.strip()
    df["ingredient_name"] = df["ingredient_name"].astype(str).fillna("").str.strip()
    df["ingredient_unit"] = df["ingredient_unit"].astype(str).fillna("").str.strip()

    df = duplicate_home_and_restaurant_components(df)

    return df

@st.cache_data(ttl=60)
def read_grocery_input():
    df = read_sheet("Food_Coach_Input", grocery_headers())

    if df.empty or df["item"].astype(str).str.strip().eq("").all():
        return pd.DataFrame(DEFAULT_GROCERY, columns=grocery_headers())

    for col in ["suggested_qty", "default_price", "low_stock_at"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["item"] = df["item"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["unit"] = df["unit"].astype(str).str.strip()
    df["storage"] = df["storage"].astype(str).str.strip()
    df["suggested_buy"] = df["suggested_buy"].astype(str).str.strip()
    df["where_to_buy"] = df["where_to_buy"].astype(str).str.strip()
    df["notes"] = df["notes"].astype(str).str.strip()

    return df

def enrich_grocery_for_shopping(grocery_df):
    """
    Adds client-friendly shopping columns.
    Source of truth:
    - suggested_buy from Food_Coach_Input
    - where_to_buy from Food_Coach_Input

    If those cells are blank, the app uses a light fallback so the card is not empty.
    """
    df = grocery_df.copy()

    if "suggested_buy" not in df.columns:
        df["suggested_buy"] = ""
    if "where_to_buy" not in df.columns:
        df["where_to_buy"] = ""

    def clean_text(value):
        value = str(value).strip()
        if value.lower() in ["nan", "none"]:
            return ""
        return value

    def fallback_suggested_buy(item):
        item_l = str(item).strip().lower()
        defaults = {
            "whey protein": "Optimum Nutrition Gold Standard Whey - Vanilla",
            "coffee": "Cold brew or coffee concentrate",
            "whole milk": "Whole milk",
            "pb whole wheat bagel": "Whole wheat bagels + peanut butter",
            "greek yogurt + granola": "Greek yogurt tub/cups + low-sugar granola",
            "greek yogurt banana granola": "Greek yogurt + bananas + granola",
            "overnight oats": "Overnight oats cups",
            "starbucks protein box": "Starbucks Eggs & Cheese Protein Box",
            "4 boiled eggs + bagel": "Pre-boiled eggs + whole wheat bagels",
            "banana": "Bananas",
            "apple": "Apples",
            "orange": "Oranges",
            "side salad": "Salad kit or salad mix",
            "baby carrots": "Baby carrots bag",
            "boiled eggs": "Pre-boiled eggs",
            "greek yogurt cup": "Greek yogurt cups",
            "trail mix": "Trail mix bag",
            "yasso greek yogurt bar": "Yasso Greek yogurt bars",
            "protein bar": "Protein bar box",
            "rice cup": "Microwave rice cups",
            "whole wheat bagel": "Whole wheat bagels",
            "rotisserie chicken portion": "Costco rotisserie chicken",
            "tuna packet": "Low-sodium tuna packets",
            "shrimp cocktail": "Shrimp cocktail",
            "chicken breast": "Pre-cooked chicken breast pack",
            "costco salad": "Costco salad kit",
            "chips": "Single-serve chips",
            "water": "Water",
            "sprite": "Sprite",
            "coke zero": "Coke Zero",
        }
        return defaults.get(item_l, str(item).strip())

    def fallback_where(item, category):
        item_l = str(item).strip().lower()
        if item_l in ["whey protein", "rotisserie chicken portion", "shrimp cocktail", "costco salad"]:
            return "Costco"
        if item_l in ["apple", "orange", "side salad", "baby carrots", "banana"]:
            return "Sprouts"
        if "starbucks" in item_l:
            return "Starbucks"
        if category and str(category).strip().lower() == "as needed":
            return "User choice"
        return "User choice"

    df["Suggested Buy"] = df.apply(
        lambda r: clean_text(r.get("suggested_buy", "")) or fallback_suggested_buy(r.get("item", "")),
        axis=1
    )
    df["Where to Buy"] = df.apply(
        lambda r: clean_text(r.get("where_to_buy", "")) or fallback_where(r.get("item", ""), r.get("category", "")),
        axis=1
    )

    return df



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


# =========================================================
# SETUP / REPAIR
# =========================================================
def setup_required_tabs():
    if not google_sheets_is_configured():
        return False, "Google Sheets is not connected."

    ss = get_spreadsheet()
    if ss is None:
        return False, "Could not open the Google Sheet."

    required = [
        ("Food_Options", food_options_headers()),
        ("Food_Coach_Input", grocery_headers()),
        ("Daily_Logs", daily_headers()),
        ("Shopping_Trips", shopping_headers()),
        ("Inventory", inventory_headers()),
        ("Budget_Log", budget_headers()),
    ]

    failed = []
    for title, headers in required:
        ws = get_or_create_worksheet(ss, title, headers)
        if ws is None:
            failed.append(title)

    if failed:
        return False, "Could not auto-create/access: " + ", ".join(failed)

    st.cache_data.clear()
    return True, "Required Google Sheets tabs are ready."


# =========================================================
# COMPONENT / OPTION LOGIC
# =========================================================
def meal_order():
    return ["Breakfast", "Lunch", "Snack", "Dinner"]

def component_sort_key(component):
    order = {
        "Drink": 1,
        "Restaurant_Main": 2,
        "Home_Main": 3,
        "Main": 4,
        "Snack_Item": 5,
        "Protein": 6,
        "Carb_Meal": 7,
        "Side": 8,
        "Dessert": 9,
        "Dessert/Treat": 9,
    }
    return order.get(component, 99)

def display_component_name(component):
    names = {
        "Restaurant_Main": "Restaurant Main",
        "Home_Main": "Home Main",
        "Snack_Item": "Snack Item",
        "Carb_Meal": "Carb / Meal",
        "Dessert/Treat": "Dessert",
    }
    return names.get(component, component.replace("_", " "))

def component_filter_for_meal(meal_slot, mode=None):
    """
    Controls which component dropdowns appear for Lunch/Dinner.
    Restaurant: Drink, Restaurant_Main, Side, Dessert
    Home: Drink, Protein, Carb_Meal, Side, Dessert
    """
    if meal_slot in ["Lunch", "Dinner"]:
        if mode == "Restaurant":
            return ["Drink", "Restaurant_Main", "Side", "Dessert"]
        if mode == "Home":
            return ["Drink", "Protein", "Carb_Meal", "Side", "Dessert"]
    return None

def duplicate_home_and_restaurant_components(food_df):
    """
    Reuses shared options without requiring duplicate rows:
    - Lunch Home mode can reuse Dinner Protein + Carb_Meal.
    - Dinner Restaurant mode can reuse Lunch Restaurant_Main.
    """
    if food_df.empty:
        return food_df

    additions = []
    existing = set(
        zip(
            food_df["meal_slot"].astype(str),
            food_df["component_slot"].astype(str),
            food_df["option_name"].astype(str),
        )
    )

    # Lunch Home: copy Dinner Protein/Carb_Meal into Lunch
    dinner_home = food_df[
        (food_df["meal_slot"] == "Dinner")
        & (food_df["component_slot"].isin(["Protein", "Carb_Meal"]))
    ].copy()

    for _, row in dinner_home.iterrows():
        new_row = row.copy()
        new_row["meal_slot"] = "Lunch"
        key = ("Lunch", str(new_row["component_slot"]), str(new_row["option_name"]))
        if key not in existing:
            additions.append(new_row)
            existing.add(key)

    # Dinner Restaurant: copy Lunch Restaurant_Main into Dinner
    lunch_restaurant = food_df[
        (food_df["meal_slot"] == "Lunch")
        & (food_df["component_slot"] == "Restaurant_Main")
    ].copy()

    for _, row in lunch_restaurant.iterrows():
        new_row = row.copy()
        new_row["meal_slot"] = "Dinner"
        key = ("Dinner", str(new_row["component_slot"]), str(new_row["option_name"]))
        if key not in existing:
            additions.append(new_row)
            existing.add(key)

    if additions:
        food_df = pd.concat([food_df, pd.DataFrame(additions)], ignore_index=True)

    return food_df

def get_components_for_meal(food_df, meal_slot):
    components = (
        food_df[
            (food_df["meal_slot"] == meal_slot)
            & (food_df["active"] == True)
        ]["component_slot"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    return sorted(components, key=component_sort_key)

def get_options(food_df, meal_slot, component_slot):
    opts = food_df[
        (food_df["meal_slot"] == meal_slot)
        & (food_df["component_slot"] == component_slot)
        & (food_df["active"] == True)
    ].copy()

    if opts.empty:
        opts = pd.DataFrame([{
            "meal_slot": meal_slot,
            "component_slot": component_slot,
            "option_name": "None",
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "cost_estimate": 0,
            "is_outside_meal": False,
            "ingredient_name": "",
            "ingredient_qty": 0,
            "ingredient_unit": "serving",
            "active": True,
            "default_choice": True,
        }])

    # Put "None" first if available, then defaults, then alphabetically-ish by original order.
    opts["_none_sort"] = opts["option_name"].astype(str).str.lower().eq("none").map({True: 0, False: 1})
    opts["_default_sort"] = opts["default_choice"].map({True: 0, False: 1})
    opts = opts.sort_values(["_none_sort", "_default_sort"]).drop(columns=["_none_sort", "_default_sort"])

    return opts

def option_to_component(row):
    return {
        "name": str(row["option_name"]),
        "calories": float(row["calories"]),
        "protein": float(row["protein"]),
        "carbs": float(row["carbs"]),
        "fat": float(row["fat"]),
        "cost_estimate": float(row["cost_estimate"]),
        "is_outside_meal": bool(row["is_outside_meal"]),
        "ingredient_name": str(row["ingredient_name"]) if pd.notna(row["ingredient_name"]) else "",
        "ingredient_qty": float(row["ingredient_qty"]),
        "ingredient_unit": str(row["ingredient_unit"]) if pd.notna(row["ingredient_unit"]) else "",
    }

def totals_from_components(components):
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost": 0}
    for c in components:
        totals["calories"] += c["calories"]
        totals["protein"] += c["protein"]
        totals["carbs"] += c["carbs"]
        totals["fat"] += c["fat"]
        totals["cost"] += c["cost_estimate"]
    return totals


# =========================================================
# COST / INVENTORY LOGIC
# =========================================================
def inventory_unit_prices():
    inv = read_inventory()
    lookup = {}

    if not inv.empty:
        for _, r in inv.iterrows():
            item = str(r["item"]).strip()
            price = float(r["last_unit_price"])
            if item and price > 0:
                lookup[item] = price

    return lookup

def estimated_unit_prices_from_coach():
    grocery = read_grocery_input()
    lookup = {}

    if grocery.empty:
        return lookup

    for _, r in grocery.iterrows():
        item = str(r["item"]).strip()
        qty = float(r["suggested_qty"])
        price = float(r["default_price"])
        if item and qty > 0:
            lookup[item] = price / qty

    return lookup

def cost_breakdown_from_selections(selections):
    actual_prices = inventory_unit_prices()
    estimated_prices = estimated_unit_prices_from_coach()

    rows = []
    grocery_actual = 0
    grocery_estimated = 0
    outside_total = 0

    for meal_slot, meal_data in selections.items():
        if not meal_data["include"]:
            continue

        for component_slot, comp in meal_data["components"].items():
            if comp["name"] == "None":
                continue

            if comp["is_outside_meal"]:
                outside_total += comp["cost_estimate"]
                rows.append({
                    "Meal": meal_slot,
                    "Component": display_component_name(component_slot),
                    "Item": comp["name"],
                    "Type": "Outside Meal",
                    "Qty Used": 1,
                    "Unit": "meal",
                    "Unit Cost": comp["cost_estimate"],
                    "Cost Used": comp["cost_estimate"],
                    "Cost Source": "Outside meal price",
                })
                continue

            item = comp["ingredient_name"]
            qty = comp["ingredient_qty"]
            unit_name = comp["ingredient_unit"]

            if not item or qty <= 0:
                continue

            if item in actual_prices:
                unit_cost = actual_prices[item]
                cost = unit_cost * qty
                source = "Actual shopping price"
                grocery_actual += cost
            elif item in estimated_prices:
                unit_cost = estimated_prices[item]
                cost = unit_cost * qty
                source = "Estimated price"
                grocery_estimated += cost
            else:
                unit_cost = comp["cost_estimate"] / qty if qty > 0 else comp["cost_estimate"]
                cost = comp["cost_estimate"]
                source = "Estimated from food option"
                grocery_estimated += cost

            rows.append({
                "Meal": meal_slot,
                "Component": display_component_name(component_slot),
                "Item": item,
                "Type": "Grocery",
                "Qty Used": qty,
                "Unit": unit_name,
                "Unit Cost": round(unit_cost, 2),
                "Cost Used": round(cost, 2),
                "Cost Source": source,
            })

    if rows:
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(columns=[
            "Meal", "Component", "Item", "Type", "Qty Used",
            "Unit", "Unit Cost", "Cost Used", "Cost Source"
        ])

    return df, grocery_actual, grocery_estimated, outside_total

def save_budget_entry(entry_date, entry_type, description, amount):
    df = pd.DataFrame([{
        "date": str(entry_date),
        "type": entry_type,
        "description": description,
        "amount": float(amount),
    }])
    return append_sheet("Budget_Log", budget_headers(), df)

def deduct_inventory(components):
    inventory = read_inventory()
    if inventory.empty:
        return False, "No inventory found yet. Use Shopping Mode first."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for comp in components:
        if comp["is_outside_meal"]:
            continue

        item = comp["ingredient_name"]
        qty = comp["ingredient_qty"]

        if not item or qty <= 0:
            continue

        match = inventory["item"].astype(str).str.strip() == str(item).strip()
        if match.any():
            idx = inventory[match].index[0]
            inventory.loc[idx, "qty_on_hand"] = max(float(inventory.loc[idx, "qty_on_hand"]) - float(qty), 0)
            inventory.loc[idx, "last_updated"] = now

    rewrite_sheet("Inventory", inventory_headers(), inventory)
    return True, "Inventory deducted."

def save_day(plan_date, selections, deduct=True):
    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cost_df, grocery_actual, grocery_estimated, outside_total = cost_breakdown_from_selections(selections)

    rows = []
    components_to_deduct = []

    for meal_slot, meal_data in selections.items():
        if not meal_data["include"]:
            continue

        for component_slot, comp in meal_data["components"].items():
            if comp["name"] == "None":
                continue

            if comp["is_outside_meal"]:
                cost = comp["cost_estimate"]
                cost_type = "Outside meal"
            else:
                matches = cost_df[
                    (cost_df["Meal"] == meal_slot)
                    & (cost_df["Component"] == display_component_name(component_slot))
                    & (cost_df["Item"] == comp["ingredient_name"])
                    & (cost_df["Type"] == "Grocery")
                ]

                cost = float(matches.iloc[0]["Cost Used"]) if not matches.empty else comp["cost_estimate"]
                cost_type = str(matches.iloc[0]["Cost Source"]) if not matches.empty else "Estimated"

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
                "cost": cost,
                "cost_type": cost_type,
                "ingredients_json": json.dumps({
                    "ingredient_name": comp["ingredient_name"],
                    "ingredient_qty": comp["ingredient_qty"],
                    "ingredient_unit": comp["ingredient_unit"],
                    "is_outside_meal": comp["is_outside_meal"],
                }),
            })

            components_to_deduct.append(comp)

    if not rows:
        return False, "No included meals to save."

    existing = read_daily_logs()
    if not existing.empty:
        existing = existing[existing["plan_date"].astype(str) != str(plan_date)]

    new_df = pd.DataFrame(rows)
    combined = pd.concat([existing, new_df], ignore_index=True) if not existing.empty else new_df
    rewrite_sheet("Daily_Logs", daily_headers(), combined)

    if deduct:
        deduct_inventory(components_to_deduct)

    total_food_cost = grocery_actual + grocery_estimated + outside_total
    save_budget_entry(plan_date, "Food Cost", "Groceries used + outside meals", total_food_cost)

    st.cache_data.clear()

    return True, f"Saved {len(rows)} items for {plan_date}."

def update_inventory_with_purchase(shopping_df):
    inv = read_inventory()
    if inv.empty:
        inv = pd.DataFrame(columns=inventory_headers())

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, r in shopping_df.iterrows():
        item = str(r["item"]).strip()
        qty = float(r["qty_bought"])
        unit_price = float(r["unit_price"])

        if not item or qty <= 0:
            continue

        match = inv["item"].astype(str).str.strip() == item if not inv.empty else pd.Series(dtype=bool)

        if not inv.empty and match.any():
            idx = inv[match].index[0]
            inv.loc[idx, "qty_on_hand"] = float(inv.loc[idx, "qty_on_hand"]) + qty
            inv.loc[idx, "last_unit_price"] = unit_price
            inv.loc[idx, "last_updated"] = now
        else:
            inv = pd.concat([inv, pd.DataFrame([{
                "item": item,
                "category": str(r.get("category", "")),
                "qty_on_hand": qty,
                "unit": str(r.get("unit", "")),
                "last_unit_price": unit_price,
                "storage": str(r.get("storage", "")),
                "low_stock_at": float(r.get("low_stock_at", 0)),
                "last_updated": now,
            }])], ignore_index=True)

    rewrite_sheet("Inventory", inventory_headers(), inv)
    st.cache_data.clear()
    return inv

def low_stock_alerts():
    inv = read_inventory()
    if inv.empty:
        return pd.DataFrame(columns=inventory_headers())

    return inv[
        (inv["low_stock_at"] > 0)
        & (inv["qty_on_hand"] <= inv["low_stock_at"])
    ].copy()

def spending_summary():
    budget = read_budget_logs()
    shopping = read_shopping_trips()

    rows = []

    if not shopping.empty:
        for _, r in shopping.iterrows():
            rows.append({
                "date": str(r["saved_at"])[:10],
                "source": "Shopping",
                "amount": float(r["total_cost"]),
            })

    if not budget.empty:
        for _, r in budget.iterrows():
            rows.append({
                "date": str(r["date"]),
                "source": str(r["type"]),
                "amount": float(r["amount"]),
            })

    if rows:
        return pd.DataFrame(rows)

    return pd.DataFrame(columns=["date", "source", "amount"])

def week_start(d):
    d = pd.to_datetime(d).date()
    return d - timedelta(days=d.weekday())


# =========================================================
# HEADER + NAV
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
# OVERVIEW PAGE
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

    shopping = read_shopping_trips()
    meals = read_daily_logs()
    budget_logs = read_budget_logs()

    total_shopping = float(shopping["total_cost"].sum()) if not shopping.empty else 0
    total_meals = float(meals["cost"].sum()) if not meals.empty else 0
    total_budget = float(budget_logs["amount"].sum()) if not budget_logs.empty else 0

    today = date.today()
    wk = week_start(today)
    wk_end = wk + timedelta(days=6)
    spend_df = spending_summary()

    if not spend_df.empty:
        spend_df["date_dt"] = pd.to_datetime(spend_df["date"], errors="coerce")
        week_spend = spend_df[
            (spend_df["date_dt"].dt.date >= wk)
            & (spend_df["date_dt"].dt.date <= wk_end)
        ]["amount"].sum()
    else:
        week_spend = 0

    st.subheader("Cost + Budget Snapshot")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Shopping Spend", f"${total_shopping:.2f}")
    m2.metric("Food Cost Logged", f"${total_meals:.2f}")
    m3.metric("Budget Log Total", f"${total_budget:.2f}")
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
        st.info("No spending history yet.")
    else:
        daily = spend_df.groupby("date", as_index=False)["amount"].sum()
        daily["daily_budget"] = CLIENT["weekly_budget"] / 7
        daily["difference"] = daily["daily_budget"] - daily["amount"]
        st.dataframe(daily, use_container_width=True, hide_index=True)
        st.line_chart(daily.set_index("date")[["amount", "daily_budget"]])


# =========================================================
# MEAL BUILDER PAGE
# =========================================================
elif page == "🍽️ Meal Builder":
    selected_date = st.date_input("Select day/date", value=date.today(), key="meal_date")
    st.subheader(f"Meal Builder — {selected_date.strftime('%A, %b %d, %Y')}")

    food_df = read_food_options()

    if food_df.empty:
        st.warning("No Food_Options found. The app is connected, but it could not parse rows from the Food_Options tab.")
        ss = get_spreadsheet()
        if ss is not None:
            try:
                ws = find_worksheet(ss, "Food_Options")
                if ws is not None:
                    preview = ws.get_all_values()[:5]
                    st.caption("Food_Options raw preview:")
                    st.write(preview)
            except Exception as e:
                st.caption(str(e))
    else:
        saved = read_daily_logs()
        saved_defaults = {}
        if not saved.empty:
            saved_day = saved[saved["plan_date"].astype(str) == str(selected_date)]
            for _, row in saved_day.iterrows():
                saved_defaults[(row["meal_slot"], row["component_slot"])] = row["component_name"]

        selections = {}

        available_meals = [m for m in meal_order() if m in food_df["meal_slot"].unique()]
        extra_meals = [m for m in food_df["meal_slot"].unique().tolist() if m not in available_meals]
        available_meals += extra_meals

        for meal_slot in available_meals:
            all_components_for_meal = get_components_for_meal(food_df, meal_slot)
            if not all_components_for_meal:
                continue

            selections[meal_slot] = {"include": False, "components": {}}

            with st.expander(meal_slot, expanded=True):
                include = st.checkbox(f"Include {meal_slot}", value=False, key=f"{selected_date}_{meal_slot}_include")
                selections[meal_slot]["include"] = include

                mode = None
                if meal_slot in ["Lunch", "Dinner"]:
                    mode = st.selectbox(
                        f"{meal_slot} type",
                        ["Restaurant", "Home"],
                        index=0 if meal_slot == "Lunch" else 1,
                        key=f"{selected_date}_{meal_slot}_mode",
                    )

                allowed_components = component_filter_for_meal(meal_slot, mode)
                if allowed_components is not None:
                    components = [c for c in allowed_components if c in all_components_for_meal]
                else:
                    components = all_components_for_meal

                # Responsive compact columns, max 4 per row.
                for start_idx in range(0, len(components), 4):
                    chunk = components[start_idx:start_idx + 4]
                    cols = st.columns(len(chunk))

                    for i, component_slot in enumerate(chunk):
                        opts = get_options(food_df, meal_slot, component_slot)
                        names = opts["option_name"].astype(str).tolist()

                        default_name = saved_defaults.get((meal_slot, component_slot), None)
                        if default_name not in names:
                            defaults = opts[opts["default_choice"] == True]
                            if not defaults.empty:
                                default_name = str(defaults.iloc[0]["option_name"])
                            else:
                                none_rows = opts[opts["option_name"].astype(str).str.lower() == "none"]
                                default_name = str(none_rows.iloc[0]["option_name"]) if not none_rows.empty else names[0]

                        default_index = names.index(default_name) if default_name in names else 0

                        with cols[i]:
                            chosen = st.selectbox(
                                display_component_name(component_slot),
                                names,
                                index=default_index,
                                key=f"{selected_date}_{meal_slot}_{mode or 'Default'}_{component_slot}"
                            )

                            row = opts[opts["option_name"].astype(str) == chosen].iloc[0]
                            comp = option_to_component(row)
                            selections[meal_slot]["components"][component_slot] = comp

                            st.markdown(
                                f"""
                                <div class="compact-kpi">
                                    <div class="compact-name">{comp['name']}</div>
                                    {comp['calories']:.0f} cal<br>
                                    {comp['protein']:.0f}g protein<br>
                                    ${comp['cost_estimate']:.2f}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                if include:
                    meal_components = list(selections[meal_slot]["components"].values())
                    totals = totals_from_components(meal_components)
                    st.markdown(
                        f"<div class='meal-total'><b>{meal_slot} Total:</b> "
                        f"{totals['calories']:.0f} cal | {totals['protein']:.0f}g protein | "
                        f"{totals['carbs']:.0f}g carbs | {totals['fat']:.0f}g fat | ${totals['cost']:.2f}</div>",
                        unsafe_allow_html=True
                    )

        all_components = []
        for meal_data in selections.values():
            if meal_data["include"]:
                all_components.extend(list(meal_data["components"].values()))

        totals = totals_from_components(all_components)
        cost_df, grocery_actual, grocery_estimated, outside_total = cost_breakdown_from_selections(selections)

        st.subheader("Live Daily Total")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Calories", f"{totals['calories']:.0f}")
        c2.metric("Protein", f"{totals['protein']:.0f}g")
        c3.metric("Carbs", f"{totals['carbs']:.0f}g")
        c4.metric("Fat", f"{totals['fat']:.0f}g")
        c5.metric("Est. Meal Cost", f"${totals['cost']:.2f}")

        st.subheader("Today's Food Cost")
        c1, c2, c3 = st.columns(3)
        c1.metric("Actual Groceries Used", f"${grocery_actual:.2f}")
        c2.metric("Estimated Groceries Used", f"${grocery_estimated:.2f}")
        c3.metric("Outside Meals", f"${outside_total:.2f}")

        total_food_cost = grocery_actual + grocery_estimated + outside_total
        st.markdown(
            f"<div class='cost-box'><b>Total Food Cost Today:</b> ${total_food_cost:.2f}<br>"
            f"<small>Actual grocery prices are used after Shopping Mode is saved. Otherwise, Food_Coach_Input estimates are used.</small></div>",
            unsafe_allow_html=True
        )

        st.subheader("Cost Breakdown")
        st.dataframe(cost_df, use_container_width=True, hide_index=True)

        deduct = st.checkbox("Deduct used grocery inventory when saving", value=True)

        if st.button("💾 Save Included Meals + Update Inventory", use_container_width=True):
            included_count = sum(1 for meal_data in selections.values() if meal_data["include"])
            if included_count == 0:
                st.warning("Pick at least one meal before saving. Check the meal boxes you ate today.")
            else:
                ok, msg = save_day(selected_date, selections, deduct=deduct)
                if ok:
                    st.success("Good job eating today! Very proud of you! 🐻🍯")
                else:
                    st.warning(msg)



def category_section_label(category):
    c = str(category).strip().lower()
    if c == "monthly":
        return "📦 Monthly"
    if c == "weekly":
        return "🛒 Weekly"
    return "✨ As Needed"

def normalized_category(category):
    c = str(category).strip().lower()
    if c == "monthly":
        return "Monthly"
    if c == "weekly":
        return "Weekly"
    return "As Needed"

def render_shopping_card(row, key_prefix):
    """
    Renders one mobile-friendly shopping card.
    Returns a dict row for saving if selected.
    """
    item = str(row.get("Item", "")).strip()
    category = str(row.get("Category", "")).strip()
    suggested_buy = str(row.get("Suggested Buy", item)).strip()
    where = str(row.get("Where to Buy", "")).strip()
    unit = str(row.get("Unit", "")).strip()
    storage = str(row.get("Storage", "")).strip()
    low_stock_at = float(pd.to_numeric(row.get("Low Stock At", 0), errors="coerce") or 0)
    suggested_qty = float(pd.to_numeric(row.get("Suggested Qty", 0), errors="coerce") or 0)
    default_price = float(pd.to_numeric(row.get("Default Price", 0), errors="coerce") or 0)
    default_unit_price = round(default_price / suggested_qty, 2) if suggested_qty > 0 else default_price

    safe_key = "".join(ch if ch.isalnum() else "_" for ch in f"{key_prefix}_{item}_{category}")

    st.markdown(
        f"""
        <div class="shopping-card">
            <div class="shopping-title">{item}</div>
            <div class="shopping-meta">
                <b>Suggested Buy:</b> {suggested_buy}<br>
                <b>Where:</b> {where}<br>
                <b>Suggested Qty:</b> {suggested_qty:g} {unit}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([0.8, 1, 1])
    with c1:
        buy = st.checkbox("Buy", value=False, key=f"{safe_key}_buy")
    with c2:
        qty = st.number_input("Qty", min_value=0.0, value=float(suggested_qty), step=1.0, key=f"{safe_key}_qty")
    with c3:
        unit_price = st.number_input("Price", min_value=0.0, value=float(default_unit_price), step=0.25, key=f"{safe_key}_price", format="%.2f")

    total = round(float(qty) * float(unit_price), 2)
    st.caption(f"Line total: ${total:.2f}")

    if buy and qty > 0:
        return {
            "item": item,
            "category": category,
            "qty_bought": qty,
            "unit": unit,
            "unit_price": unit_price,
            "total_cost": total,
            "storage": storage,
            "low_stock_at": low_stock_at,
            "suggested_buy": suggested_buy,
            "where_to_buy": where,
        }
    return None


# =========================================================
# GROCERY + SHOPPING PAGE
# =========================================================
if page == "🛒 Grocery + Shopping":
    st.subheader("Grocery + Shopping")

    weekly_budget = st.number_input("Weekly budget", min_value=50, max_value=500, value=CLIENT["weekly_budget"], step=5, key="grocery_budget")
    st.metric("Daily Budget Target", f"${weekly_budget / 7:.2f}")

    grocery_df = read_grocery_input()

    if grocery_df.empty:
        st.warning("No Food_Coach_Input found. Upload the Excel tab into Google Sheets.")
    else:
        st.markdown("### Food Coach Recommended Grocery Plan")
        st.caption("Edit this in the Google Sheet tab named Food_Coach_Input. The app reads it dynamically.")
        st.dataframe(grocery_df, use_container_width=True, hide_index=True)

        st.markdown("### Monthly Buy")
        monthly_df = grocery_df[grocery_df["category"].astype(str).str.lower() == "monthly"]
        st.dataframe(monthly_df, use_container_width=True, hide_index=True)

        st.markdown("### Weekly Refill")
        weekly_df = grocery_df[grocery_df["category"].astype(str).str.lower() == "weekly"]
        st.dataframe(weekly_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        shopping_mode = st.toggle("🛒 Turn On Shopping Mode", value=False)

        if shopping_mode:
            base = grocery_df.copy()
            base = base.rename(columns={
                "item": "Item",
                "category": "Category",
                "suggested_qty": "Suggested Qty",
                "unit": "Unit",
                "default_price": "Default Price",
                "storage": "Storage",
                "low_stock_at": "Low Stock At",
                "suggested_buy": "suggested_buy",
                "where_to_buy": "where_to_buy",
                "notes": "notes",
            })

            base = enrich_grocery_for_shopping(base)
            base["Category_Normalized"] = base["Category"].apply(normalized_category)

            selected_rows = []

            st.markdown("### Filter Shopping List")

            if "shopping_store_filter_buttons" not in st.session_state:
                st.session_state.shopping_store_filter_buttons = []
            if "shopping_category_filter_buttons" not in st.session_state:
                st.session_state.shopping_category_filter_buttons = []

            st.caption("Stores")
            detected_stores = []
            if "Where to Buy" in base.columns:
                for store_text in base["Where to Buy"].dropna().astype(str).tolist():
                    for piece in store_text.replace("/", ",").replace(" or ", ",").split(","):
                        piece = piece.strip()
                        if piece and piece.lower() not in ["user choice", "nan", "none"]:
                            detected_stores.append(piece)

            preferred_stores = ["Costco", "Sprouts", "Starbucks", "Restaurant"]
            store_buttons = []
            for s in preferred_stores + sorted(set(detected_stores)):
                if s not in store_buttons:
                    store_buttons.append(s)

            store_cols = st.columns(min(4, max(1, len(store_buttons) + 1)))
            for i, store_name in enumerate(store_buttons):
                with store_cols[i % len(store_cols)]:
                    label = f"✅ {store_name}" if store_name in st.session_state.shopping_store_filter_buttons else store_name
                    if st.button(label, key=f"filter_store_{store_name}", use_container_width=True):
                        stores = st.session_state.shopping_store_filter_buttons
                        st.session_state.shopping_store_filter_buttons = [s for s in stores if s != store_name] if store_name in stores else stores + [store_name]

            clear_cols = st.columns([1, 3])
            with clear_cols[0]:
                if st.button("🧹 Clear Stores", key="clear_store_filters", use_container_width=True):
                    st.session_state.shopping_store_filter_buttons = []

            st.caption("Categories")
            cat_cols = st.columns(4)
            with cat_cols[0]:
                if st.button("📦 Monthly", key="filter_monthly", use_container_width=True):
                    cats = st.session_state.shopping_category_filter_buttons
                    st.session_state.shopping_category_filter_buttons = [c for c in cats if c != "Monthly"] if "Monthly" in cats else cats + ["Monthly"]
            with cat_cols[1]:
                if st.button("🛒 Weekly", key="filter_weekly", use_container_width=True):
                    cats = st.session_state.shopping_category_filter_buttons
                    st.session_state.shopping_category_filter_buttons = [c for c in cats if c != "Weekly"] if "Weekly" in cats else cats + ["Weekly"]
            with cat_cols[2]:
                if st.button("✨ As Needed", key="filter_as_needed", use_container_width=True):
                    cats = st.session_state.shopping_category_filter_buttons
                    st.session_state.shopping_category_filter_buttons = [c for c in cats if c != "As Needed"] if "As Needed" in cats else cats + ["As Needed"]
            with cat_cols[3]:
                if st.button("🧹 Clear Cats", key="clear_category_filters", use_container_width=True):
                    st.session_state.shopping_category_filter_buttons = []

            search_text = st.text_input("Search items", placeholder="Search whey, yogurt, banana, Costco...", key="shopping_search_text")

            selected_stores = st.session_state.shopping_store_filter_buttons
            selected_categories = st.session_state.shopping_category_filter_buttons

            filtered_base = base.copy()

            # Store filters stack together using OR within stores.
            # Costco button also matches 'Costco or Sprouts'.
            if selected_stores:
                store_mask = False
                for store in selected_stores:
                    store_mask = store_mask | filtered_base["Where to Buy"].astype(str).str.contains(store, case=False, na=False)
                filtered_base = filtered_base[store_mask]

            # Category filters stack together using OR within categories.
            if selected_categories:
                filtered_base = filtered_base[filtered_base["Category_Normalized"].isin(selected_categories)]

            if search_text.strip():
                q = search_text.strip()
                search_mask = (
                    filtered_base["Item"].astype(str).str.contains(q, case=False, na=False)
                    | filtered_base["Suggested Buy"].astype(str).str.contains(q, case=False, na=False)
                    | filtered_base["Where to Buy"].astype(str).str.contains(q, case=False, na=False)
                    | filtered_base["Category"].astype(str).str.contains(q, case=False, na=False)
                )
                filtered_base = filtered_base[search_mask]

            active_store_text = ", ".join(selected_stores) if selected_stores else "All Stores"
            active_cat_text = ", ".join(selected_categories) if selected_categories else "All Categories"
            active_search_text = search_text.strip() if search_text.strip() else "None"

            st.markdown(
                f"""
                <div class="filter-status">
                    <b>Active Filters</b><br>
                    Store: {active_store_text}<br>
                    Category: {active_cat_text}<br>
                    Search: {active_search_text}<br>
                    Showing: {len(filtered_base)} item(s)
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### Shopping List")
            if filtered_base.empty:
                st.info("No items match the current filters.")
            else:
                for idx, row in filtered_base.iterrows():
                    result = render_shopping_card(
                        row,
                        f"filtered_{idx}_{'_'.join(selected_stores) or 'allstores'}_{'_'.join(selected_categories) or 'allcats'}_{search_text}"
                    )
                    if result:
                        selected_rows.append(result)

            st.markdown("### Add One-Off Shopping Item")
            with st.expander("➕ Add to this shopping trip only", expanded=False):
                custom_item = st.text_input("Item")
                custom_suggested = st.text_input("Suggested Buy / Product Name")
                custom_where = st.text_input("Where to Buy", value="Costco or Sprouts")
                custom_qty = st.number_input("Qty", min_value=0.0, value=0.0, step=1.0, key="custom_qty_card")
                custom_unit = st.text_input("Backend Unit", value="serving")
                custom_unit_price = st.number_input("Price", min_value=0.0, value=0.0, step=0.25, key="custom_price_card")

            if custom_item and custom_qty > 0:
                selected_rows.append({
                    "item": custom_item,
                    "category": "As Needed",
                    "qty_bought": custom_qty,
                    "unit": custom_unit,
                    "unit_price": custom_unit_price,
                    "total_cost": round(custom_qty * custom_unit_price, 2),
                    "storage": "",
                    "low_stock_at": 1,
                    "suggested_buy": custom_suggested or custom_item,
                    "where_to_buy": custom_where,
                })

            selected_df = pd.DataFrame(selected_rows)
            monthly_total = float(selected_df[selected_df["category"].astype(str).str.lower() == "monthly"]["total_cost"].sum()) if not selected_df.empty else 0
            weekly_total = float(selected_df[selected_df["category"].astype(str).str.lower() == "weekly"]["total_cost"].sum()) if not selected_df.empty else 0
            as_needed_total = float(selected_df[~selected_df["category"].astype(str).str.lower().isin(["monthly", "weekly"])]["total_cost"].sum()) if not selected_df.empty else 0
            total = monthly_total + weekly_total + as_needed_total

            st.markdown(
                f"""
                <div class="cart-card">
                    🧾 Shopping Cart<br><br>
                    Monthly: ${monthly_total:.2f}<br>
                    Weekly: ${weekly_total:.2f}<br>
                    As Needed: ${as_needed_total:.2f}<br>
                    <hr>
                    Total: ${total:.2f}
                </div>
                """,
                unsafe_allow_html=True
            )

            if not selected_df.empty:
                st.caption("Selected items:")
                st.dataframe(
                    selected_df[["item", "suggested_buy", "where_to_buy", "qty_bought", "unit_price", "total_cost"]],
                    use_container_width=True,
                    hide_index=True
                )

            if st.button("✅ End Shopping Mode + Save Purchases", use_container_width=True):
                if selected_df.empty:
                    st.warning("No purchased items selected.")
                else:
                    shopping_id = datetime.now().strftime("%Y%m%d%H%M%S")
                    saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    save_rows = []
                    for _, r in selected_df.iterrows():
                        save_rows.append({
                            "shopping_id": shopping_id,
                            "saved_at": saved_at,
                            "item": r["item"],
                            "category": r["category"],
                            "qty_bought": r["qty_bought"],
                            "unit": r["unit"],
                            "unit_price": r["unit_price"],
                            "total_cost": r["total_cost"],
                            "storage": r["storage"],
                        })

                    trip_df = pd.DataFrame(save_rows)
                    append_df = trip_df[shopping_headers()]
                    ok, msg = append_sheet("Shopping_Trips", shopping_headers(), append_df)

                    if ok:
                        update_inventory_with_purchase(pd.DataFrame([
                            {
                                "item": r["item"],
                                "category": r["category"],
                                "qty_bought": r["qty_bought"],
                                "unit": r["unit"],
                                "unit_price": r["unit_price"],
                                "storage": r["storage"],
                                "low_stock_at": r["low_stock_at"],
                            }
                            for _, r in selected_df.iterrows()
                        ]))
                        save_budget_entry(date.today(), "Shopping Trip", "Shopping mode purchase", float(total))
                        st.success("Shopping trip saved and inventory updated.")
                    else:
                        st.warning(msg)

    st.subheader("Current Inventory")
    inv = read_inventory()
    if inv.empty:
        st.info("No inventory yet. Use Shopping Mode first.")
    else:
        st.dataframe(inv, use_container_width=True, hide_index=True)


# =========================================================
# HISTORY + BUDGET PAGE
# =========================================================
if page == "📊 History + Budget":
    st.subheader("Previous Days + Budget Tracking")

    if google_sheets_is_configured():
        with st.expander("Google Sheets Setup / Repair", expanded=False):
            st.caption("Use this only if Google Sheets tabs are missing or broken.")
            if st.button("Show Connected Google Sheet Info"):
                ss = get_spreadsheet()
                if ss is None:
                    st.error("Could not connect to a spreadsheet. Check spreadsheet_id/spreadsheet_name and service account sharing.")
                else:
                    st.success(f"Connected to: {ss.title}")
                    st.code(f"Spreadsheet ID: {ss.id}")
                    st.write("Tabs visible to the app:")
                    st.write(visible_worksheet_titles(ss))

            if st.button("Create / Repair Required Google Sheet Tabs"):
                ok, msg = setup_required_tabs()
                if ok:
                    st.success(msg)
                else:
                    ss = get_spreadsheet()
                    st.error(str(msg))
                    if ss is not None:
                        st.caption(f"Connected spreadsheet: {ss.title} | ID: {ss.id}")
                        st.caption("Tabs visible to the app: " + ", ".join(visible_worksheet_titles(ss)))

            st.markdown("#### Manual setup headers")
            st.caption("If repair fails, manually create these tabs in Google Sheets and paste the matching header into row 1.")

            st.write("Food_Options")
            st.code("\\t".join(food_options_headers()))

            st.write("Food_Coach_Input")
            st.code("\\t".join(grocery_headers()))

            st.write("Daily_Logs")
            st.code("\\t".join(daily_headers()))

            st.write("Shopping_Trips")
            st.code("\\t".join(shopping_headers()))

            st.write("Inventory")
            st.code("\\t".join(inventory_headers()))

            st.write("Budget_Log")
            st.code("\\t".join(budget_headers()))

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
            day_df[[
                "meal_slot", "component_slot", "component_name",
                "calories", "protein", "carbs", "fat", "cost", "cost_type"
            ]],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.subheader("Spending Tracking Graph")

    weekly_budget = st.number_input("Weekly budget for graph", min_value=50, max_value=500, value=CLIENT["weekly_budget"], step=5)
    daily_budget = weekly_budget / 7

    spend_df = spending_summary()
    if spend_df.empty:
        st.info("No spending data yet.")
    else:
        daily = spend_df.groupby("date", as_index=False)["amount"].sum()
        daily["daily_budget"] = daily_budget
        daily["above_below_budget"] = daily["daily_budget"] - daily["amount"]

        st.dataframe(daily, use_container_width=True, hide_index=True)
        st.line_chart(daily.set_index("date")[["amount", "daily_budget"]])
        st.bar_chart(daily.set_index("date")[["above_below_budget"]])

    st.subheader("Shopping History")
    trips = read_shopping_trips()
    if trips.empty:
        st.info("No shopping trips saved yet.")
    else:
        st.dataframe(trips, use_container_width=True, hide_index=True)


st.markdown("<div class='footer-honey'>🍯 Made by Honey</div>", unsafe_allow_html=True)
