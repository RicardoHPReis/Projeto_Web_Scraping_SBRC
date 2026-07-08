# Código desenvolvido por Ricardo Reis

import ler_artigos_ABNT_2003_2016 as abnt
from bs4 import BeautifulSoup
import pymupdf as f
import requests
import re
import io

def separar_titulo_paginas(texto_descricao:str, num_paginas:int) -> tuple:
    texto_descricao = texto_descricao.replace('(short paper)', '')
    texto_titulo = texto_descricao
    texto_inicial = texto_descricao
    parte_titulo = ''
    parte_paginas = ''
    paginas = [1, num_paginas]
    
    if texto_descricao.find(' pp.') != -1:
        texto_inicial = texto_descricao.split(' pp.', 1)
    elif texto_descricao.find('.pp.') != -1:
        texto_inicial = texto_descricao.split('.pp.', 1)
    elif texto_descricao.find(' p.') != -1:
        texto_inicial = texto_descricao.split(' p.', 1)
    elif texto_descricao.find(' pp') != -1:
        texto_inicial = texto_descricao.split(' pp', 1)
    elif texto_descricao.find('. ') != -1:
        texto_inicial = texto_descricao.split('. ', 1)

    if isinstance(texto_inicial, str):
        parte_titulo = texto_descricao.strip()
        parte_paginas = ''
    else:
        parte_titulo = texto_inicial[0].strip()
        parte_paginas = texto_inicial[-1].strip()
    
    texto_titulo = parte_titulo if parte_titulo[-1] != '.' else parte_titulo[:-1]
    if len(parte_paginas) > 0:
        parte_paginas = parte_paginas if parte_paginas[-1] != '.' else parte_paginas[:-1]
    paginas = parte_paginas.split('-')
    paginas = [p.strip() for p in paginas]
    
    #print(f"Texto descrição: {texto_descricao} - Texto título: {texto_titulo} - Páginas: {paginas}") 
    if paginas[0] != '' and paginas[-1] == '':
        paginas = [int(re.sub(r'[^0-9]', '', paginas[0])), int(re.sub(r'[^0-9]', '', paginas[0]))+num_paginas-1]
    elif paginas[0] == '' and paginas[-1] != '':
        paginas = [int(re.sub(r'[^0-9]', '', paginas[1]))-num_paginas+1, int(re.sub(r'[^0-9]', '', paginas[1]))]
    elif len(texto_inicial) == 1 or parte_paginas.find('.') != -1 or len(paginas) <= 1:
        paginas = [1, num_paginas]
    else:
        paginas = [int(re.sub(r'[^0-9]', '', paginas[0])), int(re.sub(r'[^0-9]', '', paginas[1]))]

    return texto_titulo, paginas


def ler_transformar_web(link_url:str, ano_evento:int) -> list:
    anais = []
    dados_pdf = []
    pdf_dados = requests.get(link_url)
    pdf_unificado = f.open()
    soup = BeautifulSoup(pdf_dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    for br in conteudo.find_all("br"):
        br.replace_with("\n")
    
    todos_links = conteudo.find_all('p')
    for i, link in enumerate(todos_links):
        if link.find('a') == None:
            continue
        
        link_artigo = link.find('a').get('href')
        pdf_artigo = requests.get(link_artigo)
        pdf_document = f.open(stream=io.BytesIO(pdf_artigo.content), filetype="pdf")
        pdf_unificado.insert_file(pdf_document)
        
        texto_descricao = link.get_text().replace('\n\n', '\n')
        texto_des = texto_descricao.split('\n')[0]
        texto_titulo, paginas = separar_titulo_paginas(texto_des, len(pdf_document))
        texto_autores = texto_descricao.split('\n')[-1]
        
        if ano_evento >= 2003:
            dados_pdf = abnt.ler_transformar_pdf_ABNT(link_artigo, ano_evento)
            
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
            "titulo": abnt.transformar_texto(texto_titulo.strip()),
            "autores": abnt.transformar_texto(texto_autores.strip()),
            "ordem": "" if dados_pdf == [] else abnt.transformar_texto(dados_pdf[0]['ordem'].strip()),
            "universidade": "" if dados_pdf == [] else abnt.transformar_texto(dados_pdf[0]['universidade'].strip()),
            "lingua": "" if dados_pdf == [] else abnt.transformar_texto(dados_pdf[0]['lingua'].strip()),
            "num_paginas": len(pdf_document),
            "paginas": [paginas[0], paginas[-1]] if texto_descricao != "Páginas Iniciais" else [1, len(pdf_document)],
            "paginas_pdf": [1, len(pdf_document)],
            "resumo": "" if dados_pdf == [] else abnt.transformar_texto(dados_pdf[0]['resumo'].strip()),
            "referencias": "" if dados_pdf == [] else abnt.transformar_texto(dados_pdf[0]['referencias'].strip()),
            "link": link_artigo
        }
        anais.append(dados_anais_com_ano)
    
    pdf_unificado.close()
    
    return anais