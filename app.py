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
    .section-card h3 { color: var(--bear); margin-top: 0; margin-bottom: 8px; }
    div[data-testid="stMetric"] {
        background: var(--kpi-bg);
        color: var(--kpi-text);
        border: 1px solid var(--kpi-border);
        padding: 14px;
        border-radius: 14px;
        box-shadow: 0 2px 8px var(--shadow);
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div { color: var(--kpi-text) !important; }
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
    .meal-total, .cost-box {
        background: var(--success-bg);
        color: var(--success-text);
        border: 1px solid var(--success-border);
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
        div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
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
    try:
        ws = spreadsheet.worksheet(title)
    except Exception:
        try:
            ws = spreadsheet.add_worksheet(title=title, rows=100, cols=max(12, len(headers)))
            ws.update("A1", [headers])
            return ws
        except Exception as e:
            # Return None and let the caller show clean setup instructions.
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

def read_sheet(title, headers):
    ss = get_spreadsheet()
    if ss is None:
        return pd.DataFrame(columns=headers)
    ws = get_or_create_worksheet(ss, title, headers)
    if ws is None:
        st.info(f"Google Sheet tab '{title}' is not ready yet.")
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
# DEFAULT SEED DATA
# =========================================================
DEFAULT_FOOD_OPTIONS = [
    # Breakfast
    ["Breakfast","Drink","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Breakfast","Drink","Protein iced coffee",380,54,24,10,2.00,False,"Whey protein",2,"scoops","TRUE","TRUE"],
    ["Breakfast","Drink","Regular cold coffee",40,1,8,1,0.50,False,"Cold coffee",1,"serving","TRUE","FALSE"],
    ["Breakfast","Drink","Whole milk",150,8,12,8,0.75,False,"Whole milk",8,"oz","TRUE","FALSE"],
    ["Breakfast","Main","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Breakfast","Main","Peanut butter bagel",470,18,58,19,1.25,False,"Bagel",1,"bagel","TRUE","TRUE"],
    ["Breakfast","Main","Greek yogurt + granola bowl",350,20,45,8,2.00,False,"Greek yogurt",1,"serving","TRUE","FALSE"],
    ["Breakfast","Side","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Breakfast","Side","Banana",120,1,31,0,0.35,False,"Banana",1,"banana","TRUE","FALSE"],
    ["Breakfast","Side","2 boiled eggs",140,12,1,10,1.10,False,"Boiled eggs",2,"eggs","TRUE","TRUE"],
    ["Breakfast","Side","Protein bar",200,20,22,6,1.25,False,"Protein bar",1,"bar","TRUE","FALSE"],
    ["Breakfast","Dessert/Treat","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Breakfast","Dessert/Treat","Banana",120,1,31,0,0.35,False,"Banana",1,"banana","TRUE","TRUE"],
    ["Breakfast","Dessert/Treat","Greek yogurt",150,18,12,3,1.25,False,"Greek yogurt",1,"serving","TRUE","FALSE"],

    # Lunch
    ["Lunch","Drink","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Lunch","Drink","Water",0,0,0,0,0,False,"",0,"","TRUE","TRUE"],
    ["Lunch","Main","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Lunch","Main","Subway Footlong Turkey",850,60,95,22,12.00,True,"Subway Footlong Turkey",1,"meal","TRUE","TRUE"],
    ["Lunch","Main","Subway Footlong Rotisserie Chicken",900,65,95,25,13.00,True,"Subway Footlong Rotisserie Chicken",1,"meal","TRUE","FALSE"],
    ["Lunch","Main","Grocery store deli sandwich",700,35,75,25,7.00,True,"Grocery store deli sandwich",1,"meal","TRUE","FALSE"],
    ["Lunch","Main","Vitality Bowl protein wrap",700,30,75,24,15.00,True,"Vitality Bowl protein wrap",1,"meal","TRUE","FALSE"],
    ["Lunch","Main","Jersey Mike's Giant Turkey Sub",1100,70,120,38,15.00,True,"Jersey Mike's Giant Turkey Sub",1,"meal","TRUE","FALSE"],
    ["Lunch","Side","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Lunch","Side","Protein bar",200,20,22,6,1.25,False,"Protein bar",1,"bar","TRUE","TRUE"],
    ["Lunch","Side","Banana",120,1,31,0,0.35,False,"Banana",1,"banana","TRUE","FALSE"],
    ["Lunch","Side","Trail mix",380,9,35,24,1.15,False,"Trail mix",1,"serving","TRUE","FALSE"],
    ["Lunch","Dessert/Treat","None",0,0,0,0,0,False,"",0,"","TRUE","TRUE"],

    # Snack
    ["Snack","Drink","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Snack","Drink","Water",0,0,0,0,0,False,"",0,"","TRUE","TRUE"],
    ["Snack","Main","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Snack","Main","Greek yogurt + granola bowl",350,20,45,8,2.00,False,"Greek yogurt",1,"serving","TRUE","TRUE"],
    ["Snack","Main","Peanut butter bagel",470,18,58,19,1.25,False,"Bagel",1,"bagel","TRUE","FALSE"],
    ["Snack","Side","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Snack","Side","Trail mix",380,9,35,24,1.15,False,"Trail mix",1,"serving","TRUE","TRUE"],
    ["Snack","Side","Banana",120,1,31,0,0.35,False,"Banana",1,"banana","TRUE","FALSE"],
    ["Snack","Side","Protein bar",200,20,22,6,1.25,False,"Protein bar",1,"bar","TRUE","FALSE"],
    ["Snack","Dessert/Treat","None",0,0,0,0,0,False,"",0,"","TRUE","TRUE"],

    # Dinner
    ["Dinner","Drink","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Dinner","Drink","Water",0,0,0,0,0,False,"",0,"","TRUE","TRUE"],
    ["Dinner","Main","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Dinner","Main","Rotisserie chicken portion",550,65,0,30,2.50,False,"Rotisserie chicken portion",1,"portion","TRUE","TRUE"],
    ["Dinner","Main","Grocery store deli sandwich",700,35,75,25,7.00,True,"Grocery store deli sandwich",1,"meal","TRUE","FALSE"],
    ["Dinner","Side","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Dinner","Side","Whole wheat bagel",250,10,48,2,0.75,False,"Whole wheat bagel",1,"bagel","TRUE","TRUE"],
    ["Dinner","Side","Rice cup",220,4,46,2,1.25,False,"Rice cup",1,"cup","TRUE","FALSE"],
    ["Dinner","Side","Whole wheat bread serving",240,8,44,4,0.75,False,"Whole wheat bread serving",1,"serving","TRUE","FALSE"],
    ["Dinner","Dessert/Treat","None",0,0,0,0,0,False,"",0,"","TRUE","FALSE"],
    ["Dinner","Dessert/Treat","Greek yogurt",150,18,12,3,1.25,False,"Greek yogurt",1,"serving","TRUE","TRUE"],
    ["Dinner","Dessert/Treat","Protein bar",200,20,22,6,1.25,False,"Protein bar",1,"bar","TRUE","FALSE"],
]

DEFAULT_GROCERY = [
    ["Whey protein","Monthly",60,"scoops",60.00,"Room temp",10,"1 large Costco tub"],
    ["Peanut butter","Monthly",64,"tbsp",10.00,"Room temp",4,"1 large jar"],
    ["Trail mix","Monthly",20,"servings",15.00,"Room temp",3,"1 large bag"],
    ["Protein bar","Monthly",12,"bars",20.00,"Room temp",3,"1 box"],
    ["Granola","Monthly",16,"servings",8.00,"Room temp",3,"1 large bag"],
    ["Whole milk","Weekly",128,"oz",8.00,"Mini fridge",32,"1 gallon"],
    ["Cold coffee","Weekly",7,"servings",5.00,"Room temp/fridge",2,"Cold brew"],
    ["Bagel","Weekly",12,"bagels",8.00,"Room temp",3,"2 packs"],
    ["Whole wheat bagel","Weekly",6,"bagels",5.00,"Room temp",2,"1 pack"],
    ["Banana","Weekly",14,"bananas",4.00,"Room temp",3,"10-14 bananas"],
    ["Greek yogurt","Weekly",8,"servings",8.00,"Mini fridge",2,"1 pack/tub"],
    ["Boiled eggs","Weekly",12,"eggs",7.00,"Mini fridge",2,"pre-boiled pack"],
    ["Rotisserie chicken portion","Weekly",6,"portions",10.00,"Mini fridge",1,"2 chickens, portioned"],
    ["Rice cup","Weekly",4,"cups",5.00,"Room temp",1,"microwave rice cups"],
    ["Whole wheat bread serving","Weekly",6,"servings",5.00,"Room temp",2,"1 loaf"],
]


# =========================================================
# READ DATA
# =========================================================
@st.cache_data(ttl=60)
def read_food_options():
    df = read_sheet("Food_Options", food_options_headers())
    if df.empty or df["option_name"].astype(str).str.strip().eq("").all():
        df = pd.DataFrame(DEFAULT_FOOD_OPTIONS, columns=food_options_headers())
    for col in ["calories", "protein", "carbs", "fat", "cost_estimate", "ingredient_qty"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["active"] = df["active"].astype(str).str.lower().isin(["true", "yes", "1", "y"])
    df["default_choice"] = df["default_choice"].astype(str).str.lower().isin(["true", "yes", "1", "y"])
    df["is_outside_meal"] = df["is_outside_meal"].astype(str).str.lower().isin(["true", "yes", "1", "y"])
    return df

def read_grocery_input():
    df = read_sheet("Food_Coach_Input", grocery_headers())
    if df.empty or df["item"].astype(str).str.strip().eq("").all():
        df = pd.DataFrame(DEFAULT_GROCERY, columns=grocery_headers())
    for col in ["suggested_qty", "default_price", "low_stock_at"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
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
# SETUP / SEED
# =========================================================
def setup_required_tabs(seed_defaults=False):
    if not google_sheets_is_configured():
        return False, "Google Sheets is not connected."

    ss = get_spreadsheet()
    if ss is None:
        return False, "Could not open the Google Sheet. Check spreadsheet_name and sharing permissions."

    required = [
        ("Food_Options", food_options_headers()),
        ("Food_Coach_Input", grocery_headers()),
        ("Daily_Logs", daily_headers()),
        ("Shopping_Trips", shopping_headers()),
        ("Inventory", inventory_headers()),
        ("Budget_Log", budget_headers()),
    ]

    failed_tabs = []

    for title, headers in required:
        ws = get_or_create_worksheet(ss, title, headers)
        if ws is None:
            failed_tabs.append(title)

    if failed_tabs:
        return False, "Could not auto-create/access: " + ", ".join(failed_tabs) + ". Manually create these tabs in Google Sheets, then paste the header rows from the setup section below."

    if seed_defaults:
        food_df = read_sheet("Food_Options", food_options_headers())
        grocery_df = read_sheet("Food_Coach_Input", grocery_headers())

        if food_df.empty or food_df["option_name"].astype(str).str.strip().eq("").all():
            ok, msg = rewrite_sheet("Food_Options", food_options_headers(), pd.DataFrame(DEFAULT_FOOD_OPTIONS, columns=food_options_headers()))
            if not ok:
                return False, "Could not seed Food_Options. Manually paste the default rows."

        if grocery_df.empty or grocery_df["item"].astype(str).str.strip().eq("").all():
            ok, msg = rewrite_sheet("Food_Coach_Input", grocery_headers(), pd.DataFrame(DEFAULT_GROCERY, columns=grocery_headers()))
            if not ok:
                return False, "Could not seed Food_Coach_Input. Manually paste the default rows."

        st.cache_data.clear()

    return True, "Required tabs are ready."


# =========================================================
# CALCULATIONS
# =========================================================
def get_options(food_df, meal_slot, component_slot):
    opts = food_df[
        (food_df["meal_slot"].astype(str) == meal_slot)
        & (food_df["component_slot"].astype(str) == component_slot)
        & (food_df["active"] == True)
    ].copy()
    if opts.empty:
        opts = pd.DataFrame([{
            "meal_slot": meal_slot, "component_slot": component_slot, "option_name": "None",
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "cost_estimate": 0,
            "is_outside_meal": False, "ingredient_name": "", "ingredient_qty": 0,
            "ingredient_unit": "", "active": True, "default_choice": True
        }])
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

def inventory_unit_prices():
    inv = read_inventory()
    lookup = {}
    if not inv.empty:
        for _, r in inv.iterrows():
            item = str(r["item"])
            price = float(r["last_unit_price"])
            if item and price > 0:
                lookup[item] = price
    return lookup

def estimated_unit_prices_from_coach():
    grocery = read_grocery_input()
    lookup = {}
    for _, r in grocery.iterrows():
        item = str(r["item"])
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
                    "Item": comp["name"],
                    "Type": "Outside Meal",
                    "Qty Used": 1,
                    "Unit Cost": comp["cost_estimate"],
                    "Cost Used": comp["cost_estimate"],
                    "Cost Source": "Outside meal price"
                })
            else:
                item = comp["ingredient_name"]
                qty = comp["ingredient_qty"]
                if not item or qty <= 0:
                    continue

                if item in actual_prices:
                    unit = actual_prices[item]
                    source = "Actual shopping price"
                    cost = unit * qty
                    grocery_actual += cost
                elif item in estimated_prices:
                    unit = estimated_prices[item]
                    source = "Estimated price"
                    cost = unit * qty
                    grocery_estimated += cost
                else:
                    unit = comp["cost_estimate"] / qty if qty > 0 else comp["cost_estimate"]
                    source = "Estimated from meal option"
                    cost = comp["cost_estimate"]
                    grocery_estimated += cost

                rows.append({
                    "Item": item,
                    "Type": "Grocery",
                    "Qty Used": qty,
                    "Unit Cost": round(unit, 2),
                    "Cost Used": round(cost, 2),
                    "Cost Source": source
                })

    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Item", "Type", "Qty Used", "Unit Cost", "Cost Used", "Cost Source"])
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
        match = inventory["item"].astype(str) == str(item)
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
                match = cost_df[(cost_df["Item"] == comp["ingredient_name"]) & (cost_df["Type"] == "Grocery")]
                cost = float(match.iloc[0]["Cost Used"]) if not match.empty else comp["cost_estimate"]
                cost_type = str(match.iloc[0]["Cost Source"]) if not match.empty else "Estimated"

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

    return True, f"Saved {len(rows)} items for {plan_date}."

def update_inventory_with_purchase(shopping_df):
    inv = read_inventory()
    if inv.empty:
        inv = pd.DataFrame(columns=inventory_headers())

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, r in shopping_df.iterrows():
        item = str(r["item"])
        qty = float(r["qty_bought"])
        unit_price = float(r["unit_price"])
        if not item or qty <= 0:
            continue

        match = inv["item"].astype(str) == item if not inv.empty else pd.Series(dtype=bool)
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
    return inv

def low_stock_alerts():
    inv = read_inventory()
    if inv.empty:
        return pd.DataFrame(columns=inventory_headers())
    return inv[(inv["low_stock_at"] > 0) & (inv["qty_on_hand"] <= inv["low_stock_at"])].copy()

def spending_summary():
    budget = read_budget_logs()
    shopping = read_shopping_trips()
    rows = []
    if not shopping.empty:
        for _, r in shopping.iterrows():
            rows.append({"date": str(r["saved_at"])[:10], "source": "Shopping", "amount": float(r["total_cost"])})
    if not budget.empty:
        for _, r in budget.iterrows():
            rows.append({"date": str(r["date"]), "source": str(r["type"]), "amount": float(r["amount"])})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["date", "source", "amount"])

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
# OVERVIEW
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
        week_spend = spend_df[(spend_df["date_dt"].dt.date >= wk) & (spend_df["date_dt"].dt.date <= wk_end)]["amount"].sum()
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
# MEAL BUILDER
# =========================================================
elif page == "🍽️ Meal Builder":
    selected_date = st.date_input("Select day/date", value=date.today(), key="meal_date")
    st.subheader(f"Meal Builder — {selected_date.strftime('%A, %b %d, %Y')}")

    food_df = read_food_options()
    saved = read_daily_logs()
    saved_defaults = {}
    if not saved.empty:
        d = saved[saved["plan_date"].astype(str) == str(selected_date)]
        for _, row in d.iterrows():
            saved_defaults[(row["meal_slot"], row["component_slot"])] = row["component_name"]

    selections = {}

    for meal_slot in ["Breakfast", "Lunch", "Snack", "Dinner"]:
        selections[meal_slot] = {"include": False, "components": {}}
        with st.expander(meal_slot, expanded=True):
            include = st.checkbox(f"Include {meal_slot}", value=False, key=f"{selected_date}_{meal_slot}_include")
            selections[meal_slot]["include"] = include

            cols = st.columns(4)
            for i, component_slot in enumerate(["Drink", "Main", "Side", "Dessert/Treat"]):
                opts = get_options(food_df, meal_slot, component_slot)
                names = opts["option_name"].astype(str).tolist()

                default_name = saved_defaults.get((meal_slot, component_slot), None)
                if default_name not in names:
                    defaults = opts[opts["default_choice"] == True]
                    default_name = str(defaults.iloc[0]["option_name"]) if not defaults.empty else names[0]
                idx = names.index(default_name) if default_name in names else 0

                with cols[i]:
                    chosen = st.selectbox(component_slot, names, index=idx, key=f"{selected_date}_{meal_slot}_{component_slot}")
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
                totals = totals_from_components(list(selections[meal_slot]["components"].values()))
                st.markdown(
                    f"<div class='meal-total'><b>{meal_slot} Total:</b> "
                    f"{totals['calories']:.0f} cal | {totals['protein']:.0f}g protein | "
                    f"{totals['carbs']:.0f}g carbs | {totals['fat']:.0f}g fat | ${totals['cost']:.2f}</div>",
                    unsafe_allow_html=True
                )
            else:
                pass

    all_components = []
    for m in selections.values():
        if m["include"]:
            all_components.extend(list(m["components"].values()))

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
        f"<small>Actual grocery prices are used after Shopping Mode is saved. Otherwise, the app uses Food_Coach_Input estimates.</small></div>",
        unsafe_allow_html=True
    )

    st.subheader("Grocery / Outside Meal Cost Breakdown")
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
# GROCERY + SHOPPING
# =========================================================
elif page == "🛒 Grocery + Shopping":
    st.subheader("Grocery + Shopping")

    weekly_budget = st.number_input("Weekly budget", min_value=50, max_value=500, value=CLIENT["weekly_budget"], step=5, key="grocery_budget")
    st.metric("Daily Budget Target", f"${weekly_budget / 7:.2f}")

    grocery_df = read_grocery_input()
    st.markdown("### Food Coach Recommended Grocery Plan")
    st.caption("Edit this in the Google Sheet tab named Food_Coach_Input. The app reads it dynamically.")
    st.dataframe(grocery_df, use_container_width=True, hide_index=True)

    st.markdown("### Monthly Buy")
    st.dataframe(grocery_df[grocery_df["category"].astype(str).str.lower() == "monthly"], use_container_width=True, hide_index=True)

    st.markdown("### Weekly Refill")
    st.dataframe(grocery_df[grocery_df["category"].astype(str).str.lower() == "weekly"], use_container_width=True, hide_index=True)

    st.markdown("---")
    shopping_mode = st.toggle("🛒 Turn On Shopping Mode", value=False)

    if shopping_mode:
        base = grocery_df.copy()
        base = base.rename(columns={
            "item": "Item", "category": "Category", "suggested_qty": "Suggested Qty",
            "unit": "Unit", "default_price": "Default Price", "storage": "Storage", "low_stock_at": "Low Stock At"
        })
        base["Buy"] = True
        base["Qty Bought"] = base["Suggested Qty"]
        base["Unit Price"] = base.apply(lambda r: round(float(r["Default Price"]) / float(r["Suggested Qty"]), 2) if float(r["Suggested Qty"]) > 0 else 0, axis=1)
        base["Total Cost"] = base["Qty Bought"] * base["Unit Price"]
        view = base[["Buy", "Item", "Category", "Suggested Qty", "Qty Bought", "Unit", "Unit Price", "Total Cost", "Storage", "Low Stock At"]]

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
                        "item": "item", "category": "category", "qty_bought": "qty_bought",
                        "unit": "unit", "unit_price": "unit_price", "storage": "storage", "low_stock_at": "low_stock_at"
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
# HISTORY + BUDGET
# =========================================================
elif page == "📊 History + Budget":
    st.subheader("Previous Days + Budget Tracking")

    if google_sheets_is_configured():
        with st.expander("Google Sheets Setup / Repair", expanded=False):
            st.caption("Use this only if Google Sheets tabs are missing or broken.")
            if st.button("Create / Repair Required Google Sheet Tabs"):
                ok, msg = setup_required_tabs(seed_defaults=False)
                if ok:
                    st.success(msg)
                else:
                    st.error(str(msg))

            if st.button("Seed Default Food_Options + Food_Coach_Input"):
                ok, msg = setup_required_tabs(seed_defaults=True)
                if ok:
                    st.success("Default editable sheet data seeded. Refresh the app.")
                else:
                    st.error(str(msg))

            st.markdown("#### Manual setup headers")
            st.caption("If the buttons fail, manually create these tabs in your Google Sheet and paste the matching header into row 1.")

            st.write("Food_Options")
            st.code("\t".join(food_options_headers()))

            st.write("Food_Coach_Input")
            st.code("\t".join(grocery_headers()))

            st.write("Daily_Logs")
            st.code("\t".join(daily_headers()))

            st.write("Shopping_Trips")
            st.code("\t".join(shopping_headers()))

            st.write("Inventory")
            st.code("\t".join(inventory_headers()))

            st.write("Budget_Log")
            st.code("\t".join(budget_headers()))

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
        st.dataframe(day_df[["meal_slot", "component_slot", "component_name", "calories", "protein", "carbs", "fat", "cost", "cost_type"]], use_container_width=True, hide_index=True)

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
