import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Painel Vinicius", layout="wide")
st.title("💪 Painel da Barbearia - Versão Vinicius")

st.markdown("""
<div style="background-color:#003049;padding:10px;border-radius:5px">
    <span style="color:white;">Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.</span>
</div>
""", unsafe_allow_html=True)

# ------------------------- FUNÇÃO ROBUSTA DE CARREGAMENTO ------------------------
@st.cache_data
def carregar_base_vinicius():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/gviz/tq?tqx=out:csv&sheet=Base%20de%20Dados"
    df = pd.read_csv(url, encoding="utf-8")

    # Limpa e padroniza colunas
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    # Detecta automaticamente a coluna de valor
    col_valor = next((col for col in df.columns if "valor" in col.lower()), None)
    if not col_valor:
        st.write("Colunas disponíveis:", df.columns.tolist())
        raise ValueError("❌ Coluna 'Valor' não encontrada.")

    df.rename(columns={col_valor: "Valor"}, inplace=True)

    # Filtra apenas Vinicius
    df = df[df["Funcionario"] == "Vinicius"]

    # Converte data e valor
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
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

    # Mês e ano atual
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # Mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual

    # Filtros
    df_mes_atual = df[(df["Data"].dt.month == mes_atual) & (df["Data"].dt.year == ano_atual)]
    df_mes_anterior = df[(df["Data"].dt.month == mes_anterior) & (df["Data"].dt.year == ano_anterior)]

    # Receita total
    receita_atual = df_mes_atual["Valor"].sum()
    receita_anterior = df_mes_anterior["Valor"].sum()

    # Variação %
    if receita_anterior > 0:
        variacao = ((receita_atual - receita_anterior) / receita_anterior) * 100
    else:
        variacao = 0

    col1, col2 = st.columns(2)
    col1.metric("💰 Receita Total no Mês (Líquida)", f"R$ {receita_atual:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","), f"{variacao:.1f}% em relação ao mês anterior")
    col2.metric("📅 Atendimentos no Mês", len(df_mes_atual))

    st.markdown("---")

    # ------------------------- GRÁFICO DE EVOLUÇÃO DIÁRIA ------------------------
    st.subheader("📊 Evolução Diária da Receita (Mês Atual)")
    df_dia = df_mes_atual.groupby(df_mes_atual["Data"].dt.date)["Valor"].sum().reset_index()
    fig = px.bar(df_dia, x="Data", y="Valor", text_auto=True, labels={"Data": "Dia", "Valor": "Receita (R$)"})
    fig.update_layout(xaxis_title="Data", yaxis_title="Receita (R$)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------- TOP CLIENTES ------------------------
    st.subheader("👤 Top 5 Clientes por Receita no Mês Atual")
    top_clientes = df_mes_atual.groupby("Cliente")["Valor"].sum().sort_values(ascending=False).head(5).reset_index()
    st.table(top_clientes.rename(columns={"Cliente": "Cliente", "Valor": "Receita (R$)"}))

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
