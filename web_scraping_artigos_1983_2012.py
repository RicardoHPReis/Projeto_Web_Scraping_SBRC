# Código desenvolvido por Ricardo Reis

from bs4 import BeautifulSoup
import requests

def ler_transformar_web(link_url:str) -> list:
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
        paginas = texto_des.split(' pp. ')[-1]
        texto_autores = texto_descricao.split('\n')[-1]
        link_anais = link.find('a').get('href')
        
        dados_anais_com_ano = {
            "Título": texto_titulo,
            "Páginas": paginas,
            "Autores": texto_autores,
            "Universidade": "",
            "Email": "",
            "Língua": "",
            "Resumo": "",
            "Link": link_anais
        }
        anais.append(dados_anais_com_ano)
    return anais