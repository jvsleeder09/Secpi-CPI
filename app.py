import streamlit as st
import fitz
import re
import os
import time
from PIL import Image
import base64
from io import BytesIO
import importlib
import pandas as pd
import sys

# =====================================
# FUNÇÃO: CONVERTER IMAGEM EM BASE64
# =====================================
def image_to_base64(image):
    """Converte uma imagem PIL em uma string base64 para uso em HTML."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(
    page_title="SECPI | CPI",
    page_icon="🖥️",
    layout="wide"
)

# =====================================
# LOGO DO EXTRACTORGHOST E LOGOS DO PROGRAMA (LOCAIS)
# =====================================
try:
    ghost_logo = Image.open("ghost_logo.png")
    cpi_logo_sidebar = Image.open("cpi_logo.png")
    mincom_logo = Image.open("ministerio_comunicacoes_logo.png")
    cpi_logo_top = Image.open("computadores_para_inclusao_logo.png")
    marica_logo = Image.open("secpi_logo.png")
except FileNotFoundError:
    st.error("Erro: Verifique se os arquivos de logo ('ghost_logo.png', 'cpi_logo.png', 'ministerio_comunicacoes_logo.png', 'computadores_para_inclusao_logo.png' e 'secpi_logo.png') estão na mesma pasta do 'app.py'")
    st.stop()

# =====================================
# GERENCIAMENTO DE TEMA COM SESSION STATE
# =====================================
# ADAPTAÇÃO: Código para gerenciar o tema e permitir a alternância
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

current_theme = st.session_state.theme

def switch_theme():
    """Alterna entre os temas claro e escuro."""
    if st.session_state.theme == "dark":
        st.session_state.theme = "light"
    else:
        st.session_state.theme = "dark"

# =====================================
# CSS CUSTOMIZADO
# =====================================
st.markdown(f"""
<style>
    /* Variáveis CSS para ambos os temas */
    :root {{
        --bg-primary: {'#0E1117' if current_theme == 'dark' else '#FFFFFF'};
        --bg-secondary: {'#1E1E1E' if current_theme == 'dark' else '#F0F2F6'};
        --text-primary: {'#F0F2F5' if current_theme == 'dark' else '#262730'};
        --text-secondary: {'#CCCCCC' if current_theme == 'dark' else '#666666'};
        --accent-color: {'#2196F3' if current_theme == 'dark' else '#0068C9'};
        --border-color: {'rgba(255, 255, 255, 0.1)' if current_theme == 'dark' else 'rgba(0, 0, 0, 0.1)'};
        --glass-bg: {'rgba(255, 255, 255, 0.05)' if current_theme == 'dark' else 'rgba(255, 255, 255, 0.8)'};
        --glass-border: {'rgba(255, 255, 255, 0.15)' if current_theme == 'dark' else 'rgba(255, 255, 255, 0.3)'};
        --button-bg: {'rgba(33, 150, 243, 0.2)' if current_theme == 'dark' else 'rgba(0, 104, 201, 0.1)'};
        --button-hover: {'rgba(33, 150, 243, 0.4)' if current_theme == 'dark' else 'rgba(0, 104, 201, 0.2)'};
    }}

    /* ADAPTAÇÃO: Fundo principal com o gradiente que você quer */
    [data-testid="stAppViewContainer"] {{
        background: {'linear-gradient(135deg, #5C000C 0%, #00001A 50%, #002980 100%)' if current_theme == 'dark' else 'linear-gradient(135deg, #FFE5E9 0%, #F0F8FF 50%, #E6F7FF 100%)'} !important;
        color: var(--text-primary) !important;
        font-family: "Segoe UI", "Inter", sans-serif !important;
    }}

    /* ADAPTAÇÃO: Barra lateral com o mesmo gradiente */
    [data-testid="stSidebar"] {{
        background: {'linear-gradient(135deg, #5C000C 0%, #00001A 50%, #002980 100%)' if current_theme == 'dark' else 'linear-gradient(135deg, #FFE5E9 0%, #F0F8FF 50%, #E6F7FF 100%)'} !important;
        border-right: 1px solid var(--border-color) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        border-radius: 0 16px 16px 0 !important;
        padding: 2rem 1.5rem !important;
        min-width: 300px !important;
    }}

    /* CORREÇÃO: Texto dos elementos de formulário */
    .stSelectbox, .stRadio, .stCheckbox, .stFileUploader {{
        color: var(--text-primary) !important;
    }}

    .stSelectbox label, .stRadio label, .stCheckbox label, .stFileUploader label {{
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    /* CORREÇÃO: Radio buttons visíveis */
    .stRadio > div {{
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: var(--text-primary) !important;
    }}

    .stRadio label {{
        color: var(--text-primary) !important;
    }}

    /* CORREÇÃO: Checkbox visível */
    .stCheckbox > div {{
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: var(--text-primary) !important;
    }}

    /* CORREÇÃO: File uploader visível */
    .stFileUploader > div {{
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: var(--text-primary) !important;
    }}

    /* CORREÇÃO URGENTE: Garantir que o texto do selectbox seja visível */
    div[data-baseweb="select"] > div {{
        color: var(--text-primary) !important;
        background: var(--bg-primary) !important;
    }}

    div[data-baseweb="select"] input {{
        color: var(--text-primary) !important;
    }}

    /* Melhorar legibilidade da sidebar */
    .sidebar-content {{
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }}

    .sidebar-content h3 {{
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent-color) !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
        font-size: 1.2rem !important;
    }}

    .sidebar-content p, .sidebar-content ul, .sidebar-content li {{
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        margin-bottom: 0.8rem !important;
    }}

    .sidebar-content ul {{
        padding-left: 1.5rem !important;
    }}

    .sidebar-content li {{
        margin-bottom: 0.5rem !important;
    }}

    /* CORREÇÃO: Botões maiores e melhor alinhados */
    .stButton > button {{
        background: var(--button-bg) !important;
        border: 1px solid var(--accent-color) !important;
        color: var(--text-primary) !important;
        font-family: "Segoe UI", sans-serif !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s !important;
        width: 100% !important;
        min-height: 60px !important;
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        margin: 0.5rem 0 !important;
    }}

    .stButton > button:hover {{
        background: var(--button-hover) !important;
        border-color: var(--accent-color) !important;
        box-shadow: 0 6px 8px rgba(0,0,0,0.3) !important;
        transform: translateY(-2px);
    }}

    /* CORREÇÃO: Organização dos botões em colunas */
    .stButton {{
        width: 100% !important;
        margin: 1rem 0 !important;
    }}

    /* Containers de conteúdo */
    .glass-container {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    .glass-container p {{
        color: var(--text-primary) !important;
        text-align: center;
        font-family: "Segoe UI", sans-serif !important;
    }}

    .widget-label {{
        font-size: 1.2rem !important;
        color: var(--text-primary) !important;
        font-family: "Segoe UI", sans-serif !important;
        margin-bottom: 1rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 0 !important;
    }}

    /* Tabela de resultados (original) */
    .glass-table-container {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 2rem auto !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        max-width: 1400px;
    }}

    .glass-table-header {{
        background: {'rgba(255, 255, 255, 0.1)' if current_theme == 'dark' else 'rgba(0, 0, 0, 0.05)'} !important;
        border-radius: 8px;
        padding: 15px 10px;
        display: flex;
        font-weight: 600;
        color: var(--text-primary);
        font-family: "Segoe UI", sans-serif;
        font-size: 0.95rem;
    }}

    .glass-table-row {{
        display: flex;
        border-bottom: 1px solid var(--border-color);
        padding: 12px 10px;
        transition: background-color 0.2s ease;
    }}

    .glass-table-row:hover {{
        background-color: {'rgba(255, 255, 255, 0.05)' if current_theme == 'dark' else 'rgba(0, 0, 0, 0.02)'};
    }}

    .glass-table-cell {{
        flex: 1;
        padding: 0 5px;
        font-size: 0.9rem;
        color: var(--text-primary);
        word-wrap: break-word;
    }}

    /* Layout responsivo para colunas */
    @media (max-width: 768px) {{
        .stButton > button {{
            font-size: 1rem !important;
            padding: 0.8rem 1.5rem !important;
            min-height: 55px !important;
        }}
        
        [data-testid="stSidebar"] {{
            min-width: 250px !important;
            padding: 1.5rem 1rem !important;
        }}
        
        .sidebar-content h3 {{
            font-size: 1.1rem !important;
        }}
        
        .sidebar-content p, .sidebar-content ul, .sidebar-content li {{
            font-size: 0.9rem !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# =====================================
# TÍTULO E SUBTÍTULO
# =====================================
st.markdown(f"""
<div style='text-align: center; margin-top: 1.5rem; margin-bottom: 0;'>
    <img src='data:image/png;base64,{image_to_base64(ghost_logo)}' width='100'/>
    <h1 style='color: var(--text-primary); font-family: "Segoe UI", sans-serif; font-weight: 600; text-shadow: none; margin-bottom: 0.2rem;'>
        SECPI
    </h1>
    
</div>
<div class='glass-container' style='margin-top: 1rem; padding: 1rem;'>
    <h3 style='color: var(--text-primary); font-family: "Segoe UI", sans-serif; font-weight: 300; margin: 0; text-align: center;'>
        Sistema de Extração de Certificados do Programa Computadores para Inclusão
    </h3>
</div>
""", unsafe_allow_html=True)

# =====================================
# BARRA LATERAL (SIDEBAR)
# =====================================
with st.sidebar:
    # ADAPTAÇÃO: Botão para alternar o tema
    st.button(f"{'☀️' if current_theme == 'dark' else '🌙'} Alternar Tema", on_click=switch_theme, key='switch_theme_button', use_container_width=True)

    st.markdown("""
    <div class="sidebar-content">
        <h3>ℹ️ SOBRE O PROGRAMA</h3>
        <p>
        O Programa Computadores para Inclusão é uma ação do Governo Federal que promove inclusão digital através dos Centros de Recondicionamento de Computadores (CRCs):
        </p>
        <ul>
            <li>Recondicionamento de equipamentos</li>
            <li>Capacitação em tecnologia</li>
            <li>Descarte ecológico de eletroeletrônicos</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-content">
        <h3>⚙️ FUNCIONALIDADE</h3>
        <ul>
            <li>Extração automatizada de dados dos certificados</li>
            <li>Redução de 92% no tempo de processamento</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-content">
        <h3>✅ REQUISITOS</h3>
        <ul>
            <li>PDF com texto editável</li>
            <li>Nome completo visível</li>
            <li>Carga horária especificada</li>
            <li>Data de conclusão visível</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-content" style="margin-top: 3rem; text-align: center;">
        <hr style="border-color: var(--accent-color); margin-bottom: 1rem;">
        <p style="font-size: 0.9rem; color: var(--text-primary);">
        <strong>DESENVOLVIDO POR:</strong><br>
        Victor Arsego Lêla (CPI Tech)
        </p>
        <img src='data:image/png;base64,{image_to_base64(cpi_logo_sidebar)}' width='200' style='margin-top: 2rem;'/>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# ÁREA PRINCIPAL DO APLICATIVO
# =====================================
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: var(--text-primary);'>SISTEMA PRONTO PARA EXTRAÇÃO DE CERTIFICADOS</p>", unsafe_allow_html=True)

# =====================================
# UPLOAD E PROCESSAMENTO DE ARQUIVOS (FIXED)
# =====================================

opcoes_visiveis = ["Selecione um CRC...", "CRC PROTÓTIPO", "CRC NCC Belém", "CRC INAC", "CRC IEC", "CRC FUNPAPI", "CRC IA", "CRC IDC", "CRC IFS", "CRC IGH", "CRC PROGRAMANDO", "CRC UNIFAP"]

mapa_crc = {
    "CRC PROTÓTIPO": "cod_crc.crc_prototipo",
    "CRC NCC Belém": "cod_crc.crc_belem",
    "CRC INAC": "cod_crc.crc_inac",
    "CRC IEC": "cod_crc.crc_iec",
    "CRC FUNPAPI": "cod_crc.crc_funpapi",
    "CRC IA": "cod_crc.crc_ia",
    "CRC IDC": "cod_crc.crc_idc",
    "CRC IFS": "cod_crc.crc_ifs",
    "CRC IGH": "cod_crc.crc_igh",
    "CRC PROGRAMANDO": "cod_crc.crc_programando",
    "CRC UNIFAP": "cod_crc.crc_unifap",
}

st.markdown("<p class='widget-label'>Selecione o CRC que deseja realizar a extração:</p>", unsafe_allow_html=True)
crc_opcao = st.selectbox("", opcoes_visiveis, key="crc_select")

st.markdown("<p class='widget-label'>Selecione o tipo de PDF:</p>", unsafe_allow_html=True)
tipo_pdf = st.radio(
    "",
    ["Único PDF (somente frente)", "Único PDF (frente e verso)", "Vários PDFs (somente frente)", "Vários PDFs (frente e verso)"],
    key="tipo_pdf_radio"
)
    
st.markdown("<p class='widget-label'>O nome do arquivo é o nome do aluno?</p>", unsafe_allow_html=True)
nome_do_arquivo_e_nome_do_aluno = st.checkbox("Sim, o nome do arquivo é o nome do aluno", key="nome_no_arquivo_checkbox")

st.markdown("<p class='widget-label'>Envie um ou mais certificados:</p>", unsafe_allow_html=True)
arquivos = st.file_uploader(
    "Selecione os arquivos PDF",
    type="pdf",
    accept_multiple_files=True,
    key="pdf_uploader",
    label_visibility="collapsed"
)

st.write("")

# Layout melhorado para os botões com maior espaçamento
col1, col2, col3 = st.columns([1, 0.2, 1])

with col1:
    extract_button = st.button("📄 EXTRAIR DADOS", key="extract_button", use_container_width=True)

with col3:
    clear_button = st.button("🗑️ LIMPAR TUDO", key="clear_button", use_container_width=True)

st.write("")

if extract_button:
    if crc_opcao == "Selecione um CRC...":
        st.warning("⚠️ Por favor, selecione um CRC válido antes de extrair.")
    elif not arquivos:
        st.warning("⚠️ Por favor, envie um ou mais arquivos antes de extrair.")
    else:
        todos_dados = []
        extraido_com_sucesso = False
            
        with st.spinner('🔍 Extraindo dados... aguarde um momento...'):
            try:
                modulo_crc = importlib.import_module(mapa_crc[crc_opcao])
                    
                for arquivo in arquivos:
                    with open("temp.pdf", "wb") as f:
                        f.write(arquivo.getbuffer())

                    try:
                        dados_por_pagina = modulo_crc.extrair_dados(
                            "temp.pdf",
                            tipo_pdf,
                            nome_do_arquivo_e_nome_do_aluno,
                            arquivo.name
                        )

                        for i in range(len(dados_por_pagina["Nome"])):
                            dados = {
                                "Arquivo": arquivo.name,
                                "CRC": crc_opcao,
                                "Nome": dados_por_pagina["Nome"][i],
                                "Curso": dados_por_pagina["Curso"][i],
                                "Carga Horária": dados_por_pagina["Carga Horária"][i],
                                "Data": dados_por_pagina["Data"][i]
                            }
                            todos_dados.append(dados)
                            
                        extraido_com_sucesso = True

                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro ao processar o arquivo '{arquivo.name}': {e}")
                    finally:
                        if os.path.exists("temp.pdf"):
                            os.remove("temp.pdf")
                
            except KeyError:
                st.error("❌ Erro: A opção de CRC selecionada não é válida. Por favor, escolha uma opção da lista.")
            except ImportError:
                st.error(f"❌ Erro: O módulo de extração para '{crc_opcao}' não foi encontrado. Certifique-se de que os arquivos de extração (ex: crc_belem.py) estão na pasta 'cod_crc'.")
            
        if extraido_com_sucesso and todos_dados:
            df = pd.DataFrame(todos_dados)
            
            # MANTENDO A TABELA CUSTOMIZADA QUE VOCÊ GOSTOU
            st.markdown("""
            <h3>Resultados da Extração</h3>
            <div class="glass-table-header">
                <div style="flex: 2; padding: 0 5px;">📄 Arquivo</div>
                <div style="flex: 1; padding: 0 5px;">🧍 Nome</div>
                <div style="flex: 1; padding: 0 5px;">🎓 Curso</div>
                <div style="flex: 1; padding: 0 5px;">⏱️ Carga Horária</div>
                <div style="flex: 1; padding: 0 5px;">📆 Data</div>
            </div>
            """, unsafe_allow_html=True)
            
            for index, row in df.iterrows():
                st.markdown(f"""
                <div class="glass-table-row">
                    <div class="glass-table-cell" style="flex: 2;">{row['Arquivo']}</div>
                    <div class="glass-table-cell">{row['Nome']}</div>
                    <div class="glass-table-cell">{row['Curso']}</div>
                    <div class="glass-table-cell">{row['Carga Horária']}</div>
                    <div class="glass-table-cell">{row['Data']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            csv_bytes = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
            
            st.download_button(
                label="💾 BAIXAR RESULTADOS EM EXCEL",
                data=csv_bytes,
                file_name="extracao_certificados.csv",
                mime="text/csv",
                key="download_button",
                use_container_width=True
            )
        elif not extraido_com_sucesso:
            st.warning("⚠️ Nenhuma informação extraída. Por favor, verifique os arquivos e tente novamente.")

if clear_button:
    st.session_state.clear()
    st.rerun()

# =====================================
# RODAPÉ
# =====================================
st.markdown(f"""
<div style="display: flex; flex-direction: column; align-items: center; margin-top: 5rem;">
    <div style="color: var(--text-primary); font-size: 0.7rem; letter-spacing: 2px; text-align: center;">
        [ SISTEMA OFICIAL CPI - v2.1 ] © 2025 | TODOS OS DIREITOS RESERVADOS
    </div>
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 1.5rem;">
        <img src='data:image/png;base64,{image_to_base64(mincom_logo)}' alt="Logo do Ministério das Comunicações" height='60'/>
        <img src='data:image/png;base64,{image_to_base64(cpi_logo_top)}' alt="Logo do Computadores para Inclusão" height='60'/>
        <img src='data:image/png;base64,{image_to_base64(marica_logo)}' alt="Logo da SECPI" height='60'/>
    </div>
</div>
""", unsafe_allow_html=True)
