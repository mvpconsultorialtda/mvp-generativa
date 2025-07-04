# generation_engines.py
# Motores de geração de texto e imagem (exemplo genérico)
import os
from openai import OpenAI
from BingImageCreator import ImageGen
import traceback
from datetime import datetime

# --- TEXTO: OpenRouter/Mistral ---
MODELO_TEXTO_PADRAO = os.getenv("MODELO_TEXTO_PADRAO", "mistralai/mistral-7b-instruct:free")

LOG_TEXTO = "log_text_generation.log"
LOG_IMAGEM = "log_image_generation.log"

def log_event(logfile, msg):
    with open(logfile, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def gerar_texto(prompt: str, modelo: str, temperatura: float, api_key: str) -> str:
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        response = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperatura,
            max_tokens=500
        )
        result = response.choices[0].message.content.strip()
        log_event(LOG_TEXTO, f"SUCESSO | Modelo: {modelo} | Prompt: {prompt[:100]}... | Resultado: {result[:100]}...")
        return result
    except Exception as e:
        tb = traceback.format_exc()
        log_event(LOG_TEXTO, f"ERRO | Modelo: {modelo} | Prompt: {prompt[:100]}... | Erro: {e}\n{tb}")
        raise

# --- IMAGEM: Bing Image Creator ---
def gerar_imagem(prompt: str, bing_cookie: str, bing_cookie_srch: str) -> list:
    try:
        image_gen = ImageGen(auth_cookie=bing_cookie, auth_cookie_SRCHHPGUSR=bing_cookie_srch, quiet=True)
        links = image_gen.get_images(prompt)
        if links:
            log_event(LOG_IMAGEM, f"SUCESSO | Prompt: {prompt[:100]}... | Links: {links}")
        else:
            log_event(LOG_IMAGEM, f"FALHA | Prompt: {prompt[:100]}... | Nenhum link retornado.")
        return links if links else []
    except Exception as e:
        tb = traceback.format_exc()
        log_event(LOG_IMAGEM, f"ERRO | Prompt: {prompt[:100]}... | Erro: {e}\n{tb}")
        raise
