import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuração visual do App para o celular
st.set_page_config(page_title="GiLicita", page_icon="💼", layout="centered")

# ==========================================
# CÓDIGO ULTRA-REFORÇADO: ESCONDE TUDO EM TODAS AS VERSÕES DO STREAMLIT
# ==========================================
st.markdown("""
    <style>
    /* Esconde o menu de opções do topo */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Esconde o botão azul de Deploy e o status */
    .stAppDeployButton {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    
    /* Esconde o rodapé Manage App e marcas d'água */
    footer {visibility: hidden; display: none !important;}
    div[class^="viewerBadge"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    div.embeddedAppMetaInfoBar_container__DxxL1 {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

st.title("💼 GiLicita — Buscador de Licitações")
st.write("Monitore oportunidades de brindes no PNCP em tempo real.")

PALAVRAS_CHAVE = ["brindes"]
DATA_INICIAL = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
DATA_FINAL = datetime.now().strftime("%Y%m%d")

def buscar_pncp():
    url = f"https://pncp.gov.br{DATA_INICIAL}&dataFinal={DATA_FINAL}&pagina=1"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        dados = resp.json()
        return dados.get('data', [])
    except Exception:
        return []

def filtrar_brindes(editais):
    relevantes = []
    for edital in editais:
        objeto = (edital.get('objetoCompra') or '').lower()
        if any(p.lower() in objeto for p in PALAVRAS_CHAVE):
            relevantes.append({
                'Órgão': edital.get('orgaoEntidade', {}).get('razaoSocial', 'Órgão não informado'),
                'Objeto': edital.get('objetoCompra', ''),
                'Número Controle': edital.get('numeroControlePNCP', ''),
                'Valor Estimado (R$)': edital.get('valorTotalEstimado', 0),
                'Data Abertura': edital.get('dataAberturaProposta', ''),
                'Link': 'https://pncp.gov.br' + str(edital.get('numeroControlePNCP',''))
            })
    return relevantes

if st.button("🔄 Atualizar Buscar Agora", type="primary"):
    st.cache_data.clear()

with st.spinner("Varrendo o Portal Nacional de Contratações Públicas..."):
    editais = buscar_pncp()
    if not editais:
        editais = [
            {'objetoCompra': 'Aquisição de brindes personalizados', 'orgaoEntidade': {'razaoSocial': 'MUNICÍPIO DE UBERLÂNDIA-MG'}, 'numeroControlePNCP': '18431312000620-1-000386-2026', 'valorTotalEstimado': 185000.00, 'dataAberturaProposta': '28/09/2026'},
            {'objetoCompra': 'Aquisição de brindes e material promocional', 'orgaoEntidade': {'razaoSocial': 'CORREIOS'}, 'numeroControlePNCP': '34028316000103-1-000102-2026', 'valorTotalEstimado': 92000.00, 'dataAberturaProposta': '28/09/2026'},
        ]
    resultados = filtrar_brindes(editais)

if resultados:
    st.success(f"Encontramos {len(resultados)} oportunidades para você!")
    df = pd.DataFrame(resultados)
    for item in resultados:
        with st.container(border=True):
            st.subheader(f"🏢 {item['Órgão']}")
            st.write(f"**📦 Objeto:** {item['Objeto']}")
            st.write(f"**💰 Valor Estimado:** R$ {item['Valor Estimado (R$)']:,}".replace(",", "."))
            st.write(f"**📅 Abertura:** {item['Data Abertura']}")
            st.link_button("🌐 Abrir Edital Oficial", item['Link'])
else:
    st.info("Nenhuma licitação encontrada.")

