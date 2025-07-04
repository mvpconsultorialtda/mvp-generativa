from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, Any

import generation_engines
import prompt_templates
from key_manager import KeyManager

# --- Modelos de Dados Pydantic ---

class TextGenerationRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="O texto base para a geração de conteúdo (use este campo OU um template).", example="Qual a diferença entre machine learning e deep learning?")
    template_name: Optional[str] = Field(None, description="Nome do template de prompt a ser usado (ex: 'summarize').", example="creative_writing")
    template_args: Optional[Dict[str, Any]] = Field(None, description="Dicionário com os argumentos necessários para o template.", example={'topic': 'a city on the clouds', 'style': 'poem'})
    
    modelo: Optional[str] = Field(None, description="Modelo de IA a ser usado (opcional, usa o padrão do .env).", example="mistralai/mistral-large")
    temperatura: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Nível de criatividade da resposta (0.0 a 2.0).")

    @root_validator(pre=True)
    def check_prompt_or_template(cls, values):
        if 'prompt' in values and values.get('prompt') is not None:
            if 'template_name' in values and values.get('template_name') is not None:
                raise ValueError("Forneça 'prompt' ou 'template_name', mas não ambos.")
            return values
        if 'template_name' in values and values.get('template_name') is not None:
            return values
        raise ValueError("É necessário fornecer um 'prompt' ou um 'template_name'.")

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="A descrição da imagem a ser gerada.", example="A photo of a cyberpunk cat wearing neon glasses on a rainy Tokyo street, photorealistic.")

# --- Inicialização da API ---
app = FastAPI(
    title="API Genérica de Geração de Conteúdo",
    description="Uma API versátil para gerar texto e imagens usando diferentes motores de IA. Suporta prompts diretos e templates reutilizáveis.",
    version="2.0.0"
)

# --- Endpoints da API ---

@app.get("/", summary="Status da API", include_in_schema=False)
def read_root():
    return {"status": "online", "message": "Bem-vindo à API de Geração de Conteúdo! Acesse /docs para a documentação."}

@app.get("/templates/text", summary="Listar Templates de Texto", description="Retorna uma lista de todos os templates de prompt de texto disponíveis.")
def list_text_templates():
    return {
        name: {
            "description": data["description"],
            "required_args": data["required_args"],
            "example_args": data["example_args"]
        } for name, data in prompt_templates.PROMPT_TEMPLATES.items()
    }

@app.post("/generate/text", summary="Gerar Texto", description="Gera texto a partir de um prompt direto ou usando um template.")
async def create_text(request: TextGenerationRequest):
    final_prompt = ""
    if request.prompt:
        final_prompt = request.prompt
    elif request.template_name:
        template_info = prompt_templates.PROMPT_TEMPLATES.get(request.template_name)
        if not template_info:
            raise HTTPException(status_code=404, detail=f"Template '{request.template_name}' não encontrado.")
        required_args = template_info["required_args"]
        if not request.template_args or not all(arg in request.template_args for arg in required_args):
            raise HTTPException(status_code=422, detail=f"Argumentos faltando para o template '{request.template_name}'. Requer: {required_args}")
        try:
            final_prompt = template_info["function"](**request.template_args)
        except TypeError as e:
            raise HTTPException(status_code=422, detail=f"Erro nos argumentos para o template: {e}")
    try:
        # Gerenciamento de chave de texto para Mistral
        key_manager = KeyManager('MISTRALAI_MISTRAL_7B_INSTRUCT_FREE_KEY')
        key_tuple = key_manager.get_next_key()
        if not key_tuple:
            raise HTTPException(status_code=503, detail="Nenhuma chave de texto disponível no momento.")
        key_name, key_value = key_tuple
        modelo_a_usar = request.modelo or generation_engines.MODELO_TEXTO_PADRAO
        texto_gerado = generation_engines.gerar_texto(prompt=final_prompt, modelo=modelo_a_usar, temperatura=request.temperatura, api_key=key_value)
        return {"generated_text": texto_gerado, "key_used": key_name}
    except ConnectionError as e:
        if 'key_name' in locals():
            key_manager.block_key(key_name)
        raise HTTPException(status_code=503, detail=f"Serviço Indisponível: {e}")
    except Exception as e:
        if 'key_name' in locals():
            key_manager.block_key(key_name)
        raise HTTPException(status_code=500, detail=f"Erro Interno do Servidor: {e}")

@app.post("/generate/image", summary="Gerar Imagem", description="Gera imagens com base em uma descrição textual.")
async def create_image(request: ImageGenerationRequest):
    try:
        # Gerenciamento de chave de imagem para Bing
        key_manager = KeyManager('BING_AUTH_COOKIE')
        key_tuple = key_manager.get_next_key()
        if not key_tuple:
            raise HTTPException(status_code=503, detail="Nenhuma chave de imagem disponível no momento.")
        cookie1_name, cookie1, cookie2_name, cookie2 = key_tuple
        urls_imagens = generation_engines.gerar_imagem(prompt=request.prompt, bing_cookie=cookie1, bing_cookie_srch=cookie2)
        if not urls_imagens:
             raise HTTPException(status_code=404, detail="Nenhuma imagem foi gerada. O prompt pode ter sido bloqueado ou houve um problema no serviço de origem.")
        return {"image_urls": urls_imagens, "key_used": cookie1_name}
    except ConnectionError as e:
        if 'cookie1_name' in locals():
            key_manager.block_key(cookie1_name)
        raise HTTPException(status_code=503, detail=f"Serviço Indisponível: {e}")
    except PermissionError as e:
        if 'cookie1_name' in locals():
            key_manager.block_key(cookie1_name)
        raise HTTPException(status_code=401, detail=f"Não Autorizado: {e}")
    except Exception as e:
        if 'cookie1_name' in locals():
            key_manager.block_key(cookie1_name)
        raise HTTPException(status_code=500, detail=f"Erro Interno do Servidor: {e}")
