import gspread
import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

@st.cache_data(ttl=43200)
def read_from_gsheets(sheet_name):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_dict = st.secrets["gcp_service_account"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

    gc = gspread.authorize(credentials)
    sheet = gc.open_by_url(st.secrets["private_gsheets_url"])

    worksheet = sheet.worksheet(sheet_name)

    data = worksheet.get_all_values()

    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)
    return df
