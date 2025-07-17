import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Painel da Barbearia - Versão Vinicius", layout="wide")
st.title("🦶 Painel da Barbearia - Versão Vinicius")

st.markdown(
    "<div style='background-color:#002b45;padding:10px;border-radius:10px'>"
    "<p style='color:white;text-align:center'>Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.</p>"
    "</div>", unsafe_allow_html=True
)

@st.cache_data
def carregar_base_vinicius():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/export?format=csv&gid=0"
    df = pd.read_csv(url, encoding='utf-8')

    # Ajustes nas colunas
    df.columns = df.columns.str.strip()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Valor"] = pd.to_numeric(df["Valor"].replace("R\$", "", regex=True).str.replace(",", "."), errors="coerce")

    # Filtrar apenas os atendimentos do Vinicius
    df = df[df["Funcionário"] == "Vinicius"]

    return df

try:
    df = carregar_base_vinicius()

    # Exemplo de indicador: Receita do mês atual (sem comissão do salão)
    hoje = datetime.now()
    df_mes_atual = df[(df["Data"].dt.month == hoje.month) & (df["Data"].dt.year == hoje.year)]
    receita_atual = df_mes_atual["Valor"].sum()

    st.metric("💰 Receita bruta (mês atual)", f"R$ {receita_atual:,.2f}".replace(".", "X").replace(",", ".").replace("X", ","))

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
