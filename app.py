import streamlit as st

st.set_page_config(
    page_title="Barbearia - Painel do Vinicius",
    page_icon="💈",
    layout="wide"
)

# Estilo visual escuro personalizado
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

# Conteúdo principal da página inicial
st.title("💈 Painel da Barbearia - Versão Vinicius")

st.info("Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.")

st.success("Painel carregado com sucesso ✅")
