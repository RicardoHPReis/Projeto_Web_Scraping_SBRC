# Código desenvolvido por Ricardo Reis

from bs4 import BeautifulSoup
import requests

def ler_transformar_web(link_url:str, ano_evento:int) -> list:
    anais = []
    pdf_dados = requests.get(link_url)
    soup = BeautifulSoup(pdf_dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    for br in conteudo.find_all("br"):
        br.replace_with("\n")
    
    todos_links = conteudo.find_all('p')
    for link in todos_links:
        if link.find('a') == None:
            continue
        
        texto_descricao = link.get_text().replace('\n\n', '\n')
        
        texto_des = texto_descricao.split('\n')[0]
        texto_titulo = texto_des.split(' pp. ')[0]
        paginas = texto_des.split(' pp. ')[-1].split('-')
        texto_autores = texto_descricao.split('\n')[-1]
        link_anais = link.find('a').get('href')
        
        if ano_evento <= 1998:
            pass
        
        dados_anais_com_ano = {
            "titulo": texto_titulo,
            "paginas": paginas,
            "autores": texto_autores,
            "universidade": "",
            "lingua": "",
            "num_paginas": int(paginas[-1]) - int(paginas[0]) + 1,
            "paginas": [int(paginas[0]), int(paginas[-1])],
            "resumo": "",
            "referencias": "",
            "link": link_anais
        }
        anais.append(dados_anais_com_ano)
    return anais