import re

pattern = r'^Artículo (\S+)\.(.*)$'

def eliminar_encabezado(text):
    text = text.replace('CODIGO DE PROPIEDAD HORIZONTAL', '')
    modified_text = re.sub(pattern, '', text)
    return " ".join(modified_text.split())

def split_text_by_length(text, max_length=8192):
    text = text[0]
    chunks = []
    current_chunk = []

    for sentence in text.split('.'):
        if current_chunk and len('.'.join(current_chunk)) + len(sentence) + 1 <= max_length:
            current_chunk.append(sentence.strip())
        else:
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence.strip()]

    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return chunks
