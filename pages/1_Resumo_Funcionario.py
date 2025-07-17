import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")
st.title("🧑‍💼 Detalhes do Funcionário - Vinicius")

SHEET_ID = "1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE"
BASE_ABA = "Base de Dados"

@st.cache_resource
def conectar_sheets():
    info = st.secrets["GCP_SERVICE_ACCOUNT"]
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = Credentials.from_service_account_info(info, scopes=escopo)
    cliente = gspread.authorize(credenciais)
    return cliente.open_by_key(SHEET_ID)

@st.cache_data
def carregar_dados():
    planilha = conectar_sheets()
    aba = planilha.worksheet(BASE_ABA)
    df = get_as_dataframe(aba).dropna(how="all")
    df.columns = [str(col).strip() for col in df.columns]
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df["Ano"] = df["Data"].dt.year.astype(int)
    return df

@st.cache_data
def carregar_despesas():
    planilha = conectar_sheets()
    aba_desp = planilha.worksheet("Despesas")
    df_desp = get_as_dataframe(aba_desp).dropna(how="all")
    df_desp.columns = [str(col).strip() for col in df_desp.columns]
    df_desp["Data"] = pd.to_datetime(df_desp["Data"], errors="coerce")
    df_desp = df_desp.dropna(subset=["Data"])
    df_desp["Ano"] = df_desp["Data"].dt.year.astype(int)
    return df_desp

df = carregar_dados()
df_despesas = carregar_despesas()

# ✅ Filtro fixo: apenas Vinicius
funcionario_escolhido = "Vinicius"
df = df[df["Funcionário"] == funcionario_escolhido]

anos = sorted(df["Ano"].dropna().unique().tolist(), reverse=True)
ano_escolhido = st.selectbox("🗕️ Filtrar por ano", anos)

df_func = df[df["Ano"] == ano_escolhido].copy()

# Aqui você pode continuar com os KPIs, gráficos e comparativos normalmente
st.write("✅ Dados carregados para:", funcionario_escolhido)
st.dataframe(df_func)
