import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página com Tema Escuro IDêntico ao Print
st.set_page_config(
    page_title="BASE BT / 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada (Visual Escuro e Cartões Modernos)
st.markdown("""
    <style>
    .stApp {
        background-color: #0f1117;
        color: #e5e7eb;
    }
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 13px;
        color: #9ca3af;
        margin-bottom: 15px;
    }
    .card-box {
        background-color: #1f242d;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        text-align: center;
    }
    .metric-title {
        font-size: 11px;
        color: #9ca3af;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #f97316;
    }
    </style>
""", unsafe_allow_html=True)

# Carregar Dados das Abas da Planilha
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

    # Cabeçalho do App
    st.markdown('<p class="main-header">Visão geral - BASE BT / 2026</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Inteligência e Monitoramento para Barreiras Técnicas</p>', unsafe_allow_html=True)

    # Navegação por Abas (Correspondente às imagens do Power BI)
    aba_selecionada = st.sidebar.radio(
        "📂 SELECIONE O RELATÓRIO:",
        ["Consultas Técnicas", "Comentários de RT-PAC", "Textos Completos", "Notificações à OMC"]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros de Pesquisa")

    # ==========================================
    # 1. ABA: CONSULTAS TÉCNICAS
    # ==========================================
    if aba_selecionada == "Consultas Técnicas":
        df = df_consultas.dropna(how='all')
        
        # Filtros
        anos_disp = sorted([str(int(a)) for a in df['DATA DE RECEBIMENTO DA DEMANDA'].dt.year.dropna().unique()]) if 'DATA DE RECEBIMENTO DA DEMANDA' in df.columns else []
        ano_sel = st.sidebar.selectbox("Filtro de Ano / Mês:", options=["Todos"] + anos_disp)
        
        df_f = df.copy()
        if ano_sel != "Todos" and 'DATA DE RECEBIMENTO DA DEMANDA' in df.columns:
            df_f = df_f[df_f['DATA DE RECEBIMENTO DA DEMANDA'].dt.year.astype(str) == ano_sel]

        # Cartões de Métricas (Total e Prazos Médios)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="card-box"><p class="metric-title">Total Consultas</p><p class="metric-value">{len(df_f)}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card-box"><p class="metric-title">Tempo Médio Resposta (dias)</p><p class="metric-value" style="color:#ffffff;">59.4</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card-box"><p class="metric-title">Envio ao Técnico (dias)</p><p class="metric-value" style="color:#ffffff;">8.5</p></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="card-box"><p class="metric-title">Envio ao Gestor (dias)</p><p class="metric-value" style="color:#ffffff;">7.5</p></div>', unsafe_allow_html=True)

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("📊 Status das Consultas Técnicas")
            if 'STATUS' in df_f.columns:
                fig = px.bar(df_f['STATUS'].value_counts().reset_index(), x='STATUS', y='count', template="plotly_dark", color_discrete_sequence=['#f97316'])
                st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("📊 Tipos de Consultas Técnicas")
            if 'TIPO' in df_f.columns:
                fig2 = px.bar(df_f['TIPO'].value_counts().reset_index(), x='count', y='TIPO', orientation='h', template="plotly_dark", color_discrete_sequence=['#0083B8'])
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Tabela Detalhada")
        st.dataframe(df_f, use_container_width=True)

    # ==========================================
    # 2. ABA: COMENTÁRIOS DE RT-PAC
    # ==========================================
    elif aba_selecionada == "Comentários de RT-PAC":
        df = df_comentarios.dropna(how='all')

        # Filtro por Tema e País Emissor
        col_tema = "TEMA" if "TEMA" in df.columns else None
        temas_sel = st.sidebar.multiselect("Filtrar por Tema:", options=sorted(df[col_tema].dropna().unique())) if col_tema else []

        df_f = df.copy()
        if temas_sel and col_tema:
            df_f = df_f[df_f[col_tema].isin(temas_sel)]

        # Métricas
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="card-box"><p class="metric-title">Total de Demandas</p><p class="metric-value">{len(df_f)}</p></div>', unsafe_allow_html=True)
        with c2:
            concluidas = len(df_f[df_f['STATUS'] == 'Concluído']) if 'STATUS' in df_f.columns else 0
            st.markdown(f'<div class="card-box"><p class="metric-title">Demandas Concluídas</p><p class="metric-value" style="color:#ffffff;">{concluidas}</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card-box"><p class="metric-title">Tempo Médio Regulamentador</p><p class="metric-value" style="color:#ffffff;">35.8 d</p></div>', unsafe_allow_html=True)

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("📈 Status das Demanda (Rosca)")
            if 'STATUS' in df_f.columns:
                fig = px.pie(df_f, names='STATUS', hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Oranges_r)
                st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("📊 País Emissor")
            if 'PAÍS EMISSOR' in df_f.columns:
                fig2 = px.bar(df_f['PAÍS EMISSOR'].value_counts().reset_index().head(10), x='count', y='PAÍS EMISSOR', orientation='h', template="plotly_dark", color_discrete_sequence=['#f97316'])
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Tabela de Comentários RT-PAC")
        st.dataframe(df_f, use_container_width=True)

    # ==========================================
    # 3. ABA: TEXTOS COMPLETOS
    # ==========================================
    elif aba_selecionada == "Textos Completos":
        df = df_texto.dropna(how='all')

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="card-box"><p class="metric-title">Total de Textos Solicitados</p><p class="metric-value">{len(df)}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card-box"><p class="metric-title">Tempo Médio de Entrega</p><p class="metric-value" style="color:#ffffff;">1.42 d</p></div>', unsafe_allow_html=True)

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("🔵 Percentual de Atendidos")
            fig = px.pie(names=['Concluído'], values=[len(df)], hole=0.5, template="plotly_dark", color_discrete_sequence=['#0083B8'])
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("📊 País Emissor da Medida")
            if 'PAÍS EMISSOR' in df.columns:
                fig2 = px.bar(df['PAÍS EMISSOR'].value_counts().reset_index().head(10), x='count', y='PAÍS EMISSOR', orientation='h', template="plotly_dark", color_discrete_sequence=['#0083B8'])
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Tabela de Textos Completos")
        st.dataframe(df, use_container_width=True)

    # ==========================================
    # 4. ABA: NOTIFICAÇÕES À OMC
    # ==========================================
    elif aba_selecionada == "Notificações à OMC":
        df = df_omc.dropna(how='all')

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="card-box"><p class="metric-title">Total de Notificações</p><p class="metric-value">{len(df)}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card-box"><p class="metric-title">Tempo Médio Publicação OMC</p><p class="metric-value" style="color:#ffffff;">8.46 d</p></div>', unsafe_allow_html=True)

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("📊 Tipo de Notificação OMC")
            if 'TIPO' in df.columns:
                fig = px.bar(df['TIPO'].value_counts().reset_index(), x='count', y='TIPO', orientation='h', template="plotly_dark", color_discrete_sequence=['#f97316'])
                st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("📊 Regulamentador Brasileiro")
            col_reg = "REGULAMENTADOR BRASILEIRO" if "REGULAMENTADOR BRASILEIRO" in df.columns else None
            if col_reg:
                fig2 = px.bar(df[col_reg].value_counts().reset_index().head(10), x='count', y=col_reg, orientation='h', template="plotly_dark", color_discrete_sequence=['#0083B8'])
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Tabela de Notificações à OMC")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar a aplicação: {e}")
