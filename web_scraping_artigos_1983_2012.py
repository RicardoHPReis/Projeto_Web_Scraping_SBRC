# Código desenvolvido por Ricardo Reis

import ler_artigos_ABNT_2003_2016 as abnt
from bs4 import BeautifulSoup
import pymupdf as f
import requests
import re
import io


def ler_transformar_web(link_url:str, ano_evento:int) -> list:
    anais = []
    dados_pdf = []
    pdf_dados = requests.get(link_url)
    soup = BeautifulSoup(pdf_dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    for br in conteudo.find_all("br"):
        br.replace_with("\n")
    
    todos_links = conteudo.find_all('p')
    #todos_links = todos_links[18:21]
    for i, link in enumerate(todos_links):
        if link.find('a') == None:
            continue
        
        texto_descricao = link.get_text().replace('\n\n', '\n')
        
        texto_des = texto_descricao.split('\n')[0]
        texto_titulo = texto_des.split(' pp. ')[0]
        paginas = texto_des.split(' pp. ')[-1].split('-')
        texto_autores = texto_descricao.split('\n')[-1]
        link_artigo = link.find('a').get('href')
        
        if ano_evento >= 2003:
            dados_pdf = abnt.ler_transformar_pdf_ABNT(link_artigo, ano_evento)
        
        pdf_artigo = requests.get(link_artigo)
        pdf_document = f.open(stream=io.BytesIO(pdf_artigo.content), filetype="pdf")
        
        if len(texto_des.split(' pp. ')) == 1 or texto_des.split(' pp. ')[-1].find('.') != -1 or paginas[0] == '' or paginas[-1] == '':
            paginas = [1, len(pdf_document)]
        else:
            paginas = [int(re.sub(r'[^0-9]', '', paginas[0])), int(re.sub(r'[^0-9]', '', paginas[1]))]
            
        #print(f"Processando artigo: {i} {texto_titulo} - {texto_autores} - {paginas} - {link_artigo}")
        
        if pdf_artigo.status_code == 200:
            # Salva o conteúdo em um arquivo binário (.pdf)
            if texto_descricao == "Páginas Iniciais":
                with open(f"SOL_SBRC/SBRC_{ano_evento}/{i}_paginas_iniciais.pdf", 'wb') as doc:
                    doc.write(pdf_artigo.content)
            else:
                nome_arquivo = abnt.limpar_nome_arquivo(texto_titulo)
                with open(f"SOL_SBRC/SBRC_{ano_evento}/{i}_{nome_arquivo}.pdf", 'wb') as doc:
                    doc.write(pdf_artigo.content)
            
        dados_anais_com_ano = {
            "titulo": texto_titulo,
            "autores": texto_autores,
            "ordem": "" if dados_pdf == [] else dados_pdf[0]['ordem'],
            "universidade": "" if dados_pdf == [] else dados_pdf[0]['universidade'],
            "lingua": "" if dados_pdf == [] else dados_pdf[0]['lingua'],
            "num_paginas": len(pdf_document),
            "paginas": [paginas[0], paginas[-1]] if texto_descricao != "Páginas Iniciais" else [1, len(pdf_document)],
            "paginas_pdf": [1, len(pdf_document)],
            "resumo": "" if dados_pdf == [] else dados_pdf[0]['resumo'],
            "referencias": "" if dados_pdf == [] else dados_pdf[0]['referencias'],
            "link": link_artigo
        }
        anais.append(dados_anais_com_ano)
    
    return anais