# Código desenvolvido por Ricardo Reis

import pymupdf as f
import requests
import io
import re

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


def transformar_texto(texto:str) -> str:
    """
    Remove ou substitui caracteres que não foram corretamente extraídos dos PDFs 
    e que podem causar problemas de formatação ou leitura, retornando o texto corrigido.
    """
    
    texto = texto.replace("c¸", "ç").replace("`a", "à").replace("`A", "À")
    texto = texto.replace("´a", "á").replace("´A", "Á").replace("´e", "é").replace("´E", "É").replace("´ı", "í").replace("´I", "Í").replace("´o", "ó").replace("´O", "Ó").replace("´u", "ú").replace("´U", "Ú")
    texto = texto.replace("ˆa", "â").replace("ˆA", "Â").replace("ˆe", "ê").replace("ˆE", "Ê").replace("ˆı", "î").replace("ˆI", "Î").replace("ˆo", "ò").replace("ˆO", "Ô").replace("ˆu", "û").replace("ˆU", "Û")
    texto = texto.replace("˜a", "ã").replace("˜o", "õ").replace("˜A", "Ã").replace("˜O", "Õ")
    texto = texto.replace("˘g", "ğ").replace("s’", "’s")
    texto = texto.replace(" ,", ",").replace(",,", ",").replace(" .", ".").replace(" ;", ";").replace(" :", ":")
    texto = texto.replace("-\n", "").replace("\n", " ").replace("  ", " ").replace("–", "-")
    
    return texto


