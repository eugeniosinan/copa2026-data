from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

URL_FIFA = "https://www.fifa.com/pt/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?country=BR&wtw-filter=ALL"

def raspar_resultados():
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(URL_FIFA)
        pagina.wait_for_timeout(5000) # Espera o JS carregar
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
                    "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                jogos.append(jogo)
            except (IndexError, ValueError):
                pass

    # Estrutura do payload final
    payload = {
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_jogos_finalizados": len(jogos),
        "resultados": jogos
    }

    # Salva os dados em um arquivo JSON
    with open('resultados_copa.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
        
    print(f"[{datetime.now()}] Dados salvos em resultados_copa.json com sucesso!")

if __name__ == "__main__":
    raspar_resultados()
