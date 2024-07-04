import streamlit as st
import pandas as pd
import os
from app.utils import eliminar_encabezado, split_text_by_length
from app.pdf_processing import process_pdf
from app.openai_helpers import summarize, translate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI, ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

# Cargar el archivo PDF
pdf_fuente = os.path.join("data", "codigo_propiedad_horizontal.pdf")

# Lista de instituciones
lista_instituciones = [
    'Jefatura del Estado', 'Comunidad Autónoma de Cataluña', 'Ministerio de Gracia y Justicia',
    'Ministerio de Justicia', 'Ministerio de Sanidad y Consumo', 'Ministerio de la Vivienda',
    'Presidencia del Gobierno', 'Ministerio de Fomento', 
    'Ministerio de la Presidencia, Relaciones con las Cortes y Memoria Democrática',
    'Ministerio de Industria, Turismo y Comercio', 'Ministerio de Transportes, Turismo y Comunicaciones',
    'Ministerio de Relaciones con las Cortes y de la Secretaría del Gobierno',
    'Ministerio de Transportes y Movilidad Sostenible', 'Ministerio de Hacienda',
    'Ministerio de Trabajo y Seguridad Social', 'Ministerio de Empleo y Seguridad Social'
]

# Procesar el PDF
diccionario_leyes = process_pdf(pdf_fuente, lista_instituciones)

# Crear el DataFrame
rows = [(ley, articulo, texto)
        for ley, sub_dict in diccionario_leyes.items()
        for articulo, texto in sub_dict.items()]

df = pd.DataFrame(rows, columns=['ley', 'articulo', 'texto'])
df['articulo'] = df['articulo'].apply(lambda x: x.split('.')[0].lower())
df['texto'] = df['texto'].apply(lambda x: [eliminar_encabezado(x)])
df['long_texto'] = df['texto'].apply(lambda x: len(x[0]))
df.loc[df['long_texto'] > 8192, 'texto'] = df[df['long_texto'] > 8192]['texto'].apply(split_text_by_length)
df = df.explode('texto', ignore_index=True)
df['identificador'] = df['ley'] + ', ' + df['articulo']
df = df[~df['texto'].str.contains('derogado')]
# df['resumen'] = df['texto'].apply(lambda x: summarize(x))

# Crear embeddings
chunks = list(df['texto'].values)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# Crear la base de datos Chroma
# docs = [Document(page_content=text, metadata={'source':df['identificador'].iloc[i], 'summary':df['resumen'].iloc[i]}) for i, text in enumerate(chunks)]
# db = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db/chroma_db_experto_resumen")
db = Chroma(persist_directory="chroma_db/chroma_db_experto_resumen", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={'k': 5})
llm = ChatOpenAI(model="gpt-4")

# Definir el prompt template
prompt_template = PromptTemplate.from_template(
    """Eres la administradora de una finca y tu deber es responder a las dudas legales que tengan los inquilinos de la finca, justificando tu respuesta con la Ley y el artículo en el que te has basado, presentes en los metadatos de los documentos recuperados.
    Debes generar la respuesta basándote solamente en la información proporcionada a continuación
    {documento1}, {documento2}, {documento3}, {documento4}, {documento5}. Si no hay información relevante en los documentos, indica que no dispones de la respuesta.
    Pregunta del inquilino
    {question}."""
)

memory_chain = prompt_template | llm | StrOutputParser()

def generate_response(input_text):
    documentos = retriever.invoke(input_text)
    response = memory_chain.invoke({
        'documento1': documentos[0],
        'documento2': documentos[1],
        'documento3': documentos[2],
        'documento4': documentos[3],
        'documento5': documentos[4],
        'question': input_text
    })
    st.info(response)
    return documentos

# Configurar Streamlit
st.title("Chatbot sobre el Código de la Propiedad horizontal")

with st.form('my_form'):
    text = st.text_area('Escribe tu pregunta:', '')
    submitted = st.form_submit_button('Enviar')
    if submitted:
        documentos = generate_response(text)