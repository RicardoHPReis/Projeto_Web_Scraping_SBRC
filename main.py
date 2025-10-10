# Código desenvolvido por Ricardo Reis

import web_scraping_artigos_2013_2016 as c_pdf
import web_scraping_artigos_1983_2012 as c_link
from bs4 import BeautifulSoup
import requests
import time
import json

def web_scraping_sbrc(url:str) -> list:
    dados = requests.get(url)
    soup = BeautifulSoup(dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    texto_conteudo = conteudo.get_text("\n", strip=True)
    eventos = texto_conteudo.split("\n")

    for i,j in enumerate(eventos):
        eventos[i] = eventos[i].split(" – ")

    todos_links = conteudo.find_all('a')
    for i, link in enumerate(todos_links):
        link_pdf = link.get('href')
        if not link_pdf.startswith('http'):
            link_pdf = f"https://ce-resd.sbc.org.br{link_pdf}"
        eventos[i].append(link_pdf)

    eventos.reverse()
    eventos = [e for e in eventos if int(e[0]) < 2017]
    for i,j in enumerate(eventos):
        eventos[i][0] = int(eventos[i][0])
    
    return eventos


def web_scraping_eventos(eventos:list) -> list:
    lista_anais = {}
    lista_geral = []
    anais = []
    for e in eventos:
        ano_evento = e[0]
        dados_evento = e[1].split(", ")
        nr_simposio = dados_evento[0].split(" ")[0]
        simposio_evento = dados_evento[0].split(" ")[-1]
        cidade_evento = dados_evento[1]
        estado_evento = dados_evento[2]
        link_evento = e[-1]
        
        if ano_evento > 2012:
            anais = c_pdf.ler_transformar_pdf(link_evento)
        else:
            anais = c_link.ler_transformar_web(link_evento)
        
        lista_anais = {
            "ano": ano_evento,
            "nr_simposio": nr_simposio,
            "simposio": simposio_evento,
            "cidade": cidade_evento,
            "estado": estado_evento,
            "anais": anais
        }
        print(f"Ano: {ano_evento} - Total de artigos: {len(anais)}")
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
    url_seed = "https://ce-resd.sbc.org.br/?page_id=40"
    
    lista_simposios = web_scraping_sbrc(url_seed)
    for simposios in lista_simposios:
        print(simposios)
    
    json_geral = web_scraping_eventos(lista_simposios)
    for evento in json_geral:
        soma_artigos += len(evento['anais'])
    
    print(f"Total de eventos: {len(lista_simposios)}\n")
    print(f"Total de artigos: {soma_artigos}")
    
    salvar_json(json_geral, nome_arquivo_final)


if __name__ == "__main__":
    main()