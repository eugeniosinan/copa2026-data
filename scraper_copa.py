from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone, timedelta

URL_FIFA = "https://www.fifa.com/pt/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?country=BR&wtw-filter=ALL"

# Dicionário de padronização (De: Nome FIFA -> Para: Nome Planilha)
DE_PARA_TIMES = {
    "República da Coreia": "Coreia do Sul",
    "Tchéquia": "República Tcheca",
    "Bósnia e Herzegovina": "Bósnia",
    "RI do Irã": "Irã",
    "Curaçau": "Curaçao",
    "RD do Congo": "RD Congo"
}

def raspar_resultados():
    # Define o fuso horário de Brasília (UTC-3)
    fuso_brasilia = timezone(timedelta(hours=-3))
    
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(URL_FIFA)
        pagina.wait_for_timeout(5000)
        html = pagina.content()
        navegador.close()

    soup = BeautifulSoup(html, 'html.parser')
    texto_pagina = soup.get_text(separator='|', strip=True)
    pedacos = texto_pagina.split('|')
    
    jogos = []
    for i, texto in enumerate(pedacos):
        if texto == "FIM":
            try:
                # Pega os nomes originais retornados pelo site da FIFA
                nome_mandante_cru = pedacos[i-2].strip()
                nome_visitante_cru = pedacos[i+3].strip()

                jogo = {
                    "sigla_mandante": pedacos[i-3].strip(),
                    # O .get() tenta achar no dicionário. Se não achar, usa o nome original mesmo.
                    "mandante": DE_PARA_TIMES.get(nome_mandante_cru, nome_mandante_cru),
                    "gols_mandante": int(pedacos[i-1].strip()),
                    "gols_visitante": int(pedacos[i+1].strip()),
                    "sigla_visitante": pedacos[i+2].strip(),
                    "visitante": DE_PARA_TIMES.get(nome_visitante_cru, nome_visitante_cru),
                    "status": "Finalizado",
                    "atualizado_em": datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")
                }
                jogos.append(jogo)
            except (IndexError, ValueError):
                pass

    # Estrutura do payload final também com a hora correta
    payload = {
        "ultima_atualizacao": datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S"),
        "total_jogos_finalizados": len(jogos),
        "resultados": jogos
    }

    # Salva o arquivo JSON
    with open('resultados_copa.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    raspar_resultados()