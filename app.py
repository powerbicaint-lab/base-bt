import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página e tema escuro moderno
st.set_page_config(
    page_title="BASE BT / 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para imitar a interface escura elegante do print
st.markdown("""
    <style>
    .stApp {
        background-color: #0f1117;
        color: #e5e7eb;
    }
    .main-header {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 20px;
    }
    .card-box {
        background-color: #1f242d;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 12px;
        color: #9ca3af;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #f97316;
    }
    </style>
""", unsafe_allow_html=True)

# Carregar dados com cache
@st.cache_data
def carregar_dados():
    caminho = "BASE DATA BT (1).xlsx"
    xls = pd.ExcelFile(caminho)
    
    df_comentarios = pd.read_excel(xls, sheet_name="Comentários RT-PAC")
    df_consultas = pd.read_excel(xls, sheet_name="Consultas")
    df_texto = pd.read_excel(xls, sheet_name="TextoCompleto")
    df_omc = pd.read_excel(xls, sheet_name="Notificações a OMC")
    
    return df_comentarios, df_consultas, df_texto, df_omc

try:
    df_comentarios, df_consultas, df_texto, df_omc = carregar_dados()

    # Cabeçalho Principal IDêntico ao Print
    st.markdown('<p class="main-header">Visão geral</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Inteligência para barreiras técnicas • BASE BT / 2026</p>', unsafe_allow_html=True)

    # Menu lateral de navegação entre as abas
    aba_selecionada = st.sidebar.radio(
        "📂 SELECIONE A BASE:",
        ["Comentários RT-PAC", "Consultas", "Texto Completo", "Notificações a OMC"]
    )

    # Selecionar o dataframe correto
    if aba_selecionada == "Comentários RT-PAC":
        df = df_comentarios
    elif aba_selecionada == "Consultas":
        df = df_consultas
    elif aba_selecionada == "Texto Completo":
        df = df_texto
    else:
        df = df_omc

    df = df.dropna(how='all')

    # --- FILTROS DE PESQUISA NA BARRA LATERAL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros de Pesquisa")

    # Filtro de País Emissor / Demandante
    col_pais = "PAÍS EMISSOR" if "PAÍS EMISSOR" in df.columns else ("PAÍS DEMANDANTE" if "PAÍS DEMANDANTE" in df.columns else None)
    paises_sel = []
    if col_pais:
        paises = sorted([str(p) for p in df[col_pais].dropna().unique()])
        paises_sel = st.sidebar.multiselect("País:", options=paises)

    # Filtro de Ano
    col_ano = "ANO" if "ANO" in df.columns else None
    anos_sel = []
    if col_ano:
        anos = sorted([str(int(a)) for a in df[col_ano].dropna().unique() if pd.notna(a)])
        anos_sel = st.sidebar.multiselect("Ano:", options=anos)

    # Filtro de Tema (Específico para RT-PAC / Comentários ou geral se houver)
    col_tema = "TEMA" if "TEMA" in df.columns else None
    temas_sel = []
    if aba_selecionada == "Comentários RT-PAC" and col_tema:
        temas = sorted([str(t) for t in df[col_tema].dropna().unique()])
        temas_sel = st.sidebar.multiselect("Tema (RT-PAC):", options=temas)
    elif col_tema:
        temas = sorted([str(t) for t in df[col_tema].dropna().unique()])
        temas_sel = st.sidebar.multiselect("Tema:", options=temas)

    # Aplicar Filtros
    df_filtrado = df.copy()

    if paises_sel and col_pais:
        df_filtrado = df_filtrado[df_filtrado[col_pais].astype(str).isin(paises_sel)]
    if anos_sel and col_ano:
        df_filtrado = df_filtrado[df_filtrado[col_ano].astype(str).isin(anos_sel)]
    if temas_sel and col_tema:
        df_filtrado = df_filtrado[df_filtrado[col_tema].astype(str).isin(temas_sel)]

    # --- CARDS DE MÉTRICAS ESTILO APP ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="card-box" style="border: 1px solid #f97316;">
                <p class="metric-title">Registros Filtrados</p>
                <p class="metric-value">{len(df_filtrado)}</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        num_paises = df_filtrado[col_pais].nunique() if col_pais else 0
        st.markdown(f"""
            <div class="card-box">
                <p class="metric-title">Países</p>
                <p class="metric-value" style="color: #ffffff;">{num_paises}</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        num_temas = df_filtrado[col_tema].nunique() if col_tema else 0
        st.markdown(f"""
            <div class="card-box">
                <p class="metric-title">Temas</p>
                <p class="metric-value" style="color: #ffffff;">{num_temas}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- GRÁFICOS E VISUALIZAÇÕES ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📊 Volume por País")
        if not df_filtrado.empty and col_pais:
            df_pais_counts = df_filtrado[col_pais].value_counts().reset_index().head(10)
            df_pais_counts.columns = [col_pais, 'count']
            
            fig_pais = px.bar(
                df_pais_counts,
                x='count',
                y=col_pais,
                orientation='h',
                template="plotly_dark",
                color_discrete_sequence=['#f97316']
            )
            fig_pais.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig_pais, use_container_width=True)
        else:
            st.info("Sem dados para exibir.")

    with g2:
        st.subheader("📈 Distribuição por Tema / Status")
        col_grafico = col_tema if col_tema else ("STATUS" if "STATUS" in df_filtrado.columns else None)
        if not df_filtrado.empty and col_grafico:
            fig_pie = px.pie(
                df_filtrado,
                names=col_grafico,
                hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sem dados para exibir.")

    st.markdown("---")

    # --- TABELA DE DADOS ---
    st.subheader(f"📋 Base Detalhada — {aba_selecionada}")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f-f"Erro ao carregar os dados: {e}")
