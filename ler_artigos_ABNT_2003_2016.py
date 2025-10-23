# Código desenvolvido por Ricardo Reis

import pymupdf as f
import requests
import io

def transformar_texto(texto:str) -> str:
    texto = texto.replace("c¸", "ç").replace("`a", "à").replace("`A", "À")
    texto = texto.replace("´a", "á").replace("´A", "Á").replace("´e", "é").replace("´E", "É").replace("´ı", "í").replace("´I", "Í").replace("´o", "ó").replace("´O", "Ó").replace("´u", "ú").replace("´U", "Ú")
    texto = texto.replace("ˆa", "â").replace("ˆA", "Â").replace("ˆe", "ê").replace("ˆE", "Ê").replace("ˆı", "î").replace("ˆI", "Î").replace("ˆo", "ò").replace("ˆO", "Ô").replace("ˆu", "û").replace("ˆU", "Û")
    texto = texto.replace("˜a", "ã").replace("˜o", "õ").replace("˜A", "Ã").replace("˜O", "Õ")
    texto = texto.replace("˘g", "ğ")
    return texto


def ler_transformar_pdf(link_pdf:str, ano_evento:int) -> list:
    anais = []
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
        resumo = ''
        flag = False
        
        if text.find("Abstract.") != -1:         
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            texto_base = transformar_texto(span["text"])
                            font_name = span["font"]
                            font_size = span["size"]
                            #print(f"Texto: '{texto_base}', Fonte: {font_name}, Tamanho: {font_size}")
                            if font_size >= 15 and len(texto_base) > 2:
                                nomes_artigos += texto_base + ' '
                                flag = True
                                continue
                            if font_name == 'NimbusRomNo9L-Medi' and flag and len(texto_base) > 2:
                                autores += texto_base + ' '
                            if font_name == 'NimbusRomNo9L-Regu' and flag and len(texto_base) > 2:
                                universidades += texto_base + ' '
                            if font_name == 'NimbusMonL-Regu' and texto_base.find('@') != -1 and len(texto_base) > 2:
                                flag = False

            abstract = text.split("Abstract.", 1)[-1]
            if text.find("Resumo.") != -1:
                lingua = 'Pt'
                resumo = text.split("Resumo.", 1)[-1]
                resumo = resumo.split("1.", 1)[0].strip()
            else:
                lingua = 'En'
                resumo = abstract.split("1.", 1)[0].strip()
            
            dados_anais_com_ano = {
                "titulo": nomes_artigos.strip(),
                "paginas": int(page_num+1),
                "autores": autores.replace(" , ", ", ").strip(),
                "universidade": universidades.strip(),
                "lingua": lingua,
                "resumo": resumo.replace("-\n", "").replace("\n", " ").strip(),
                "link": ""
            }
            if len(anais) > 0:
                anais[-1]['paginas'] = dados_anais_com_ano['paginas']-anais[-1]['paginas']
            anais.append(dados_anais_com_ano)
    anais[-1]['paginas'] = len(pdf_document)-anais[-1]['paginas']
    return anais