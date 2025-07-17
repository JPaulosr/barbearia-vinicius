import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# ========== SENHA ========== #
SENHA_CORRETA = "vinicius2025"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    with st.form("form_login", clear_on_submit=True):
        senha = st.text_input("🔐 Digite a senha para acessar:", type="password")
        entrar = st.form_submit_button("Entrar")
        if entrar:
            if senha == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.success("✅ Acesso liberado. Carregando painel...")
                st.experimental_rerun()
            else:
                st.error("❌ Senha incorreta. Tente novamente.")
    st.stop()
    
import streamlit as st
import pandas as pd
import plotly.express as px
from unidecode import unidecode
from io import BytesIO
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")
st.title("🧑‍💼 Detalhes do Funcionário Vinicius")

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

# === Filtra apenas Vinicius ===
df = df[df["Funcionário"] == "Vinicius"]
anos = sorted(df["Ano"].dropna().unique().tolist(), reverse=True)
ano_escolhido = st.selectbox("🕕️ Filtrar por ano", anos)
df_func = df[df["Ano"] == ano_escolhido].copy()

# === Filtros adicionais ===
col_filtros = st.columns(3)
meses_disponiveis = df_func["Data"].dt.month.unique()
meses_disponiveis.sort()
mes_filtro = col_filtros[0].selectbox("🗖️ Filtrar por mês", options=["Todos"] + list(meses_disponiveis))
if mes_filtro != "Todos":
    df_func = df_func[df_func["Data"].dt.month == mes_filtro]

dias_disponiveis = df_func["Data"].dt.day.unique()
dias_disponiveis.sort()
dia_filtro = col_filtros[1].selectbox("🗕️ Filtrar por dia", options=["Todos"] + list(dias_disponiveis))
if dia_filtro != "Todos":
    df_func = df_func[df_func["Data"].dt.day == dia_filtro]

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

# === KPIs ===
st.subheader("📌 Indicadores Gerais")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔢 Total de atendimentos", df_func.shape[0])
col2.metric("👥 Clientes únicos", df_func["Cliente"].nunique())
col3.metric("💰 Receita total", f"R$ {df_func['Valor'].sum():,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
col4.metric("🎼 Ticket médio", f"R$ {df_func['Valor'].mean():,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

# === Exportar dados ===
st.subheader("📄 Exportar dados filtrados")
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_func.to_excel(writer, index=False, sheet_name="Vinicius")
buffer.seek(0)
st.download_button(
    label="Baixar Excel com dados filtrados",
    data=buffer,
    file_name="vinicius_dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
