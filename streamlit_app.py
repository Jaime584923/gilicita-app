"""
GiLicita - Agente REAL - Busca Brasil todo
Versão melhorada - 8 palavras-chave
RODE NO SEU PC: python gilicita_agente_MELHORADO.py
"""

import requests
import csv
from datetime import datetime, timedelta
import time

PALAVRAS_CHAVE = ["brinde", "caneca", "squeeze", "chaveiro", "copo", "camiseta", "kit", "agenda"]
# Busca últimos 60 dias para pegar mais resultados
DATA_INICIAL = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
DATA_FINAL = datetime.now().strftime("%Y%m%d")

def buscar_pncp_real():
    print(f"[GiLicita] 🔍 Varrendo {DATA_INICIAL} a {DATA_FINAL} - Palavras: {PALAVRAS_CHAVE}")
    todos = []
    
    # Busca 3 páginas do PNCP (cada página tem 100 editais)
    for pagina in range(1, 4):
        url = f"https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={DATA_INICIAL}&dataFinal={DATA_FINAL}&pagina={pagina}"
        print(f"[GiLicita] Página {pagina}: {url}")
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            editais = dados.get('data', [])
            print(f"  -> {len(editais)} editais")
            if not editais:
                break
            todos.extend(editais)
            time.sleep(1)  # Não sobrecarregar API
        except Exception as e:
            print(f"  Erro: {e}")
            break
    
    print(f"[GiLicita] Total bruto: {len(todos)} editais")
    
    relevantes = []
    for edital in todos:
        objeto = (edital.get('objetoCompra') or '').lower()
        for palavra in PALAVRAS_CHAVE:
            if palavra.lower() in objeto:
                relevantes.append({
                    'orgao': edital.get('orgaoEntidade', {}).get('razaoSocial', 'Órgão não informado'),
                    'objeto': edital.get('objetoCompra', ''),
                    'valor': edital.get('valorTotalEstimado', 0),
                    'abertura': edital.get('dataAberturaProposta', edital.get('dataPublicacaoPncp','')),
                    'link': f"https://pncp.gov.br/app/editais/{edital.get('numeroControlePNCP','')}",
                    'palavra': palavra,
                    'uf': edital.get('unidadeOrgao',{}).get('ufSigla','') or edital.get('orgaoEntidade',{}).get('ufSigla','')
                })
                break
    
    print(f"[GiLicita] ✅ {len(relevantes)} licitações REAIS de brindes!")
    return relevantes

def gerar_tudo(relevantes):
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    # CSV
    nome_csv = f'gilicita_brasil_{hoje}.csv'
    with open(nome_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['orgao','objeto','valor','abertura','link','palavra','uf'])
        writer.writeheader()
        writer.writerows(relevantes)
    print(f"[GiLicita] 📊 Planilha: {nome_csv}")
    
    # HTML para iPhone ATUALIZADO com dados reais
    cards = ""
    for r in relevantes[:20]:
        valor_fmt = f"R$ {r['valor']:,.0f}" if r['valor'] else "A consultar"
        msg = f"🚨 LICITAÇÃO BRINDES!%0A🏛️ {r['orgao'][:50]}%0A📦 {r['objeto'][:80]}%0A💰 {valor_fmt}%0A🔑 Achou por: {r['palavra']}"
        cards += f'''
<div class="card">
<h3>🏛️ {r['orgao'][:70]}</h3>
<div class="obj">{r['objeto'][:180]}</div>
<div class="meta">
<span class="badge money">{valor_fmt}</span>
<span class="badge">{r['uf']}</span>
<span class="badge">🔑 {r['palavra']}</span>
<span class="badge">{r['abertura'][:10]}</span>
</div>
<a class="btn" href="https://wa.me/?text={msg}" target="_blank">💬 Mandar para Gi</a>
<a class="btn2" href="{r['link']}" target="_blank">📄 Ver Edital no PNCP</a>
</div>
'''
    
    html = f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="theme-color" content="#059669">
<title>GiLicita REAL - {len(relevantes)} licitações</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,sans-serif}}
body{{background:#f0fdf4;padding:16px;max-width:430px;margin:0 auto}}
.header{{background:#059669;color:white;padding:20px;border-radius:20px;text-align:center;margin-bottom:14px}}
.card{{background:white;border-radius:18px;padding:16px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,0.06);border-left:5px solid #059669}}
.badge{{background:#ecfdf5;color:#065f46;padding:4px 9px;border-radius:99px;font-size:11px;font-weight:600;margin-right:4px}}
.badge.money{{background:#059669;color:white}}
.btn{{display:block;background:#25D366;color:white;text-align:center;padding:14px;border-radius:12px;font-weight:700;text-decoration:none;margin-bottom:6px}}
.btn2{{display:block;background:white;color:#059669;border:1px solid #a7f3d0;text-align:center;padding:10px;border-radius:12px;font-weight:600;text-decoration:none;font-size:13px}}
</style></head><body>
<div class="header"><h1>🎁 GiLicita REAL</h1><p>{len(relevantes)} licitações encontradas HOJE - Brasil todo</p><p style="font-size:11px;margin-top:4px">{hoje} • {', '.join(PALAVRAS_CHAVE)}</p></div>
{cards}
<div style="text-align:center;padding:20px;color:#666;font-size:12px">Dados REAIS do PNCP • Atualize rodando o script no PC</div>
</body></html>'''
    
    with open('GiLicita-iPhone-REAL.html','w',encoding='utf-8') as f:
        f.write(html)
    print(f"[GiLicita] 📱 iPhone REAL: GiLicita-iPhone-REAL.html")

if __name__ == "__main__":
    relevantes = buscar_pncp_real()
    if relevantes:
        gerar_tudo(relevantes)
        print(f"\n✅ SUCESSO! {len(relevantes)} licitações REAIS!")
        print(f"Agora mande GiLicita-iPhone-REAL.html para seu iPhone!")
    else:
        print("\n⚠️ Nenhuma com essas palavras hoje. Tente aumentar dias para 90")
