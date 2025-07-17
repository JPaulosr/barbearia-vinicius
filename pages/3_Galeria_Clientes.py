import streamlit as st
import pandas as pd
import gspread
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from google.oauth2.service_account import Credentials
import cloudinary
import cloudinary.uploader

st.set_page_config(page_title="Galeria de Clientes", layout="wide")
st.title("❤️ Galeria de Clientes")

# ========== LOGO PADRÃO ==========
LOGO_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# ========== CONFIGURAR CLOUDINARY ==========
cloudinary.config(
    cloud_name=st.secrets["CLOUDINARY"]["cloud_name"],
    api_key=st.secrets["CLOUDINARY"]["api_key"],
    api_secret=st.secrets["CLOUDINARY"]["api_secret"]
)

# ========== FUNÇÃO PARA CARREGAR IMAGEM COM SEGURANÇA ==========
def carregar_imagem_segura(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
            return Image.open(BytesIO(response.content))
    except Exception as e:
        st.warning(f"Erro ao carregar imagem: {e}")
    return None

# ========== CARREGAR DADOS ==========
def carregar_dados():
    try:
        escopos = ["https://www.googleapis.com/auth/spreadsheets"]
        credenciais = Credentials.from_service_account_info(
            st.secrets["GCP_SERVICE_ACCOUNT"], scopes=escopos
        )
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open_by_url(st.secrets["PLANILHA_URL"])
        aba = planilha.worksheet("clientes_status")
        dados = aba.get_all_records()
        return pd.DataFrame(dados), aba
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), None

# ========== EXIBIR GALERIA ==========
df, aba_clientes = carregar_dados()

if df.empty or "Foto" not in df.columns:
    st.info("Nenhuma imagem encontrada.")
else:
    nomes = df["Cliente"].dropna().unique()
    nome_filtrado = st.selectbox("Filtrar por cliente:", ["Todos"] + sorted(nomes.tolist()))

    if nome_filtrado != "Todos":
        df = df[df["Cliente"] == nome_filtrado]

    fotos_validas = df.dropna(subset=["Foto"])

    if fotos_validas.empty:
        st.warning("Nenhuma imagem disponível para esse filtro.")
    else:
        fotos_validas["Cliente"] = fotos_validas["Cliente"].astype(str)
        fotos_validas = fotos_validas.sort_values(by="Cliente", key=lambda x: x.str.lower())
        grupos = fotos_validas.groupby(fotos_validas["Cliente"].str[0].str.upper())
        letras_disponiveis = sorted(grupos.groups.keys())

        st.markdown("### 🔡 Navegação por letra")
        st.markdown(" | ".join([f"[{letra}](#{letra.lower()})" for letra in letras_disponiveis]), unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🟢 Expandir tudo"):
                st.session_state["expand_all"] = True
        with col2:
            if st.button("🔴 Recolher tudo"):
                st.session_state["expand_all"] = False

        for letra, grupo in grupos:
            total = len(grupo)
            expanded_default = st.session_state.get("expand_all", True)

            st.markdown(f'<a name="{letra.lower()}"></a>', unsafe_allow_html=True)
            with st.expander(f"🔤 {letra} ({total} cliente{'s' if total > 1 else ''})", expanded=expanded_default):
                cols = st.columns(3)

                for i, (idx, row) in enumerate(grupo.iterrows()):
                    with cols[i % 3]:
                        # Carregar imagem segura
                        img = carregar_imagem_segura(row["Foto"])
                        if not isinstance(img, Image.Image):
                            img = carregar_imagem_segura(LOGO_PADRAO)

                        if isinstance(img, Image.Image):
                            try:
                                st.image(img, caption=row["Cliente"], use_container_width=True)
                            except Exception as e:
                                st.error(f"Erro ao exibir imagem de {row['Cliente']}: {e}")
                                st.write("Tipo de img:", type(img))
                        else:
                            st.warning(f"⚠️ Imagem inválida para {row['Cliente']}")
                            st.write("Tipo inválido:", type(img))

                        with st.expander(f"🛠 Ações para {row['Cliente']}"):
                            if st.button(f"❌ Excluir imagem", key=f"excluir_{idx}"):
                                try:
                                    cell = aba_clientes.find(str(row["Cliente"]))
                                    if cell:
                                        col_foto = df.columns.get_loc("Foto") + 1
                                        aba_clientes.update_cell(cell.row, col_foto, "")
                                        st.success("✅ Imagem removida da planilha.")

                                    if "res.cloudinary.com" in row["Foto"]:
                                        nome_img = row["Foto"].split("/")[-1].split(".")[0]
                                        public_id = f"Fotos clientes/{nome_img}"
                                        cloudinary.uploader.destroy(public_id)
                                        st.success("✅ Imagem deletada do Cloudinary com sucesso.")

                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao deletar imagem: {e}")

                            nova_foto = st.text_input("🔄 Substituir link da imagem", key=f"edit_{idx}")
                            if nova_foto:
                                try:
                                    cell = aba_clientes.find(str(row["Cliente"]))
                                    if cell:
                                        col_foto = df.columns.get_loc("Foto") + 1
                                        aba_clientes.update_cell(cell.row, col_foto, nova_foto)
                                        st.success("✅ Imagem substituída com sucesso.")
                                        st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao substituir imagem: {e}")
