import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página e layout
st.set_page_config(
    page_title="Base BT - Pesquisa e Indicadores",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Base BT - Pesquisa & Dashboard Interativo")
st.markdown("Aplicação de consulta interativa desenvolvida com base nos dados do Power BI.")

# Carregar dados com cache para alta performance
@st.cache_data
def carregar_dados():
    caminho = "BASE DATA BT (1).xlsx"
    xls = pd.ExcelFile(caminho)
    
    # Carregando as abas principais da planilha
    df_comentarios = pd.read_excel(xls, sheet_name="Comentários RT-PAC")
    df_consultas = pd.read_excel(xls, sheet_name="Consultas")
    df_texto = pd.read_excel(xls, sheet_name="TextoCompleto")
    
    return df_comentarios, df_consultas, df_texto

try:
    df_comentarios, df_consultas, df_texto = carregar_dados()

    # Menu lateral para escolher a aba/base de dados
    aba_selecionada = st.sidebar.radio(
        "📂 Escolha a Base de Dados:",
        ["Comentários RT-PAC", "Consultas", "Texto Completo"]
    )

    if aba_selecionada == "Comentários RT-PAC":
        df = df_comentarios
    elif aba_selecionada == "Consultas":
        df = df_consultas
    else:
        df = df_texto

    # Limpeza de linhas totalmente vazias
    df = df.dropna(how='all')

    # --- BARRA LATERAL: FILTROS DE PESQUISA ---
    st.sidebar.header("🔍 Filtros de Pesquisa")

    # Filtro de País Emissor
    col_pais = "PAÍS EMISSOR" if "PAÍS EMISSOR" in df.columns else None
    paises_sel = []
    if col_pais:
        paises = sorted([str(p) for p in df[col_pais].dropna().unique()])
        paises_sel = st.sidebar.multiselect("Filtrar por País Emissor:", options=paises)

    # Filtro de Produto
    col_produto = "PRODUTO" if "PRODUTO" in df.columns else None
    produtos_sel = []
    if col_produto:
        produtos = sorted([str(p) for p in df[col_produto].dropna().unique()])
        produtos_sel = st.sidebar.multiselect("Filtrar por Produto:", options=produtos)

    # Filtro por Status
    col_status = "STATUS" if "STATUS" in df.columns else None
    status_sel = []
    if col_status:
        status_opts = sorted([str(s) for s in df[col_status].dropna().unique()])
        status_sel = st.sidebar.multiselect("Filtrar por Status:", options=status_opts)

    # Aplicando os filtros selecionados aos dados
    df_filtrado = df.copy()

    if paises_sel and col_pais:
        df_filtrado = df_filtrado[df_filtrado[col_pais].astype(str).isin(paises_sel)]
    if produtos_sel and col_produto:
        df_filtrado = df_filtrado[df_filtrado[col_produto].astype(str).isin(produtos_sel)]
    if status_sel and col_status:
        df_filtrado = df_filtrado[df_filtrado[col_status].astype(str).isin(status_sel)]

    # --- CARTÕES DE MÉTRICAS NO TOPO ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Registros", len(df_filtrado))
    m2.metric("Países Envolvidos", df_filtrado[col_pais].nunique() if col_pais else 0)
    m3.metric("Produtos Distintos", df_filtrado[col_produto].nunique() if col_produto else 0)
    m4.metric("Status Mapeados", df_filtrado[col_status].nunique() if col_status else 0)

    st.markdown("---")

    # --- GRÁFICOS INTERATIVOS ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📊 Demandas por País Emissor")
        if not df_filtrado.empty and col_pais:
            fig_pais = px.bar(
                df_filtrado[col_pais].value_counts().reset_index(),
                x='count',
                y=col_pais,
                orientation='h',
                title="Volume por País",
                labels={'count': 'Quantidade', col_pais: 'País'},
                color_discrete_sequence=['#0083B8']
            )
            fig_pais.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_pais, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para o gráfico de países.")

    with g2:
        st.subheader("📈 Distribuição por Status")
        if not df_filtrado.empty and col_status:
            fig_status = px.pie(
                df_filtrado,
                names=col_status,
                title="Proporção de Status",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para o gráfico de status.")

    st.markdown("---")

    # --- TABELA DE SAÍDA E PESQUISA ---
    st.subheader("📋 Tabela de Dados Detalhada")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar a base de dados: {e}")
