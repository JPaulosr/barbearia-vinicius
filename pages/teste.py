import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(page_title="Comissões Recebidas", layout="wide")
st.title("💸 Comissões Recebidas - Vinicius")

# === Autenticar e carregar dados ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_URL = st.secrets["PLANILHA_URL"]

@st.cache_resource

def conectar_planilha():
    creds = Credentials.from_service_account_info(
        st.secrets["GCP_SERVICE_ACCOUNT"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    planilha = client.open_by_url(SHEET_URL)
    return planilha

@st.cache_data

def carregar_despesas():
    planilha = conectar_planilha()
    aba = planilha.worksheet("Despesas")
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors='coerce')
    return df

# === Processar dados ===
df_despesas = carregar_despesas()
df_vinicius = df_despesas[df_despesas["Descricao"].str.contains("Vinicius", case=False, na=False)]

if df_vinicius.empty:
    st.warning("Nenhuma comissão encontrada para Vinicius.")
    st.stop()

# Agrupar por mês
comissoes_mes = df_vinicius.copy()
comissoes_mes["AnoMes"] = comissoes_mes["Data"].dt.to_period("M").astype(str)
resumo = comissoes_mes.groupby("AnoMes")["Valor"].sum().reset_index()
resumo = resumo.sort_values("AnoMes")

# === Exibir gráfico ===
st.subheader("📊 Gráfico de Comissões Recebidas")
fig = px.bar(resumo, x="AnoMes", y="Valor", text_auto=True,
             labels={"AnoMes": "Mês", "Valor": "Valor Recebido (R$)"},
             title="Comissões recebidas por mês")
st.plotly_chart(fig, use_container_width=True)

# === Exibir tabela detalhada ===
st.subheader("📋 Tabela de Comissões")
st.dataframe(resumo.rename(columns={"AnoMes": "Mês", "Valor": "Total Recebido (R$)"}), use_container_width=True)

# === Total acumulado ===
st.metric("💰 Total Recebido:", f"R$ {resumo['Valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
