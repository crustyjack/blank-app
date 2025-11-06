import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.title("🎈 My Streamlit App with Feedback")

# --- Google Sheets setup ---
SERVICE_ACCOUNT_FILE = "hybrid-sentry-477409-a3-969ace30f310.json"  # Path to your JSON
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load service account info securely from Streamlit secrets
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=SCOPES)
gc = gspread.authorize(creds)

# Replace with your Google Sheet ID
SPREADSHEET_ID = "1R9dchyFwr_PplMguXJbInBtQaQ8zUAMNION3eb__QqQ"
spreadsheet = gc.open_by_key(SPREADSHEET_ID)

# --- Helper Functions ---
def get_sheet_dataframe(sheet_name):
    """Read a worksheet into a DataFrame."""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.WorksheetNotFound:
        st.warning(f"Worksheet '{sheet_name}' not found.")
        return pd.DataFrame()

def append_feedback(sheet_name, timestamp, name, feedback, email=None):
    """
    Append a row to a Google Sheet feedback tab.
    If email is provided, include it in the row.
    """
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        # Determine columns based on whether email is used
        headers = ["timestamp", "name"]
        if email is not None:
            headers.append("email")
        headers.append("feedback")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols=str(len(headers)))
        worksheet.append_row(headers)

    # Prepare row to append
    row = [timestamp, name]
    if email is not None:
        row.append(email)
    row.append(feedback)

    worksheet.append_row(row)

def feedback_form(sheet_name: str, table_name: str, add_email: bool = False):
    """
    Display a feedback form for a given table and append feedback to the Google Sheet.
    
    Args:
        sheet_name (str): Name of the Google Sheet tab where feedback will be saved.
        table_name (str): Display name of the table on the Streamlit page.
        add_email (bool): Whether to include an email field in the form.
    """
    #st.subheader(table_name)
    
    # Display the feedback form
    with st.form(f"feedback_form_{sheet_name}"):
        st.write(f"💬 Feedback on {table_name}")
        name = st.text_input("Your name (optional):", key=f"name_{sheet_name}")
        if add_email:
            email = st.text_input("Your email address (optional):", key=f"email_{sheet_name}")
        feedback = st.text_area("Your feedback:", key=f"feedback_{sheet_name}")
        submitted = st.form_submit_button("Submit feedback")

        if submitted and feedback.strip() != "":
            # Prepare the row data
            row_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name]
            if add_email:
                row_data.append(email)
            row_data.append(feedback)

            # Append feedback using your append_feedback function
            append_feedback(sheet_name, *row_data)
            
            st.success(f"✅ Feedback submitted for {table_name}!")


# --- Read main tables ---
df_gebouw = get_sheet_dataframe("Gebouwdeomgeving")
df_gebouw["URL:"] = df_gebouw["URL:"].apply(lambda x: f"[{x}]({x})")

df_mobiliteit = get_sheet_dataframe("Mobiliteit")
df_mobiliteit["URL:"] = df_mobiliteit["URL:"].apply(lambda x: f"[{x}]({x})")

df_bedrijven = get_sheet_dataframe("Bedrijventerrein")
df_bedrijven["URL:"] = df_bedrijven["URL:"].apply(lambda x: f"[{x}]({x})")

df_cluster6 = get_sheet_dataframe("Cluster 6")
df_cluster6["URL:"] = df_cluster6["URL:"].apply(lambda x: f"[{x}]({x})")

df_andere = get_sheet_dataframe("Andere")
df_andere["URL:"] = df_andere["URL:"].apply(lambda x: f"[{x}]({x})")

# --- Display tables ---
st.set_page_config(layout="wide")   # allow app to use full browser width

st.subheader("🏠 Gebouwde omgeving")
st.dataframe(df_gebouw, use_container_width=True, column_config={
    "URL:": st.column_config.LinkColumn("URL:")
})
feedback_form("Feedback_Gebouwdeomgeving", "Gebouwdeomgeving", add_email=True)

st.subheader("🚗 Mobiliteit")
st.dataframe(df_mobiliteit, use_container_width=True, column_config={
    "URL:": st.column_config.LinkColumn("URL:")
})
feedback_form("Feedback_Mobiliteit", "Mobiliteit", add_email=True)

st.subheader("🚗 Bedrijventerrein")
st.dataframe(df_bedrijven, use_container_width=True, column_config={
    "URL:": st.column_config.LinkColumn("URL:")
})
feedback_form("Feedback_Bedrijventerrein", "Bedrijventerrein", add_email=True)

st.subheader("🚗 Cluster 6")
st.dataframe(df_cluster6, use_container_width=True, column_config={
    "URL:": st.column_config.LinkColumn("URL:")
})
feedback_form("Feedback_Cluster6", "Cluster 6", add_email=True)

st.subheader("🚗 Andere")
st.dataframe(df_andere, use_container_width=True, column_config={
    "URL:": st.column_config.LinkColumn("URL:")
})
feedback_form("Feedback_Andere", "Andere", add_email=True)
