import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🧑‍💼 Detalhes do Funcionário - Vinicius</h1>", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    url_dados = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/export?format=csv&id=1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE&gid=0"
    df = pd.read_csv(url_dados)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors='coerce')
    df = df[df["Profissional"] == "Vinicius"]
    df = df[df["Status"] != "Desmarcado"]
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df.dropna(subset=["Valor", "Data"])
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["DiaSemana"] = df["Data"].dt.day_name().str[:3]
    return df

df = carregar_dados()

# Filtros
col1, col2, col3, col4 = st.columns(4)
anos = sorted(df['Ano'].unique(), reverse=True)
meses = ['Todos'] + list(range(1, 13))
dias_semana = ['Todas'] + list(df['DiaSemana'].unique())

ano = col1.selectbox("📅 Filtrar por ano", anos)
mes = col2.selectbox("📅 Filtrar por mês", meses)
dia_semana = col3.selectbox("📅 Filtrar por dia", dias_semana)

df_filtrado = df[df['Ano'] == ano]
if mes != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Mes'] == mes]
if dia_semana != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['DiaSemana'] == dia_semana]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("📅 Total de atendimentos", len(df_filtrado))
col2.metric("🧑‍🤝‍🧑 Clientes únicos", df_filtrado["Cliente"].nunique())
col3.metric("💰 Receita (50%)", f"R$ {df_filtrado['Valor'].sum() * 0.5:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Gráfico: Atendimentos por Dia da Semana (dados reais)
st.markdown("### 🗓️ Atendimentos por dia da semana")
dias_ordenados = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
df_semana = df_filtrado.copy()
df_semana['DiaSemana'] = pd.Categorical(df_semana['DiaSemana'], categories=dias_ordenados, ordered=True)
grafico_semana = df_semana['DiaSemana'].value_counts().sort_index().reset_index()
grafico_semana.columns = ['DiaSemana', 'Qtd Atendimentos']
fig_dia_semana = px.bar(grafico_semana, x='DiaSemana', y='Qtd Atendimentos',
                        text='Qtd Atendimentos', color_discrete_sequence=['#7f7fff'])
fig_dia_semana.update_layout(xaxis_title="DiaSemana", yaxis_title="Qtd Atendimentos", template="plotly_dark")
st.plotly_chart(fig_dia_semana, use_container_width=True)

# Receita por Mês
st.markdown("### 📊 Receita Mensal por Mês e Ano")
df_receita = df_filtrado.groupby(['Ano', 'Mes'])['Valor'].sum().reset_index()
df_receita['DataLabel'] = pd.to_datetime(df_receita[['Ano', 'Mes']].assign(DAY=1), errors='coerce')
df_receita = df_receita.dropna(subset=["DataLabel"])
df_receita['Valor'] = df_receita['Valor'] * 0.5
fig_receita = px.bar(df_receita.sort_values("DataLabel"),
                     x="DataLabel", y="Valor",
                     text_auto='.2s',
                     labels={"Valor": "Receita (R$)", "DataLabel": "Mês"},
                     color_discrete_sequence=["skyblue"])
fig_receita.update_layout(template="plotly_dark")
st.plotly_chart(fig_receita, use_container_width=True)
