import fitz
import re

def process_pdf(pdf_path, lista_instituciones):
    diccionario_leyes = {}
    with fitz.open(pdf_path) as doc:
        for page_num in range(16, len(doc)):
            page = doc[page_num]
            text = page.get_text('text')
            if text.startswith('§'):
                lines = text.split('\n')
                for idx, text in enumerate(lines):
                    for institucion in lista_instituciones:
                        if institucion in text:
                            for idx_2, text in enumerate(lines[idx:]):
                                if 'Referencia: BOE-' in text:
                                    dict_key = " ".join(lines[1:idx]).replace("  ", " ")
                                    diccionario_leyes[dict_key] = lines[idx:][idx_2+1:]
            else:
                lines = text.split('\n')
                diccionario_leyes[dict_key] += lines[2:-4]

    pattern = r'^Artículo (\S+)\.(.*)$'
    for ley in list(diccionario_leyes.keys()):
        lineas = diccionario_leyes[ley]
        diccionario_matches = {}
        contenido_entre_matches = ""
        ultimo_match = None

        for l in lineas:
            match = re.match(pattern, l)
            if match:
                if ultimo_match:
                    diccionario_matches[ultimo_match] = contenido_entre_matches.strip()
                
                ultimo_match = match.group(0)
                contenido_entre_matches = ""
            else:
                contenido_entre_matches += l

        if ultimo_match:
            diccionario_matches[ultimo_match] = contenido_entre_matches.strip()
        
        diccionario_leyes[ley] = diccionario_matches

    return diccionario_leyes
