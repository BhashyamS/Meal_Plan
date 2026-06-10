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

def read_sheet(title, headers):
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
        records = ws.get_all_records()
    except Exception:
        return pd.DataFrame(columns=headers)

    if not records:
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(records)
    for col in headers:
        if col not in df.columns:
            df[col] = ""

    return df[headers]

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
    return ["item", "category", "suggested_qty", "unit", "default_price", "storage", "low_stock_at", "notes"]

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
        st.warning("No Food_Options found. Upload the Excel tabs into Google Sheets or seed/create the Food_Options tab in History + Budget.")
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
            components = get_components_for_meal(food_df, meal_slot)
            if not components:
                continue

            selections[meal_slot] = {"include": False, "components": {}}

            with st.expander(meal_slot, expanded=True):
                include = st.checkbox(f"Include {meal_slot}", value=False, key=f"{selected_date}_{meal_slot}_include")
                selections[meal_slot]["include"] = include

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
                                # If no default is set, prefer None.
                                none_rows = opts[opts["option_name"].astype(str).str.lower() == "none"]
                                default_name = str(none_rows.iloc[0]["option_name"]) if not none_rows.empty else names[0]

                        default_index = names.index(default_name) if default_name in names else 0

                        with cols[i]:
                            chosen = st.selectbox(
                                display_component_name(component_slot),
                                names,
                                index=default_index,
                                key=f"{selected_date}_{meal_slot}_{component_slot}"
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


# =========================================================
# GROCERY + SHOPPING PAGE
# =========================================================
elif page == "🛒 Grocery + Shopping":
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
            })

            base["Buy"] = True
            base["Suggested Qty"] = pd.to_numeric(base["Suggested Qty"], errors="coerce").fillna(0)
            base["Default Price"] = pd.to_numeric(base["Default Price"], errors="coerce").fillna(0)
            base["Qty Bought"] = base["Suggested Qty"]
            base["Unit Price"] = base.apply(
                lambda r: round(float(r["Default Price"]) / float(r["Suggested Qty"]), 2) if float(r["Suggested Qty"]) > 0 else 0,
                axis=1
            )
            base["Total Cost"] = base["Qty Bought"] * base["Unit Price"]

            view = base[[
                "Buy", "Item", "Category", "Suggested Qty", "Qty Bought",
                "Unit", "Unit Price", "Total Cost", "Storage", "Low Stock At"
            ]]

            edited = st.data_editor(
                view,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "Buy": st.column_config.CheckboxColumn("Buy"),
                    "Qty Bought": st.column_config.NumberColumn("Qty Bought", min_value=0.0, step=1.0),
                    "Unit Price": st.column_config.NumberColumn("Unit Price", min_value=0.0, step=0.25, format="$%.2f"),
                    "Total Cost": st.column_config.NumberColumn("Total Cost", min_value=0.0, step=0.25, format="$%.2f"),
                },
            )

            edited["Qty Bought"] = pd.to_numeric(edited["Qty Bought"], errors="coerce").fillna(0)
            edited["Unit Price"] = pd.to_numeric(edited["Unit Price"], errors="coerce").fillna(0)
            edited["Total Cost"] = (edited["Qty Bought"] * edited["Unit Price"]).round(2)

            selected = edited[(edited["Buy"] == True) & (edited["Qty Bought"] > 0)].copy()
            total = float(selected["Total Cost"].sum()) if not selected.empty else 0
            st.metric("Shopping Total", f"${total:.2f}")

            st.markdown("### Add One-Off Shopping Item")
            with st.expander("➕ Add to this shopping trip only", expanded=False):
                custom_item = st.text_input("Item")
                custom_qty = st.number_input("Qty", min_value=0.0, value=0.0, step=1.0)
                custom_unit = st.text_input("Unit", value="serving")
                custom_unit_price = st.number_input("Unit Price", min_value=0.0, value=0.0, step=0.25)

            if st.button("✅ End Shopping Mode + Save Purchases", use_container_width=True):
                rows = []
                shopping_id = datetime.now().strftime("%Y%m%d%H%M%S")
                saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for _, r in selected.iterrows():
                    rows.append({
                        "shopping_id": shopping_id,
                        "saved_at": saved_at,
                        "item": r["Item"],
                        "category": r["Category"],
                        "qty_bought": r["Qty Bought"],
                        "unit": r["Unit"],
                        "unit_price": r["Unit Price"],
                        "total_cost": r["Total Cost"],
                        "storage": r["Storage"],
                        "low_stock_at": r["Low Stock At"],
                    })

                if custom_item and custom_qty > 0:
                    rows.append({
                        "shopping_id": shopping_id,
                        "saved_at": saved_at,
                        "item": custom_item,
                        "category": "Custom",
                        "qty_bought": custom_qty,
                        "unit": custom_unit,
                        "unit_price": custom_unit_price,
                        "total_cost": custom_qty * custom_unit_price,
                        "storage": "",
                        "low_stock_at": 1,
                    })

                if not rows:
                    st.warning("No purchased items selected.")
                else:
                    trip_df = pd.DataFrame(rows)
                    append_df = trip_df[shopping_headers()]
                    ok, msg = append_sheet("Shopping_Trips", shopping_headers(), append_df)

                    if ok:
                        update_inventory_with_purchase(trip_df.rename(columns={
                            "item": "item",
                            "category": "category",
                            "qty_bought": "qty_bought",
                            "unit": "unit",
                            "unit_price": "unit_price",
                            "storage": "storage",
                            "low_stock_at": "low_stock_at",
                        }))
                        save_budget_entry(date.today(), "Shopping Trip", "Shopping mode purchase", float(trip_df["total_cost"].sum()))
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
elif page == "📊 History + Budget":
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
