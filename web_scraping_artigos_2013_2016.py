# Código desenvolvido por Ricardo Reis

import ler_artigos_ABNT_2003_2016 as abnt
import pymupdf as f
import requests
import io
import re


def ler_transformar_pdf(link_pdf:str, ano_evento:int) -> list:
    anais = []
    inicio_artigos = 0
    pdf_dados = requests.get(link_pdf)
    pdf_dados.raise_for_status()
    pdf_bytes = io.BytesIO(pdf_dados.content)
    pdf_document = f.open(stream=pdf_bytes, filetype="pdf")
    
    anais = abnt.ler_transformar_pdf_ABNT(link_pdf, ano_evento)
   
    # Necessário para atualizar o número de páginas do último artigo, pois o final do PDF pode ser o final do último artigo, então há uma atualização do número de páginas do último artigo.
    if len(anais) > 0:
        if anais[-1]['num_paginas'] == 0:
            anais[-1]['paginas'].append(len(pdf_document)-inicio_artigos-2)
            anais[-1]['paginas_pdf'].append(len(pdf_document)-1)
            anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0]
    
    # Criação de um novo documento PDF para cada artigo, contendo apenas as páginas correspondentes a esse artigo, e salvando esses documentos em uma pasta específica para o ano do evento.
    for i, artigo in enumerate(anais):
        novo_doc = f.open()  # Cria um novo documento PDF
        nome_arquivo = abnt.limpar_nome_arquivo(artigo['titulo'])
        novo_doc.insert_pdf(pdf_document, from_page=artigo['paginas_pdf'][0]-1, to_page=artigo['paginas_pdf'][1]-1)
        novo_doc.save(f"SOL_SBRC/SBRC_{ano_evento}/{i+1}_{nome_arquivo}.pdf")
    
    # Criação de um novo documento PDF contendo as páginas que não foram utilizadas para os artigos, e salvando esse documento em uma pasta específica para o ano do evento.
    paginas_nao_utilizadas = range(1, len(pdf_document))
    for artigo in anais:
        paginas_nao_utilizadas = [p for p in paginas_nao_utilizadas if p < artigo['paginas_pdf'][0] or p > artigo['paginas_pdf'][1]]
    
    resto_doc = f.open()  # Cria um novo documento PDF
    for paginas in paginas_nao_utilizadas:
        resto_doc.insert_pdf(pdf_document, from_page=paginas-1, to_page=paginas-1)
    
    resto_doc.save(f"SOL_SBRC/SBRC_{ano_evento}/paginas_nao_utilizadas.pdf")
    
    return anais