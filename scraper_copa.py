from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timezone, timedelta

URL_FIFA = "https://www.fifa.com/pt/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?country=BR&wtw-filter=ALL"

def raspar_resultados():
    # Cria a regra do fuso horário de Brasília (UTC-3)
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
                jogo = {
                    "sigla_mandante": pedacos[i-3].strip(),
                    "mandante": pedacos[i-2].strip(),
                    "gols_mandante": int(pedacos[i-1].strip()),
                    "gols_visitante": int(pedacos[i+1].strip()),
                    "sigla_visitante": pedacos[i+2].strip(),
                    "visitante": pedacos[i+3].strip(),
                    "status": "Finalizado",
                    # Usa o fuso horário aqui
                    "atualizado_em": datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")
                }
                jogos.append(jogo)
            except (IndexError, ValueError):
                pass

    # Usa o fuso horário aqui também no cabeçalho do JSON
    payload = {
        "ultima_atualizacao": datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S"),
        "total_jogos_finalizados": len(jogos),
        "resultados": jogos
    }

    with open('resultados_copa.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    raspar_resultados()