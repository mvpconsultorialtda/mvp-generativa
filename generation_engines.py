# generation_engines.py
# Motores de geração de texto e imagem (exemplo genérico)
import os
from openai import OpenAI
from BingImageCreator import ImageGen

# --- TEXTO: OpenRouter/Mistral ---
MODELO_TEXTO_PADRAO = os.getenv("MODELO_TEXTO_PADRAO", "mistralai/mistral-7b-instruct:free")

def gerar_texto(prompt: str, modelo: str, temperatura: float, api_key: str) -> str:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    response = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperatura,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# --- IMAGEM: Bing Image Creator ---
def gerar_imagem(prompt: str, bing_cookie: str, bing_cookie_srch: str) -> list:
    image_gen = ImageGen(auth_cookie=bing_cookie, auth_cookie_SRCHHPGUSR=bing_cookie_srch, quiet=True)
    links = image_gen.get_images(prompt)
    return links if links else []
