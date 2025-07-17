import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Barbearia - Painel do Vinicius",
    page_icon="📈",
    layout="wide"
)

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

st.title("🖔 Painel da Barbearia - Versão Vinicius")
st.info("Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.")

@st.cache_data
def carregar_base_vinicius():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/export?format=csv&id=1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE&gid=0"
    df = pd.read_csv(url, encoding="utf-8")
    df.columns = df.columns.str.strip()  # Remove espaços extras
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df["Valor"] = pd.to_numeric(df["Valor"].replace("R$", "", regex=True).str.replace(",", "."), errors="coerce")
    df = df[df["Funcionário"] == "Vinicius"]
    return df

df = carregar_base_vinicius()

# Filtro por mês atual e anterior
hoje = datetime.today()
mes_atual = hoje.month
ano_atual = hoje.year

mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1

df_mes_atual = df[(df["Data"].dt.month == mes_atual) & (df["Data"].dt.year == ano_atual)]
df_mes_anterior = df[(df["Data"].dt.month == mes_anterior) & (df["Data"].dt.year == ano_anterior)]

# Receita líquida = 50% do valor bruto
receita_atual = df_mes_atual["Valor"].sum() * 0.5
receita_anterior = df_mes_anterior["Valor"].sum() * 0.5

atendimentos_atual = len(df_mes_atual)
atendimentos_anterior = len(df_mes_anterior)

# Cálculo de diferenças
dif_receita = receita_atual - receita_anterior
dif_percentual = (dif_receita / receita_anterior) * 100 if receita_anterior > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("Atendimentos no mês", atendimentos_atual, f"{atendimentos_atual - atendimentos_anterior:+}")
col2.metric("Receita líquida (50%)", f"R$ {receita_atual:,.2f}", f"R$ {dif_receita:,.2f}")
col3.metric("Variação (%)", f"{dif_percentual:.1f}%", delta_color="normal")

st.success("Painel carregado com dados reais do Vinicius ✅")
