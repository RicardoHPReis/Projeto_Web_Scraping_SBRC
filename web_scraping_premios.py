# Código desenvolvido por Ricardo Reis

from bs4 import BeautifulSoup
import requests

def ler_premios(link_url:str) -> list:
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
        
    premios.reverse()
    #print(premios)
    return premios
ler_premios('https://ce-resd.sbc.org.br/?page_id=296')