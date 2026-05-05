# Código desenvolvido por Ricardo Reis

import web_scraping_artigos_2013_2016 as c_pdf
import web_scraping_artigos_1983_2012 as c_link
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time
import json
import re

# Função para realizar o web scraping e ler os coordenadores dos eventos da SBRC, retornando uma lista de coordenadores com seus respectivos anos e funções
def adcionar_coordenadores(link_url:str) -> list:
    coordenadores = []
    pdf_dados = requests.get(link_url)
    soup = BeautifulSoup(pdf_dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    for br in conteudo.find_all("br"):
        br.replace_with("\n")
    
    todos_links = conteudo.find_all('p')
    for i in range(0, len(todos_links), 2):
        if i+1 >= len(todos_links):
            break
        texto_simposio = todos_links[i].get_text()
        texto_coordenadores = todos_links[i+1].get_text().replace('\n\n', '\n')
        pessoas = texto_coordenadores.split("\n")
        
        ano = int(texto_simposio.split(" – ")[0])
        coord_geral = pessoas[0].replace("Geral:", "").strip()
        coord_programa = pessoas[1].replace("Programa:", "").strip()
        
        coordenadores.append([ano, coord_geral, coord_programa])
    
    coordenadores = [e for e in coordenadores if int(e[0]) <= 2016]
    
    coordenadores.reverse()
    #print(coordenadores)
    return coordenadores
 
# Função para realizar o web scraping e ler os prêmios dos eventos da SBRC, retornando uma lista de prêmios com seus respectivos anos e vencedores
def adcionar_premios(link_url:str) -> list:
    premios = []
    pdf_dados = requests.get(link_url)
    soup = BeautifulSoup(pdf_dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    for br in conteudo.find_all("br"):
        br.replace_with("\n")
    
    texto_premios = conteudo.find_all('p')[-1]
    texto = texto_premios.get_text().replace('\n\n', '\n').replace('–\n', '- ').replace(' (in memoriam)', '')
    lista_premios = texto.split('\n')
    for i, prem in enumerate(lista_premios):
        lista = prem.split(' – ')
        lista[0] = int(lista[0])
        lista[1] = lista[1].strip()
        premios.append(lista)
        
    premios = [e for e in premios if int(e[0]) <= 2016]
    
    premios.reverse()
    #print(premios)
    return premios

# Função para realizar o web scraping dos eventos da SBRC, retornando uma lista de eventos com seus respectivos links para os anais
def web_scraping_sbrc(url:str) -> list:
    dados_pagina = requests.get(url)
    dados_html = BeautifulSoup(dados_pagina.content, 'html.parser')
    conteudo_principal = dados_html.find('div', class_='entry-content')
    texto_conteudo = conteudo_principal.get_text("\n", strip=True)
    eventos_sbrc = texto_conteudo.split("\n")

    # Realiza a limpeza e formatação dos dados dos eventos da SBRC, utilizando expressões regulares para separar os campos de cada evento, e removendo espaços em branco desnecessários
    for i,j in enumerate(eventos_sbrc):
        eventos_sbrc[i] = re.split(r'[–,]', eventos_sbrc[i])
        eventos_sbrc[i] = [eventos_sbrc[i][0]] + eventos_sbrc[i][1].split() + eventos_sbrc[i][2:]
        eventos_sbrc[i] = [e.strip() for e in eventos_sbrc[i] if e.strip()]
        eventos_sbrc[i][0] = int(eventos_sbrc[i][0])
    
    # Adiciona os coordenadores e os prêmios aos eventos da SBRC, utilizando as funções de leitura de coordenadores e prêmios, e associando-os aos eventos correspondentes
    lista_coords = adcionar_coordenadores('https://ce-resd.sbc.org.br/?page_id=49')
    lista_premios = adcionar_premios('https://ce-resd.sbc.org.br/?page_id=296')
    for i, j in enumerate(eventos_sbrc):
        coord_geral = [c[1] for c in lista_coords if c[0] == eventos_sbrc[i][0]]
        coord_prog = [c[2] for c in lista_coords if c[0] == eventos_sbrc[i][0]]
        premiados = [p[1] for p in lista_premios if p[0] == eventos_sbrc[i][0]]
        
        eventos_sbrc[i].append(coord_geral[0] if coord_geral != [] else '') # Coordenador Geral
        eventos_sbrc[i].append(coord_prog[0] if coord_prog != [] else '')   # Coordenador do Programa
        eventos_sbrc[i].append(premiados[0] if premiados != [] else '')     # Premiados

    # Adiciona os links para os anais dos eventos da SBRC, utilizando o BeautifulSoup para extrair os links presentes na página e associando-os aos eventos correspondentes
    todos_links = conteudo_principal.find_all('a')
    for i, link in enumerate(todos_links):
        link_pdf = link.get('href')
        if not link_pdf.startswith('http'):
            link_pdf = f"https://ce-resd.sbc.org.br{link_pdf}"
        eventos_sbrc[i].append(link_pdf)
    eventos_sbrc.reverse()
    
    # Filtra os eventos da SBRC para incluir apenas aqueles até o ano de 2016, utilizando uma compreensão de lista para selecionar apenas os eventos que atendem a essa condição, e convertendo o ano de cada evento para um inteiro para facilitar a comparação
    #eventos_sbrc = [e for e in eventos_sbrc if int(e[0]) <= 2016]
    eventos_sbrc = [e for e in eventos_sbrc if int(e[0]) == 1990]
    
    return eventos_sbrc

# Função principal para realizar o web scraping dos eventos e seus respectivos anais, utilizando as funções de leitura e transformação de PDF ou web, dependendo do ano do evento
def web_scraping_eventos(eventos_sbrc:list) -> list:
    lista_anais = {}
    lista_geral = []
    anais = []
    
    for ev in eventos_sbrc:
        # Marca o tempo de início
        inicio = time.perf_counter()
        
        ano_evento = ev[0]
        nr_simposio = ev[1]
        simposio_evento = ev[2]
        cidade_evento = ev[3]
        estado_evento = ev[4]
        coord_geral_evento = ev[5]
        coord_programa_evento = ev[6]
        premiados_evento = ev[7]
        link_evento = ev[-1]
        
        if ano_evento > 2012:   
            # Pega os anais dos eventos de 2013 a 2016, utilizando a função de leitura e transformação de PDF, pois os anais desses eventos estão disponíveis em um único PDF
            anais = c_pdf.ler_transformar_pdf(link_evento, ano_evento)
        else:                   
            # Pega os anais dos eventos de 1983 a 2012, utilizando a função de leitura e transformação de web, pois os anais desses eventos estão disponíveis em páginas web com links para os artigos individuais
            anais = c_link.ler_transformar_web(link_evento, ano_evento)
        
        lista_anais = {
            "ano": ano_evento,
            "nr_simposio": nr_simposio,
            "simposio": simposio_evento,
            "cidade": cidade_evento,
            "estado": estado_evento,
            "coord_geral": coord_geral_evento,
            "coord_programa": coord_programa_evento,
            "premiados": premiados_evento,
            "anais": anais
        }
        # Marca o tempo de fim
        fim = time.perf_counter()

        # Calcula a diferença
        tempo_total = fim - inicio
        
        print(f"Ano: {ano_evento} - Total de artigos: {len(anais)} - Tempo: {tempo_total:.1f} segundos")
        lista_geral.append(lista_anais)
        
    return lista_geral

# Função para salvar os dados em um arquivo JSON, recebendo a lista de dados e o nome do arquivo como parâmetros
def salvar_json(lista_dados:list, nome_arquivo:str) -> None:
    try:
        with open(nome_arquivo, "w", encoding='utf-8') as arquivo_json:
            json.dump(lista_dados, arquivo_json, ensure_ascii=False, indent=4)
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso.")
    except IOError as e:
        print(f"Erro ao salvar arquivo '{nome_arquivo}': {e}")


def salvar_json_por_ano(lista_dados:list, nome_arquivo:str) -> None:
    Path('JSON_SBRC').mkdir(parents=True, exist_ok=True)
    for evento in lista_dados:
        nome_arquivo_final = f"JSON_SBRC/{nome_arquivo}_{evento['ano']}.json"
        try:
            with open(nome_arquivo_final, "w", encoding='utf-8') as arquivo_json:
                json.dump(evento, arquivo_json, ensure_ascii=False, indent=4)
            print(f"Arquivo '{nome_arquivo_final}' salvo com sucesso.")
        except IOError as e:
            print(f"Erro ao salvar arquivo '{nome_arquivo_final}': {e}")


def main():
    soma_artigos = 0
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
    
    #salvar_json(resultado_json, "lista_SBRC.json")
    salvar_json_por_ano(resultado_json, "lista_SBRC")


if __name__ == "__main__":
    main()