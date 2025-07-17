import streamlit as st
import pandas as pd
import plotly.express as px
from unidecode import unidecode
from io import BytesIO
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")
st.title("🧑‍💼 Detalhes do Funcionário - Vinicius")

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

# === FILTRAR APENAS VINICIUS ===
df = df[df["Funcionário"] == "Vinicius"].copy()

# === Filtro por ano ===
anos = sorted(df["Ano"].dropna().unique().tolist(), reverse=True)
ano_escolhido = st.selectbox("🗕️ Filtrar por ano", anos)
df_func = df[df["Ano"] == ano_escolhido].copy()

# === Filtros adicionais ===
col_filtros = st.columns(3)

# Filtro por mês
meses_disponiveis = df_func["Data"].dt.month.unique()
meses_disponiveis.sort()
mes_filtro = col_filtros[0].selectbox("📆 Filtrar por mês", options=["Todos"] + list(meses_disponiveis))
if mes_filtro != "Todos":
    df_func = df_func[df_func["Data"].dt.month == mes_filtro]

# Filtro por dia
dias_disponiveis = df_func["Data"].dt.day.unique()
dias_disponiveis.sort()
dia_filtro = col_filtros[1].selectbox("📅 Filtrar por dia", options=["Todos"] + list(dias_disponiveis))
if dia_filtro != "Todos":
    df_func = df_func[df_func["Data"].dt.day == dia_filtro]

# Filtro por semana
df_func["Semana"] = df_func["Data"].dt.isocalendar().week
semanas_disponiveis = df_func["Semana"].unique().tolist()
semanas_disponiveis.sort()
semana_filtro = col_filtros[2].selectbox("🗓️ Filtrar por semana", options=["Todas"] + list(semanas_disponiveis))
if semana_filtro != "Todas":
    df_func = df_func[df_func["Semana"] == semana_filtro]

# === Filtro por tipo de serviço ===
tipos_servico = df_func["Serviço"].dropna().unique().tolist()
tipo_selecionado = st.multiselect("Filtrar por tipo de serviço", tipos_servico)
if tipo_selecionado:
    df_func = df_func[df_func["Serviço"].isin(tipo_selecionado)]

# === Insights ===
st.subheader("📌 Insights do Funcionário")
col1, col2, col3, col4 = st.columns(4)
total_atendimentos = df_func.shape[0]
clientes_unicos = df_func["Cliente"].nunique()
total_receita = df_func["Valor"].sum()
ticket_medio_geral = df_func["Valor"].mean()
col1.metric("🔢 Total de atendimentos", total_atendimentos)
col2.metric("👥 Clientes únicos", clientes_unicos)
col3.metric("💰 Receita total", f"R$ {total_receita:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
col4.metric("🎫 Ticket médio", f"R$ {ticket_medio_geral:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

# === Receita mensal (com 50%) ===
st.subheader("📊 Receita Mensal (com 50% aplicado)")
meses_pt = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
df_func["MesNum"] = df_func["Data"].dt.month
df_func["MesNome"] = df_func["MesNum"].map(meses_pt) + df_func["Data"].dt.strftime(" %Y")
df_func["Receita_50"] = df_func["Valor"] * 0.5
receita_mensal = df_func.groupby(["MesNum", "MesNome"])["Receita_50"].sum().reset_index()
receita_mensal = receita_mensal.sort_values("MesNum")
receita_mensal["Valor Formatado"] = receita_mensal["Receita_50"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
fig_receita = px.bar(
    receita_mensal,
    x="MesNome",
    y="Receita_50",
    text="Valor Formatado",
    template="plotly_white",
    labels={"Receita_50": "Valor Recebido"}
)
fig_receita.update_traces(textposition="outside", cliponaxis=False)
st.plotly_chart(fig_receita, use_container_width=True)

# === Histórico de atendimentos ===
st.subheader("📄 Histórico de Atendimentos")
st.dataframe(df_func.sort_values("Data", ascending=False), use_container_width=True)

# === Exportar dados ===
st.subheader("📥 Exportar dados filtrados")
buffer = BytesIO()
df_func.to_excel(buffer, index=False, sheet_name="Filtrado", engine="openpyxl")
st.download_button("Baixar Excel com dados filtrados", data=buffer.getvalue(), file_name="dados_filtrados_vinicius.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
