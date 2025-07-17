# Arquivo: 1_Resumo_Funcionario.py (versão exclusiva do Vinicius)

import streamlit as st
import pandas as pd
import plotly.express as px
from unidecode import unidecode
from io import BytesIO
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")
st.title("🧑‍💼 Resumo Funcionário - Vinicius")

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

# === Dados fixos para Vinicius ===
funcionario_escolhido = "Vinicius"
anos = sorted(df[df["Funcionário"] == funcionario_escolhido]["Ano"].dropna().unique(), reverse=True)
ano_escolhido = st.selectbox("🗕️ Filtrar por ano", anos)

df_func = df[(df["Funcionário"] == funcionario_escolhido) & (df["Ano"] == ano_escolhido)].copy()

# Filtros por mês, dia, semana
col_filtros = st.columns(3)
meses_disponiveis = df_func["Data"].dt.month.unique()
meses_disponiveis.sort()
mes_filtro = col_filtros[0].selectbox("📆 Filtrar por mês", options=["Todos"] + list(meses_disponiveis))
if mes_filtro != "Todos":
    df_func = df_func[df_func["Data"].dt.month == mes_filtro]

dias_disponiveis = df_func["Data"].dt.day.unique()
dias_disponiveis.sort()
dia_filtro = col_filtros[1].selectbox("📅 Filtrar por dia", options=["Todos"] + list(dias_disponiveis))
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

# === KPIs
st.subheader("📌 Insights do Funcionário")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔢 Total de atendimentos", df_func.shape[0])
col2.metric("👥 Clientes únicos", df_func["Cliente"].nunique())
col3.metric("💰 Receita total (50%)", f"R$ {df_func['Valor'].sum() * 0.5:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
col4.metric("🎫 Ticket médio (50%)", f"R$ {df_func['Valor'].mean() * 0.5:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

# === Dia com mais atendimentos (valor líquido - 50%)
dia_top = (
    df_func.groupby("Data")
    .agg(Qtd_Atendimentos=('Cliente', 'count'), Valor_Bruto=('Valor', 'sum'))
    .reset_index()
)

if not dia_top.empty:
    dia_maior = dia_top.sort_values("Qtd_Atendimentos", ascending=False).iloc[0]
    data_formatada = dia_maior["Data"].strftime("%d/%m/%Y")
    qtd = int(dia_maior["Qtd_Atendimentos"])
    valor_liquido = dia_maior["Valor_Bruto"] * 0.5  # 50%
    valor_formatado = f"R$ {valor_liquido:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    st.info(f"📅 Dia com mais atendimentos: {data_formatada} com {qtd} atendimentos — Valor recebido: {valor_formatado}")

# === Gráfico: Atendimentos por dia da semana
st.markdown("### 📆 Atendimentos por dia da semana")
dias_semana = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
df_func["DiaSemana"] = df_func["Data"].dt.dayofweek.map(dias_semana)
grafico_semana = df_func.groupby("DiaSemana").size().reset_index(name="Qtd Atendimentos")
grafico_semana = grafico_semana.sort_values("DiaSemana", key=lambda x: x.map(dias_semana))
st.plotly_chart(px.bar(grafico_semana, x="DiaSemana", y="Qtd Atendimentos", text_auto=True, template="plotly_white"), use_container_width=True)

# === Receita mensal
st.subheader("📊 Receita Mensal")
meses_pt = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
df_func["MesNum"] = df_func["Data"].dt.month
df_func["MesNome"] = df_func["MesNum"].map(meses_pt) + df_func["Data"].dt.strftime(" %Y")
receita_mensal = df_func.groupby(["MesNum", "MesNome"])["Valor"].sum().reset_index()
receita_mensal = receita_mensal.sort_values("MesNum")
receita_mensal["Valor Formatado"] = receita_mensal["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

fig_receita = px.bar(receita_mensal, x="MesNome", y="Valor", text="Valor Formatado", template="plotly_white")
fig_receita.update_traces(textposition="outside", cliponaxis=False)
st.plotly_chart(fig_receita, use_container_width=True)

# === Comparativo real
comissao_real = df_despesas[
    (df_despesas["Prestador"] == "Vinicius") & 
    (df_despesas["Descrição"].str.contains("comissão", case=False, na=False)) & 
    (df_despesas["Ano"] == ano_escolhido)
]["Valor"].sum()

bruto = df_func["Valor"].sum()
receita_liquida = comissao_real
salao_ficou = bruto - comissao_real

comparativo = pd.DataFrame({
    "Tipo": ["Receita Bruta", "Receita (comissão real)", "Lucro para o salão"],
    "Valor": [bruto, receita_liquida, salao_ficou]
})
comparativo["Valor Formatado"] = comparativo["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
st.subheader("💸 Comparativo da Receita")
st.dataframe(comparativo[["Tipo", "Valor Formatado"]], use_container_width=True)

# === Histórico
st.subheader("🗒️ Histórico de Atendimentos")
st.dataframe(df_func.sort_values("Data", ascending=False), use_container_width=True)

# === Exportação
st.subheader("📄 Exportar dados")
buffer = BytesIO()
df_func.to_excel(buffer, index=False, sheet_name="Filtrado", engine="openpyxl")
st.download_button("Baixar Excel com dados filtrados", data=buffer.getvalue(), file_name="dados_vinicius.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
