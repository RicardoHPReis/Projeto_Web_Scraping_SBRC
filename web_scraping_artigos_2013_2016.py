# Código desenvolvido por Ricardo Reis

import pymupdf as f
import requests
import io

def transformar_texto(texto:str) -> str:
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
    flag_ref = False
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
        flag = False
        flag_numeros = False
        flag_universidade = False
        
        if text.find("Abstract.") != -1:
            flag_ref = False
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
                            
                            if font_size >= 15 and len(texto_base) > 2:
                                nomes_artigos += texto_base + ' '
                                flag = True
                            elif font_name == 'NimbusMonL-Regu' or font_name.find("Italic") != -1 or font_name.find("Courier") != -1:
                                flag_numeros = False
                                flag = False
                            elif (font_name == 'CMMI8') and flag and len(texto_base) <= 2:
                                ordem += texto_base
                                flag_numeros = False
                            elif (font_name == 'CMR8' or (font_size<=8.1)) and not flag_numeros and flag and not flag_universidade and len(texto_base) <= 2:
                                ordem += texto_base
                                flag_numeros = True
                            elif (font_name == 'CMR8' or (font_size<=8.1)) and flag_universidade and flag and len(texto_base) <= 2:
                                universidades += '|'
                            elif (font_name == 'NimbusRomNo9L-Medi' or font_name.find("Bold") != -1) and font_size >= 11 and flag:
                                autores += ', ' if not autores.endswith(',') and autores != '' else ''
                                autores += texto_base + ' '
                                
                                ordem += '|' if not ordem.endswith('|') else ''
                                flag_numeros = False
                            elif (font_name == 'NimbusRomNo9L-Regu' or font_name.find("Times") != -1) and font_size >= 11 and flag:
                                universidades += texto_base + ' '
                                flag_numeros = False
                            elif (font_name == 'CMR8' or (font_size<=8.1)) and flag and flag_numeros:
                                universidades += '|'
                                flag_universidade = True

            abstract = text.split("Abstract.", 1)[-1]
            if text.find("Resumo.") != -1:
                lingua = 'Pt'
                resumo = text.split("Resumo.", 1)[-1]
                resumo = resumo.split("1.", 1)[0].strip()
            else:
                lingua = 'En'
                resumo = abstract.split("1.", 1)[0].strip()
            
            dados_anais_com_ano = {
                "titulo": transformar_texto(nomes_artigos.strip()),
                "autores": transformar_texto(autores.strip()),
                "ordem": transformar_texto(ordem.replace('|','',1).strip()),
                "universidade": transformar_texto(universidades.replace('|','',1).strip()),
                "lingua": lingua,
                "num_paginas": 0,
                "paginas": [int(page_num-inicio_artigos)],
                "paginas_pdf": [int(page_num)+1],
                "resumo": transformar_texto(resumo.strip()),
                "referencias": "",
                "link": ""
            }
            if len(anais) > 0 and anais[-1]['num_paginas'] == 0:
                anais[-1]['paginas'].append(int(page_num) - inicio_artigos - 1)
                anais[-1]['paginas_pdf'].append(int(page_num))
                anais[-1]['num_paginas'] = dados_anais_com_ano['paginas'][0] - anais[-1]['paginas'][0]
            if len(anais) == 0:
                inicio = 3 if ano_evento != 2015 else 1
                inicio_artigos = int(page_num) - inicio
                dados_anais_com_ano['paginas'][0] = page_num - inicio_artigos
            anais.append(dados_anais_com_ano)
            
        if text.find("Resumo.") != -1 and anais[-1]['resumo'] != "" :
            flag_ref = False
            resumo_pt = text.split("Resumo.", 1)[-1]
            resumo_pt = resumo_pt.split("1.", 1)[0].strip()
            anais[-1]['resumo'] = transformar_texto(resumo_pt.strip())
            anais[-1]['lingua'] = 'Pt'
            
        if text.find("Índice por Autor") != -1 and (ano_evento == 2013 or ano_evento == 2014) and inicio_artigos > 0:
            anais[-1]['paginas'].append(int(page_num) - inicio_artigos - 1)
            anais[-1]['paginas_pdf'].append(int(page_num))
            anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0] + 1
            flag_ref = False
        if text.find("Sessão Técnica ") != -1 and (ano_evento == 2013 or ano_evento == 2014) and inicio_artigos > 0:
            anais[-1]['paginas'].append(int(page_num) - inicio_artigos - 1)
            anais[-1]['paginas_pdf'].append(int(page_num))
            anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0] + 1
            flag_ref = False
        
        if text.find("Referências") != -1 or text.find("References") != -1 or flag_ref:
            if flag_ref:
                anais[-1]['referencias'] += text
            else:
                anais[-1]['referencias'] = text.split("Referências", 1)[-1] if text.find("Referências") != -1 else text.split("References", 1)[-1]
            flag_ref = True
    
    if anais[-1]['num_paginas'] == 0:
        anais[-1]['paginas'].append(len(pdf_document)-inicio_artigos-2)
        anais[-1]['paginas_pdf'].append(len(pdf_document)-1)
        anais[-1]['num_paginas'] = anais[-1]['paginas'][1] - anais[-1]['paginas'][0]
    
    return anais