import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from st_aggrid import AgGrid, GridOptionsBuilder

# -------------------------------
# PAGE SETUP
# -------------------------------
st.set_page_config(page_title="⚡ Energiehub database ⚡", layout="wide")
st.title("⚡ Energiehub database ⚡")
st.subheader("Contact: Michael Jenks | m.j.f.jenks@hva.nl")
st.subheader("Hogeschool van Amsterdam")

# -------------------------------
# GOOGLE SHEETS SETUP
# -------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=SCOPES)
gc = gspread.authorize(creds)

SPREADSHEET_ID = "1R9dchyFwr_PplMguXJbInBtQaQ8zUAMNION3eb__QqQ"
spreadsheet = gc.open_by_key(SPREADSHEET_ID)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def get_sheet_dataframe(sheet_name):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.WorksheetNotFound:
        st.warning(f"Worksheet '{sheet_name}' not found.")
        return pd.DataFrame()

def append_feedback(sheet_name, timestamp, name, feedback, email=None):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        headers = ["timestamp", "name"]
        if email is not None:
            headers.append("email")
        headers.append("feedback")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols=str(len(headers)))
        worksheet.append_row(headers)

    row = [timestamp, name]
    if email is not None:
        row.append(email)
    row.append(feedback)
    worksheet.append_row(row)

def feedback_form(sheet_name: str, table_name: str, add_email: bool = False):
    with st.form(f"feedback_form_{sheet_name}"):
        st.write(f"💬 Feedback voor {table_name}")
        name = st.text_input("Uw naam (optioneel):", key=f"name_{sheet_name}")
        email = st.text_input("Uw e-mailadres (optioneel):", key=f"email_{sheet_name}") if add_email else None
        feedback = st.text_area("Uw feedback:", key=f"feedback_{sheet_name}")
        submitted = st.form_submit_button("Feedback indienen")

        if submitted and feedback.strip():
            append_feedback(
                sheet_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name,
                feedback,
                email,
            )
            st.success(f"✅ Feedback ingediend voor {table_name}!")

# -------------------------------
# LOAD DATA
# -------------------------------
df_gebouw     = get_sheet_dataframe("Gebouwdeomgeving")
df_mobiliteit  = get_sheet_dataframe("Mobiliteit")
df_bedrijven   = get_sheet_dataframe("Bedrijventerrein")
df_cluster6    = get_sheet_dataframe("Cluster 6")
df_andere      = get_sheet_dataframe("Andere")

tables = {
    "🏠 Gebouwde omgeving": df_gebouw,
    "🚗 Mobiliteit": df_mobiliteit,
    "🏭🏢 Bedrijventerrein": df_bedrijven,
    "🏭 Cluster 6": df_cluster6,
    "⍰ Andere": df_andere,
}

# -------------------------------
# GLOBAL SEARCH INPUT
# -------------------------------
st.markdown("---")
global_search = st.text_input("🔍 Zoekterm (filtert alle tabellen)", placeholder="Typ om te zoeken...")

# -------------------------------
# HELPER: RENDER AGGRID TABLE
# -------------------------------
def render_aggrid(df, search_text, key):
    if df.empty:
        st.info("Geen gegevens beschikbaar.")
        return

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=True,
        searchable=True,
        wrapText=True,
        autoHeight=True,
    )
    gb.configure_grid_options(domLayout="autoHeight", quickFilter=True)
    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        quickFilterText=search_text,
        theme="alpine",  # "balham", "material" also nice
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        key=key,
    )

# -------------------------------
# DISPLAY ALL TABLES + FEEDBACK FORMS
# -------------------------------
for name, df in tables.items():
    st.subheader(name)
    render_aggrid(df, global_search, key=name)
    feedback_form(f"Feedback_{name.replace(' ', '').replace('🏠','').replace('🚗','').replace('🏭🏢','').replace('🏭','').replace('⍰','')}", name, add_email=True)
    st.divider()

