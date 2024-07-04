import openai

def summarize(text):
    messages = [
        {"role": "system", "content": "Eres un asistente inteligente y tu tarea es resumir en 2 frases el texto que te pase el usuario"}
    ]
    messages.append({"role": "user", "content": text})
    chat = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    answer = chat.choices[0].message.content
    return answer

def translate(text):
    messages = [
        {"role": "system", "content": "Eres un asistente inteligente y tu tarea es traducir al español el texto que te pase el usuario"}
    ]
    messages.append({"role": "user", "content": text})
    chat = openai.chat.completions.create(model="gpt-4", messages=messages)
    answer = chat.choices[0].message.content
    return answer
