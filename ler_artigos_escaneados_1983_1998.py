# Código desenvolvido por Ricardo Reis

import pdf2image as img
import pymupdf as f
import pytesseract
import requests

url_pdf = "https://ce-resd.sbc.org.br/sbrc/1993/p01.pdf"
# def ler_transformar_pdf(link_pdf:str) -> list:
anais = []
pdf_dados = requests.get(url_pdf)
pdf_dados.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
pdf_doc = f.open(stream=pdf_dados.content, filetype="pdf")
pdf_bytes = pdf_doc.tobytes()
pdf_images = img.convert_from_bytes(pdf_bytes, fmt="PNG")

lingua = ""
resumo = ""
abstract = ""
paginas = len(pdf_doc)
outro = ""
referencias = ""
flag_ref = False

texto_dividido = ''
for i, pagina in enumerate(pdf_images):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ricar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    texto_extraido = pytesseract.image_to_string(pagina, lang='por')
    #print(texto_extraido)
    #print("Transcrição concluída.")

    texto_dividido = texto_extraido
    if (texto_extraido.find("Resumo") != -1 or texto_extraido.find("Sumário") != -1 or texto_extraido.find("Abstract") != -1) and i<2:
        if texto_extraido.find("Resumo") != -1:
            texto_dividido = texto_extraido.split("Resumo", 1)[-1]
        if texto_extraido.find("Sumário") != -1:
            texto_dividido = texto_extraido.split("Sumário", 1)[-1]
        
        abstract = texto_dividido.split("Abstract",1)[-1].strip()
        resumo = texto_dividido.split("Abstract",1)[0].strip()
        
        if texto_extraido.find("Resumo") != -1 or texto_extraido.find("Sumário") != -1:
            if lingua == '' or lingua == 'En':
                lingua = 'Pt'
        else:
            if lingua == '':
                lingua = 'En'
                
        if i == 0:
            outro = texto_dividido[0:-1].strip()
    
    if (texto_extraido.find("Referência") != -1 or texto_extraido.find("Reference") != -1 or flag_ref) and i > 1:
        if texto_extraido.find("Referências") != -1:
            texto_dividido = texto_extraido.split("Referências", 1)[-1]
            flag_ref = True
        elif texto_extraido.find("Referência") != -1:
            texto_dividido = texto_extraido.split("Referência", 1)[-1]
            flag_ref = True
        if texto_extraido.find("References") != -1:
            texto_dividido = texto_extraido.split("References", 1)[-1]
            flag_ref = True
        elif texto_extraido.find("References") != -1:
            texto_dividido = texto_extraido.split("Reference", 1)[-1]
            flag_ref = True
        
        referencias += texto_dividido.strip() + '\n'
            
print(f"Resumo: {resumo}")
print(f"Abstract: {abstract}") 
print(f"Língua: {lingua}")
print(f"Páginas: {paginas}")
print(f"Referências: {referencias}")
print(f"Outro: {outro}")