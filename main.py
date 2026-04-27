# Código desenvolvido por Ricardo Reis

import web_scraping_artigos_2013_2016 as c_pdf
import web_scraping_artigos_1983_2012 as c_link
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time
import json

# Função para realizar o web scraping dos eventos da SBRC, 
# retornando uma lista de eventos com seus respectivos links para os anais
def web_scraping_sbrc(url:str) -> list:
    dados_pagina = requests.get(url)
    dados_html = BeautifulSoup(dados_pagina.content, 'html.parser')
    conteudo_principal = dados_html.find('div', class_='entry-content')
    texto_conteudo = conteudo_principal.get_text("\n", strip=True)
    eventos_sbrc = texto_conteudo.split("\n")

    for i,j in enumerate(eventos_sbrc):
        eventos_sbrc[i] = eventos_sbrc[i].split(" – ")

    todos_links = conteudo_principal.find_all('a')
    for i, link in enumerate(todos_links):
        link_pdf = link.get('href')
        if not link_pdf.startswith('http'):
            link_pdf = f"https://ce-resd.sbc.org.br{link_pdf}"
        eventos_sbrc[i].append(link_pdf)

    eventos_sbrc.reverse()
    eventos_sbrc = [e for e in eventos_sbrc if int(e[0]) <= 2016]
    for i,j in enumerate(eventos_sbrc):
        eventos_sbrc[i][0] = int(eventos_sbrc[i][0])
    
    return eventos_sbrc

# Função principal para realizar o web scraping dos eventos e seus respectivos anais,
# utilizando as funções de leitura e transformação de PDF ou web, dependendo do ano do evento
def web_scraping_eventos(eventos_sbrc:list) -> list:
    lista_anais = {}
    lista_geral = []
    anais = []
    
    for ev in eventos_sbrc:
        # Marca o tempo de início
        inicio = time.perf_counter()
        
        ano_evento = ev[0]
        dados_evento = ev[1].split(", ")
        
        nr_simposio = dados_evento[0].split(" ")[0]
        simposio_evento = dados_evento[0].split(" ")[-1]
        cidade_evento = dados_evento[1]
        estado_evento = dados_evento[2]
        link_evento = ev[-1]
        
        if ano_evento > 2012:   # 2013-2016
            anais = c_pdf.ler_transformar_pdf(link_evento, ano_evento)
        else:                   # 1983-2012
            anais = c_link.ler_transformar_web(link_evento, ano_evento)
        
        lista_anais = {
            "ano": ano_evento,
            "nr_simposio": nr_simposio,
            "simposio": simposio_evento,
            "cidade": cidade_evento,
            "estado": estado_evento,
            "anais": anais
        }
        # Marca o tempo de fim
        fim = time.perf_counter()

        # Calcula a diferença
        tempo_total = fim - inicio
        
        print(f"Ano: {ano_evento} - Total de artigos: {len(anais)} - Tempo: {tempo_total:.1f} segundos")
        lista_geral.append(lista_anais)
        
    return lista_geral

    
def salvar_json(dados:list, nome_arquivo:str) -> None:
    try:
        with open(nome_arquivo, "w", encoding='utf-8') as json_file:
            json.dump(dados, json_file, ensure_ascii=False, indent=4)
        print("Data successfully saved to product_info.json")
    except IOError as e:
        print(f"Error saving file: {e}")


def main():
    soma_artigos = 0
    nome_arquivo_final = "lista_SBRC.json"
    url_inicial = "https://ce-resd.sbc.org.br/?page_id=40"
    
    lista_simposios = web_scraping_sbrc(url_inicial)
    for simposios in lista_simposios:
        print(simposios)

    # Cria uma pasta chamada 'SOL_SBRC'
    Path('SOL_SBRC').mkdir(parents=True, exist_ok=True)
    for simposios in lista_simposios:
        ano_evento = simposios[0]
        Path(f"SOL_SBRC/SBRC_{ano_evento}").mkdir(exist_ok=True)
    
    resultado_json = web_scraping_eventos(lista_simposios)
    for evento in resultado_json:
        soma_artigos += len(evento['anais'])
    
    print(f"Total de eventos: {len(lista_simposios)}\n")
    print(f"Total de artigos: {soma_artigos}")
    
    salvar_json(resultado_json, nome_arquivo_final)


if __name__ == "__main__":
    main()