import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Função para carregar dados do Google Sheets
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/export?format=csv&id=1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE&gid=0"
    df = pd.read_csv(url)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["Dia"] = df["Data"].dt.day
    df["Semana"] = df["Data"].dt.isocalendar().week
    df["DiaSemana"] = df["Data"].dt.day_name().str[:3]
    return df

# Layout da página
st.title("👨‍💼 Detalhes do Funcionário - Vinicius")
df = carregar_dados()
df = df[df["Profissional"] == "Vinicius"]

# Filtros
anos = sorted(df["Ano"].unique(), reverse=True)
ano = st.selectbox("📆 Filtrar por ano", anos)
df = df[df["Ano"] == ano]

mes = st.selectbox("📅 Filtrar por mês", ["Todos"] + sorted(df["Mes"].unique()))
if mes != "Todos":
    df = df[df["Mes"] == mes]

dia = st.selectbox("📅 Filtrar por dia", ["Todos"] + sorted(df["Dia"].unique()))
if dia != "Todos":
    df = df[df["Dia"] == dia]

semana = st.selectbox("📅 Filtrar por semana", ["Todas"] + sorted(df["Semana"].unique()))
if semana != "Todas":
    df = df[df["Semana"] == semana]

servicos_disponiveis = df["Tipo"].dropna().unique().tolist()
tipo_servico = st.multiselect("🧾 Filtrar por tipo de serviço", servicos_disponiveis)
if tipo_servico:
    df = df[df["Tipo"].isin(tipo_servico)]

# Insights
col1, col2, col3, col4 = st.columns(4)
col1.metric("📘 Total de atendimentos", len(df))
col2.metric("👥 Clientes únicos", df["Cliente"].nunique())
col3.metric("💰 Receita total", f"R$ {df['Valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col4.metric("💳 Ticket médio", f"R$ {df['Valor'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Dia com mais atendimentos
if not df.empty:
    dia_top = df.groupby("Data").size().sort_values(ascending=False).reset_index()
    top_data = dia_top.iloc[0, 0].strftime("%d/%m/%Y")
    top_qtd = dia_top.iloc[0, 1]
    st.info(f"📅 Dia com mais atendimentos: {top_data} com {top_qtd} atendimentos")

# Atendimentos por dia da semana
st.subheader("📅 Atendimentos por dia da semana")
df_semana = df.groupby("DiaSemana").size().reindex(["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"])
fig1 = px.bar(x=df_semana.index, y=df_semana.values, labels={"x": "DiaSemana", "y": "Qtd Atendimentos"}, text=df_semana.values)
fig1.update_traces(marker_color="#788bff", textposition="outside")
fig1.update_layout(xaxis_title="Dia da Semana", yaxis_title="Quantidade", showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# Receita mensal
st.subheader("📊 Receita Mensal por Mês e Ano")
df_mes = df.groupby("Mes")["Valor"].sum().reset_index()
df_mes["MesNome"] = df_mes["Mes"].apply(lambda x: datetime(2025, x, 1).strftime("%B %Y"))
fig2 = px.bar(df_mes, x="MesNome", y="Valor", text="Valor", labels={"Valor": "Receita (R$)", "MesNome": "Mês"})
fig2.update_traces(marker_color="lightskyblue", texttemplate="R$ %{text:,.2f}", textposition="outside")
fig2.update_layout(xaxis_title="Mês", yaxis_title="Receita", showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

st.caption("Dados exclusivos do funcionário Vinicius.")