def ler_transformar_pdf(link_pdf:str, ano_evento:int) -> list:
    anais = []
    inicio_artigos = 0
    fl_referencias = False
    pdf_dados = requests.get(link_pdf)
    pdf_dados.raise_for_status()
    pdf_bytes = io.BytesIO(pdf_dados.content)
    pdf_document = f.open(stream=pdf_bytes, filetype="pdf")
    #print(f"Number of pages: {len(pdf_document)}")
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict") # Obter texto como um dicionário com informações detalhadas
        text = transformar_texto(page.get_text("text"))
        
        lingua = ''
        nomes_artigos = ''
        autores = ''
        universidades = ''
        ordem = ''
        resumo = ''
        fl_inicio_artigo = False
        fl_ordem = False
        fl_universidade = False
        
        if (text.find("Abstract.") != -1 or text.find("Abstract -") != -1):
            fl_referencias = False
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]: 
                            texto_base = transformar_texto(span["text"])
                            font_name = span["font"]
                            font_size = span["size"]
                            print(f"Texto: '{texto_base}', Fonte: {font_name}, Tamanho: {font_size}")
                            
                            if texto_base.strip() == "":
                                continue
                            
                            # Regras 
                            # A ideia é usar uma combinação de regras para tentar identificar o título da melhor forma possível, mesmo que haja algumas inconsistências na formatação dos PDFs.
                            # A ideia é identificar o título do artigo, que é a informação mais fácil de identificar, pois geralmente tem uma formatação mais clara e consistente.
                            
                            # Titulo: Fonte >= 15 e texto com mais de 2 caracteres
                            if font_size >= 15 and len(texto_base) > 2:
                                nomes_artigos += texto_base + ' '
                                fl_inicio_artigo = True
                                
                            # Fim dos dados iniciais do artigo: Fonte padrão ou início do Resumo/Abstract
                            elif texto_base.find("Abstract") != -1 or texto_base.find("Resumo") != -1:
                                fl_ordem = False
                                fl_inicio_artigo = False
                                
                            # Fim dos dados iniciais do artigo: Fonte padrão ou início do Resumo/Abstract
                            elif font_name == 'NimbusMonL-Regu' or font_name == 'NimbusMonoL' or font_name.find("Ital") != -1 or font_name.find("Courier") != -1:
                                fl_ordem = False
                                continue
                            
                            #Regras para identificar os dados de autores, universidade e a ordem, que são os mais difíceis de identificar, pois não possuem uma formatação tão clara quanto os dados de título e autores. A ideia é usar uma combinação de regras para tentar identificar esses dados da melhor forma possível, mesmo que haja algumas inconsistências na formatação dos PDFs.
                            elif fl_inicio_artigo:
                                # Ordem: Fonte CMMI8 e texto com até 3 caracteres, ou Fonte CMR8 (ou tamanho <= 8.1)
                                if (font_name == 'CMMI8') and len(texto_base) <= 3:
                                    ordem += texto_base
                                    fl_ordem = False
                                    
                                # Ordem: Fonte de tamanho <= 8.1, texto com até 3 caracteres, flag e sem fl_ordem e sem fl_universidade
                                elif font_size <= 8.1 and not fl_ordem and not fl_universidade:
                                    if ordem != '' and not ordem.endswith(',') and not ordem.endswith('|'):
                                        ordem += '|'
                                    ordem += texto_base
                                    fl_ordem = True
                                
                                # Se tiver algum numero no meio dos dados de universidade, é mais provável que seja parte da ordem do que da universidade, então há um pipe para separar os dados de universidade
                                elif font_size<=8.1 and fl_universidade:
                                    universidades += '|'
                                
                                # Autores: Fonte NimbusRomNo9L-Medi ou fonte com "Bold" e fonte maior que 11
                                elif (font_name == 'NimbusRomanNo9L' or font_name.find("Medi") != -1 or font_name.find("Bold") != -1) and not fl_universidade and font_size >= 10.9:
                                    if autores != '' and not texto_base.startswith(','):
                                        autores += ', '
                                    if texto_base != ',' and texto_base != ', ':
                                        autores += texto_base
                                    fl_ordem = False
                                
                                # Universidade: Fonte NimbusRomNo9L-Regu ou fonte com "Times"
                                elif (font_name == 'NimbusRomanNo9L' or font_name.find("Regu") != -1 or font_name.find("Times") != -1) and font_size > 8.1:
                                    if universidades != '' and not universidades.endswith('|'):
                                        universidades += ' '
                                    universidades += texto_base
                                    fl_universidade = True
                                    fl_ordem = False
                                
                                # Universidade: Fonte de tamanho <= 8.1 e fl_ordem
                                elif font_size<=8.1 and fl_ordem:
                                    fl_universidade = True

            # Se o texto da página contém "Resumo." ou "Resumo -", é provável que seja o início do resumo em português, caso contrário, é provável que seja o início do resumo em inglês. 
            # A ideia é usar essa informação para tentar identificar o resumo da melhor forma possível, mesmo que haja algumas inconsistências na formatação dos PDFs.
            if (text.find("Resumo.") != -1 or text.find("Resumo -") != -1):
                lingua = 'Pt'
                resumo = text.split("Resumo -", 1)[-1] if text.find("Resumo -") != -1 else text.split("Resumo.", 1)[-1]
                resumo = resumo.split("1.", 1)[0].strip()
            else:
                lingua = 'En'
                abstract = text.split("Abstract -", 1)[-1] if text.find("Abstract -") != -1 else text.split("Abstract.", 1)[-1]
                resumo = abstract.split("1.", 1)[0].strip()
            
            # Junção de todos os dados do artigo em um dicionário, que é adicionado a uma lista de anais. 
            # A ideia é criar um dicionário com todas as informações do artigo, para facilitar a organização e o acesso a essas informações posteriormente.
            dados_anais_com_ano = {
                "titulo": transformar_texto(nomes_artigos.strip()),
                "autores": transformar_texto(autores.strip()),
                "ordem": transformar_texto(ordem.strip()),
                "universidade": transformar_texto(universidades.strip()),
                "lingua": lingua,
                "num_paginas": 0,
                "paginas": [int(page_num-inicio_artigos)],
                "paginas_pdf": [int(page_num)+1],
                "resumo": transformar_texto(resumo.strip()),
                "referencias": "",
                "link": ""
            }
            
            # Se o artigo anterior não tiver o número de páginas definido, é provável que o início do próximo artigo seja o final do artigo anterior, então há uma atualização do número de páginas do artigo anterior.
            if len(anais) > 0 and anais[-1]['num_paginas'] == 0:
                anais[-1]['paginas'].append(int(page_num) - inicio_artigos - 1)
                anais[-1]['paginas_pdf'].append(int(page_num))
                anais[-1]['num_paginas'] = dados_anais_com_ano['paginas'][0] - anais[-1]['paginas'][0]
            
            # Se o artigo atual for o primeiro artigo encontrado, é provável que o início do artigo seja o início do PDF, então há uma atualização do número de páginas do artigo atual.
            if len(anais) == 0:
                inicio = 3 if ano_evento != 2015 else 1
                inicio_artigos = int(page_num) - inicio
                dados_anais_com_ano['paginas'][0] = page_num - inicio_artigos
                
            print(f"{dados_anais_com_ano}")
            anais.append(dados_anais_com_ano)
        
        if len(anais) > 0:
            # Caso haja algum artigo que apresente um resumo em protuguês, mas não foi identificado na primeira página, é feito a busca novamente.
            if (text.find("Resumo.") != -1 or text.find("Resumo -") != -1) and anais[-1]['lingua'] != "En":
                fl_referencias = False
                resumo_pt = text.split("Resumo -", 1)[-1] if text.find("Resumo -") != -1 else text.split("Resumo.", 1)[-1]
                resumo_pt = resumo_pt.split("1.", 1)[0].strip()
                anais[-1]['resumo'] = transformar_texto(resumo_pt.strip())
                anais[-1]['lingua'] = 'Pt'
            
            # Se o texto da página conter "Índice por Autor" ou "Sessão Técnica", é preciso atualizar o número de páginas do artigo.
            if text.find("Índice por Autor") != -1 and (ano_evento == 2013 or ano_evento == 2014) and inicio_artigos > 0:
                anais[-1]['paginas'].append(int(page_num) - inicio_artigos - 1)
                anais[-1]['paginas_pdf'].append(int(page_num))
                anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0] + 1
                fl_referencias = False
            if text.find("Sessão Técnica ") != -1 and (ano_evento == 2013 or ano_evento == 2014) and inicio_artigos > 0:
                anais[-1]['paginas'].append(int(page_num) - inicio_artigos - 1)
                anais[-1]['paginas_pdf'].append(int(page_num))
                anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0] + 1
                fl_referencias = False
            
            # Se o texto da página contém "Referências" ou "References", é provável que seja o início das referências do artigo, então há uma atualização do campo de referências do artigo atual.
            if text.find("Referências") != -1 or text.find("References") != -1 or fl_referencias:
                if fl_referencias:
                    anais[-1]['referencias'] += text
                else:
                    anais[-1]['referencias'] = text.split("Referências", 1)[-1] if text.find("Referências") != -1 else text.split("References", 1)[-1]
                fl_referencias = True
    
    # Necessário para atualizar o número de páginas do último artigo, pois o final do PDF pode ser o final do último artigo, então há uma atualização do número de páginas do último artigo.
    if len(anais) > 0:
        if anais[-1]['num_paginas'] == 0:
            anais[-1]['paginas'].append(len(pdf_document)-inicio_artigos-2)
            anais[-1]['paginas_pdf'].append(len(pdf_document)-1)
            anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0]
    
    # Criação de um novo documento PDF para cada artigo, contendo apenas as páginas correspondentes a esse artigo, e salvando esses documentos em uma pasta específica para o ano do evento.
    for i, artigo in enumerate(anais):
        novo_doc = f.open()  # Cria um novo documento PDF
        nome_arquivo = limpar_nome_arquivo(artigo['titulo'])
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