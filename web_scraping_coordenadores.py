# Código desenvolvido por Ricardo Reis

from bs4 import BeautifulSoup
import requests

def ler_coordenadores(link_url:str) -> list:
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
    
    coordenadores.reverse()
    #print(coordenadores)
    return coordenadores

ler_coordenadores('https://ce-resd.sbc.org.br/?page_id=49')