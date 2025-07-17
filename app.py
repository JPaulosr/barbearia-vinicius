import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------- CONFIGURAÇÕES INICIAIS ------------------------
st.set_page_config(page_title="Painel Vinicius", layout="wide")
st.title("💪 Painel da Barbearia - Versão Vinicius")

st.markdown("""
<div style="background-color:#003049;padding:10px;border-radius:5px">
    <span style="color:white;">Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.</span>
</div>
""", unsafe_allow_html=True)

# ------------------------- CARREGAR PLANILHA DO GOOGLE ------------------------

@st.cache_data
def carregar_base_vinicius():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/gviz/tq?tqx=out:csv&sheet=Base%20de%20Dados"
    df = pd.read_csv(url, encoding="utf-8")

    # Filtrar atendimentos do Vinicius
    df = df[df["Funcionário"] == "Vinicius"]

    # Converter a data corretamente
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

    # Corrigir e converter a coluna "Valor"
    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "")
        .str.replace(",", ".")
    )
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    return df

# ------------------------- INÍCIO DO APP ------------------------

try:
    df = carregar_base_vinicius()

    # Subtítulo com o mês atual
    st.subheader("📆 Mês atual - Resumo")

    # Filtro para mês e ano atual
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    df_mes_atual = df[(df["Data"].dt.month == mes_atual) & (df["Data"].dt.year == ano_atual)]

    # Cálculo da receita líquida do mês
    receita_atual = df_mes_atual["Valor"].sum()

    # Exibição do indicador
    st.metric("💰 Receita Total no Mês (Líquida)", f"R$ {receita_atual:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
