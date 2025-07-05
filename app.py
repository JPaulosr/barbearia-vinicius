import streamlit as st

st.set_page_config(
    page_title="Barbearia - Painel do Vinicius",
    page_icon="💈",
    layout="wide"
)

# Estilo visual escuro
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

# Sidebar com links para páginas
with st.sidebar:
    st.header("📚 Navegação")
    st.page_link("pages/1_Resumo_Funcionario.py", label="Resumo do Funcionário", icon="📊")
    st.page_link("pages/2_Frequencia_Clientes.py", label="Frequência dos Clientes", icon="👥")
    st.page_link("pages/3_Galeria_Clientes.py", label="Galeria de Clientes", icon="🖼️")
    st.page_link("pages/4_Tempos_Atendimento.py", label="Tempos de Atendimento", icon="⏱️")
    st.page_link("pages/5_Clientes_Detalhes.py", label="Detalhes dos Clientes", icon="📋")

# Conteúdo principal
st.title("💈 Painel da Barbearia - Versão Vinicius")
st.info("Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.")
st.success("Painel carregado com sucesso ✅")
