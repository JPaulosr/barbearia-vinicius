import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Detalhes Funcionário", layout="wide")
st.markdown("<h1>👨‍💼 Detalhes do Funcionário - Vinicius</h1>", unsafe_allow_html=True)

# FUNÇÃO PARA CARREGAR DADOS DO GOOGLE SHEETS
@st.cache_data
def carregar_dados_google_sheets(sheet_url, aba_nome):
    escopo = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credenciais = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_url(sheet_url)
    aba = planilha.worksheet(aba_nome)
    dados = aba.get_all_records()
    return pd.DataFrame(dados)

# CARREGAR DADOS
sheet_url = 'https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/edit?usp=sharing'
df = carregar_dados_google_sheets(sheet_url, 'Base de Dados')

# TRATAMENTO
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
df = df[df['Funcionario'] == 'Vinicius']

# SIDEBAR/FILTROS
anos = sorted(df['Data'].dt.year.unique())
ano = st.selectbox("📅 Filtrar por ano", anos)

df_filtrado = df[df['Data'].dt.year == ano]

mes = st.selectbox("📅 Filtrar por mês", ['Todos'] + sorted(df_filtrado['Data'].dt.month.unique().tolist()))
if mes != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Data'].dt.month == mes]

dia = st.selectbox("📅 Filtrar por dia", ['Todos'] + sorted(df_filtrado['Data'].dt.day.unique().tolist()))
if dia != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Data'].dt.day == dia]

semana = st.selectbox("📅 Filtrar por semana", ['Todas'] + sorted(df_filtrado['Data'].dt.isocalendar().week.unique().tolist()))
if semana != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Data'].dt.isocalendar().week == semana]

tipos_servico = st.multiselect("💈 Filtrar por tipo de serviço", options=df_filtrado['Tipo'].unique())
if tipos_servico:
    df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipos_servico)]

# INSIGHTS
total_atendimentos = df_filtrado.shape[0]
clientes_unicos = df_filtrado['Cliente'].nunique()
receita_total = df_filtrado['Valor'].sum()
ticket_medio = receita_total / total_atendimentos if total_atendimentos > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total de atendimentos", total_atendimentos)
col2.metric("👥 Clientes únicos", clientes_unicos)
col3.metric("💰 Receita total", f"R$ {receita_total:,.2f}".replace(".", ","))
col4.metric("💳 Ticket médio", f"R$ {ticket_medio:,.2f}".replace(".", ","))

# MAIOR DIA DE ATENDIMENTOS
if not df_filtrado.empty:
    dia_maior = df_filtrado['Data'].value_counts().idxmax()
    qtd_maior = df_filtrado['Data'].value_counts().max()
    st.info(f"📅 Dia com mais atendimentos: {dia_maior.strftime('%d/%m/%Y')} com {qtd_maior} atendimentos")

# ATENDIMENTOS POR DIA DA SEMANA
df_filtrado['DiaSemana'] = df_filtrado['Data'].dt.day_name().str[:3]
dias_ordem = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
df_semana = df_filtrado['DiaSemana'].value_counts().reindex(dias_ordem).fillna(0).reset_index()
df_semana.columns = ['DiaSemana', 'Qtd']

st.markdown("### 📅 Atendimentos por dia da semana")
fig1 = px.bar(df_semana, x='DiaSemana', y='Qtd', text='Qtd', color_discrete_sequence=['#7B83EB'])
st.plotly_chart(fig1, use_container_width=True)

# RECEITA MENSAL
df_filtrado['AnoMes'] = df_filtrado['Data'].dt.to_period('M')
df_mes = df_filtrado.groupby('AnoMes')['Valor'].sum().reset_index()
df_mes['AnoMes'] = df_mes['AnoMes'].astype(str)

st.markdown("### 📊 Receita Mensal por Mês e Ano")
fig2 = px.bar(df_mes, x='AnoMes', y='Valor', text='Valor', color_discrete_sequence=['#82C9FF'])
fig2.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
fig2.update_layout(xaxis_title="Mês", yaxis_title="Receita (R$)")
st.plotly_chart(fig2, use_container_width=True)
