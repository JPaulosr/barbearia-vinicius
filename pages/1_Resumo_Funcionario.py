import streamlit as st
import pandas as pd
import plotly.express as px
from unidecode import unidecode
from io import BytesIO
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")
st.title("🧑‍💼 Detalhes do Funcionário")

# === CONFIGURAÇÃO GOOGLE SHEETS ===
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

df = carregar_dados()

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

df_despesas = carregar_despesas()

# === FILTRAR SOMENTE DADOS DO VINICIUS ===
df = df[df["Funcionário"] == "Vinicius"]

# === Filtro por ano ===
anos = sorted(df["Ano"].dropna().unique().tolist(), reverse=True)
ano_escolhido = st.selectbox("🗕️ Filtrar por ano", anos)
df_func = df[df["Ano"] == ano_escolhido].copy()

# === Insights do Funcionário ===
st.subheader("📌 Insights do Funcionário")

# KPIs
col1, col2, col3, col4 = st.columns(4)
total_atendimentos = df_func.shape[0]
clientes_unicos = df_func["Cliente"].nunique()
total_receita = df_func["Valor"].sum()
ticket_medio_geral = df_func["Valor"].mean()

col1.metric("🔢 Total de atendimentos", total_atendimentos)
col2.metric("👥 Clientes únicos", clientes_unicos)
col3.metric("💰 Receita total", f"R$ {total_receita:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
col4.metric("🎫 Ticket médio", f"R$ {ticket_medio_geral:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

# Dia mais cheio
dia_mais_cheio = df_func.groupby(df_func["Data"].dt.date).agg({"Valor": "sum", "Cliente": "count"}).reset_index()
dia_mais_cheio = dia_mais_cheio.sort_values("Cliente", ascending=False).head(1)
if not dia_mais_cheio.empty:
    data_cheia = pd.to_datetime(dia_mais_cheio.iloc[0, 0]).strftime("%d/%m/%Y")
    qtd_atend = int(dia_mais_cheio.iloc[0, 2])
    valor_dia = dia_mais_cheio.iloc[0, 1] * 0.5
    valor_formatado = f"R$ {valor_dia:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    st.info(f"📅 Dia com mais atendimentos: **{data_cheia}** com **{qtd_atend} atendimentos** — Valor recebido: **{valor_formatado}**")

# Receita mensal
st.subheader("📊 Receita Mensal por Mês e Ano")
df_func["MesNome"] = df_func["Data"].dt.strftime("%b %Y")
df_func["MesNum"] = df_func["Data"].dt.month
df_receita = df_func.groupby(["MesNum", "MesNome"]).agg({"Valor": "sum"}).reset_index()
df_receita = df_receita.sort_values("MesNum")
df_receita["Comissão"] = df_receita["Valor"] * 0.5

df_receita["ComissãoFormat"] = df_receita["Comissão"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

fig = px.bar(df_receita, x="MesNome", y="Comissão", text="ComissãoFormat", labels={"Comissão": "Valor Recebido"})
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Exportação
buffer = BytesIO()
df_func.to_excel(buffer, index=False, sheet_name="Filtrado", engine="openpyxl")
st.download_button("📄 Baixar Excel com dados filtrados", data=buffer.getvalue(), file_name="dados_filtrados_vinicius.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
