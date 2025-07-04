import streamlit as st
import os

st.set_page_config(
    page_title="Barbearia - Painel do Vinicius",
    page_icon="💈",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161a23; }
    </style>
""", unsafe_allow_html=True)

st.title("💈 Painel da Barbearia - Versão Vinicius")

st.info("Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.")

# Oculta mensagens desnecessárias do Streamlit
st.markdown("""
    <style>
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.success("Painel carregado com sucesso ✅")
