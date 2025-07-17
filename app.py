import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(
    page_title="Barbearia - Painel do Vinicius",
    page_icon="💈",
    layout="wide"
)

# ========== ESTILO ==========
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stSidebar"] {
        background-color: #161a23;
        color: white;
    }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("💈 Painel da Barbearia - Versão Vinicius")

# ========== CARREGAR DADOS ==========
@st.cache_data
def carregar_base_vinicius():
    escopos = ["https://www.googleapis.com/auth/spreadsheets"]
    credenciais = Credentials.from_service_account_info(
        st.secrets["GCP_SERVICE_ACCOUNT"], scopes=escopos
    )
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_url(st.secrets["PLANILHA_URL"])
    aba = planilha.worksheet("Base de Dados")
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    df["Data"] = pd.to_datetime(df["Data"])
    df = df[df["Funcionário"] == "Vinicius"]
    return df

df = carregar_base_vinicius()

# ========== FILTRAR MÊS ATUAL E ANTERIOR ==========
hoje = datetime.today()
mes_atual = hoje.month
ano_atual = hoje.year

df_mes_atual = df[(df["Data"].dt.month == mes_atual) & (df["Data"].dt.year == ano_atual)]
df_mes_anterior = df[(df["Data"].dt.month == (mes_atual - 1)) & (df["Data"].dt.year == ano_atual)]

# ========== CÁLCULO DE ATENDIMENTOS (considerando combos corretamente) ==========
def contar_atendimentos(df_raw):
    df_raw = df_raw.copy()
    # A partir de 11/05/2025, considerar agrupamento por cliente + data
    df_raw["Data"] = pd.to_datetime(df_raw["Data"])
    corte_data = pd.to_datetime("2025-05-11")
    antes = df_raw[df_raw["Data"] < corte_data]
    depois = df_raw[df_raw["Data"] >= corte_data]
    atend_antes = len(antes)
    atend_depois = depois.drop_duplicates(subset=["Cliente", "Data"])
    total = atend_antes + len(atend_depois)
    return total

# ========== MÉTRICAS ==========
atendimentos_atual = contar_atendimentos(df_mes_atual)
atendimentos_anterior = contar_atendimentos(df_mes_anterior)

receita_atual = df_mes_atual["Valor líquido"].sum()
receita_anterior = df_mes_anterior["Valor líquido"].sum()

# ========== VARIAÇÕES ==========
def calc_variacao(valor_atual, valor_ant):
    if valor_ant == 0:
        return "—"
    return f"{((valor_atual - valor_ant) / valor_ant) * 100:.1f}%"

var_atend = calc_variacao(atendimentos_atual, atendimentos_anterior)
var_receita = calc_variacao(receita_atual, receita_anterior)

# ========== EXIBIR ==========
st.info("Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.")

st.subheader("📊 Resumo do mês atual")

col1, col2 = st.columns(2)
with col1:
    st.metric("👥 Atendimentos no mês", atendimentos_atual, delta=var_atend)
with col2:
    st.metric("💰 Receita líquida no mês", f"R$ {receita_atual:,.2f}", delta=var_receita)

st.success("Painel carregado com sucesso ✅")
