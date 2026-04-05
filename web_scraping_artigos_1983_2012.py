# Código desenvolvido por Ricardo Reis

from bs4 import BeautifulSoup
import pymupdf as f
import requests
import re
import io

def limpar_nome_arquivo(nome:str) -> str:
    """
    Remove ou substitui caracteres que não são permitidos em nomes de arquivos 
    (Windows, Linux e macOS).
    """
    
    padrao_invalido = r'[<>:"/\\|?*\x00-\x1f]'
    
    # Substitui os caracteres inválidos
    nome_seguro = re.sub(padrao_invalido, "", nome)
    nome_seguro = nome_seguro.replace("  ", " ")
    
    nome_seguro = nome_seguro if len(nome_seguro) <= 130 else nome_seguro[:130] 
        
    return nome_seguro


def ler_transformar_web(link_url:str, ano_evento:int) -> list:
    anais = []
    pdf_dados = requests.get(link_url)
    soup = BeautifulSoup(pdf_dados.content, 'html.parser')
    conteudo = soup.find('div', class_='entry-content')
    for br in conteudo.find_all("br"):
        br.replace_with("\n")
    
    todos_links = conteudo.find_all('p')
    for i, link in enumerate(todos_links):
        if link.find('a') == None:
            continue
        
        texto_descricao = link.get_text().replace('\n\n', '\n')
        
        texto_des = texto_descricao.split('\n')[0]
        texto_titulo = texto_des.split(' pp. ')[0]
        paginas = texto_des.split(' pp. ')[-1].split('-')
        texto_autores = texto_descricao.split('\n')[-1]
        link_artigo = link.find('a').get('href')
        
        print(f"Processando artigo: {i} {texto_titulo} - {texto_autores} - {paginas} - {link_artigo}")
        
        if ano_evento <= 1998:
            pass
        
        pdf_artigo = requests.get(link_artigo)
        pdf_document = f.open(stream=io.BytesIO(pdf_artigo.content), filetype="pdf")
        if pdf_artigo.status_code == 200:
            # Salva o conteúdo em um arquivo binário (.pdf)
            if texto_descricao == "Páginas Iniciais":
                with open(f"SOL_SBRC/SBRC_{ano_evento}/{i}_paginas_iniciais.pdf", 'wb') as doc:
                    doc.write(pdf_artigo.content)
            else:
                nome_arquivo = limpar_nome_arquivo(texto_titulo)
                with open(f"SOL_SBRC/SBRC_{ano_evento}/{i}_{nome_arquivo}.pdf", 'wb') as doc:
                    doc.write(pdf_artigo.content)
            
        dados_anais_com_ano = {
            "titulo": texto_titulo,
            "paginas": paginas,
            "autores": texto_autores,
            "universidade": "",
            "lingua": "",
            "num_paginas": len(pdf_document),
            "paginas": [int(paginas[0]), int(paginas[-1])] if texto_descricao != "Páginas Iniciais" else [1, len(pdf_document)],
            "resumo": "",
            "referencias": "",
            "link": link_artigo
        }
        anais.append(dados_anais_com_ano)
    
    return anais