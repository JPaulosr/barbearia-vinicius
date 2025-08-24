# -*- coding: utf-8 -*-
# 2_Adicionar_Atendimento.py — versão Vinicius

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread.utils import rowcol_to_a1
from datetime import datetime
import pytz
import unicodedata
import requests
from collections import Counter

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Adicionar Atendimento — Vinicius",
    page_icon="✂️",
    layout="wide"
)

SHEET_ID = "1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE"
ABA_DADOS = "Base de Dados"
STATUS_ABA = "clientes_status"

TZ = "America/Sao_Paulo"
DATA_FMT = "%d/%m/%Y"

# =========================
# FUNÇÕES AUXILIARES
# =========================
def now_br():
    return datetime.now(pytz.timezone(TZ))

def _fmt_brl(v: float) -> str:
    try:
        v = float(v)
    except Exception:
        v = 0.0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# GOOGLE SHEETS
# =========================
@st.cache_resource
def conectar_sheets():
    info = st.secrets["GCP_SERVICE_ACCOUNT"]
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = Credentials.from_service_account_info(info, scopes=escopo)
    cliente = gspread.authorize(credenciais)
    return cliente.open_by_key(SHEET_ID)

def carregar_base():
    aba = conectar_sheets().worksheet(ABA_DADOS)
    df = get_as_dataframe(aba).dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df, aba

def salvar_base(df_final: pd.DataFrame):
    aba = conectar_sheets().worksheet(ABA_DADOS)
    aba.clear()
    set_with_dataframe(aba, df_final, include_index=False, include_column_header=True)

# =========================
# UI
# =========================
st.title("📅 Adicionar Atendimento — Vinicius")

# Calendário em português — sempre no dia de hoje BR
hoje_br = now_br().date()
data_input = st.date_input("Data", value=hoje_br)
data = data_input.strftime("%d/%m/%Y")

# Mês em português sem Babel
MESES_PT = ["janeiro","fevereiro","março","abril","maio","junho","julho",
            "agosto","setembro","outubro","novembro","dezembro"]
st.caption(f"Data selecionada: {data_input.day} de {MESES_PT[data_input.month-1]} de {data_input.year}")

# Carregar base existente
df_existente, _ = carregar_base()
df_existente["_dt"] = pd.to_datetime(df_existente["Data"], format=DATA_FMT, errors="coerce")
df_2025 = df_existente[df_existente["_dt"].dt.year == 2025]

clientes_existentes = sorted(df_2025["Cliente"].dropna().unique())

# =========================
# FORMULÁRIO
# =========================
cA, cB = st.columns([2, 1])
with cA:
    cliente = st.selectbox("Nome do Cliente", clientes_existentes)
    novo_nome = st.text_input("Ou digite um novo nome de cliente")
    cliente = novo_nome if novo_nome else cliente
with cB:
    st.image("https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png",
             caption=(cliente or "Cliente"), width=200)

# Campos fixos só para Vinicius
funcionario = "Vinicius"
fase = "Dono + funcionário"

servico = st.text_input("Serviço")
valor = st.number_input("Valor", step=1.0, format="%.2f")

if st.button("💾 Salvar Atendimento"):
    if not servico or not cliente:
        st.warning("⚠️ Preencha cliente e serviço.")
    else:
        nova = {
            "Data": data,
            "Serviço": servico,
            "Valor": valor,
            "Conta": "Carteira",
            "Cliente": cliente,
            "Combo": "",
            "Funcionário": funcionario,
            "Fase": fase,
            "Tipo": "Serviço",
            "Período": "Manhã",
        }
        df_final = pd.concat([df_existente, pd.DataFrame([nova])], ignore_index=True)
        salvar_base(df_final)
        st.success(f"✅ Atendimento salvo para {cliente} em {data} — {servico} ({_fmt_brl(valor)})")
