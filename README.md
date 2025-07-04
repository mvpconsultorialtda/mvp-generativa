Entendido! A solicitação é para transformar a API em uma ferramenta completamente geral, removendo qualquer contexto de jogo e focando em sua função principal: gerar texto e imagens a partir de prompts.
Ajustei todo o projeto para refletir essa nova identidade. Os "templates de prompt" foram mantidos, mas agora são exemplos genéricos e úteis, como "resumir texto" ou "escrever uma história", em vez de "criar evento de jogo".
Aqui está a nova estrutura, completamente generalizada.
Estrutura do Projeto (Geral)
generation_engines.py: O motor de geração (OpenAI/Bing). Nenhuma alteração necessária aqui, pois ele já era genérico.
prompt_templates.py: Este arquivo foi completamente reimaginado. Em vez de prompts de jogo, ele agora contém templates genéricos e úteis que demonstram o poder da API.
api.py: O arquivo principal da API, com todo o texto, descrições e exemplos ajustados para um contexto geral.
.env e requirements.txt: Permanecem os mesmos.
Passo 1: requirements.txt e .env
Estes arquivos não mudam. Garanta que eles existam e estejam configurados como antes.
Passo 2: Motores de Geração (generation_engines.py)
Este arquivo permanece inalterado. Ele é o coração técnico e já está pronto para uso geral. Você pode usar o código da resposta anterior sem modificações.
Passo 3: Templates de Prompt (prompt_templates.py) - Versão Generalizada
Este arquivo foi completamente reescrito para remover a lógica do jogo e fornecer templates úteis em um contexto geral.
Generated python
# prompt_templates.py

def format_summary_prompt(text_to_summarize: str) -> str:
    """Formata um prompt para resumir um bloco de texto."""
    return f"Please provide a concise summary of the following text:\n\n---\n{text_to_summarize}\n---\n\nSummary:"

def format_creative_writing_prompt(topic: str, style: str) -> str:
    """Formata um prompt para escrita criativa com base em um tópico e estilo."""
    return f"Write a {style} about the following topic: {topic}. Be creative and engaging."

def format_json_extraction_prompt(text_to_parse: str, fields: list) -> str:
    """Formata um prompt para extrair dados de um texto para um formato JSON."""
    fields_str = ", ".join([f'"{field}"' for field in fields])
    return f"""From the text below, extract the following fields: {fields_str}.
Return ONLY a valid JSON object with these fields. If a field is not found, use null.

Text: "{text_to_parse}"

JSON Output:
"""

# --- Registro Central de Templates Genéricos ---
PROMPT_TEMPLATES = {
    "summarize": {
        "function": format_summary_prompt,
        "description": "Resume um bloco de texto fornecido.",
        "required_args": ["text_to_summarize"],
        "example_args": { "text_to_summarize": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by humans and other animals. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of successfully achieving its goals." }
    },
    "creative_writing": {
        "function": format_creative_writing_prompt,
        "description": "Escreve uma peça criativa (ex: poema, conto) sobre um tópico em um determinado estilo.",
        "required_args": ["topic", "style"],
        "example_args": { "topic": "a lonely lighthouse on a distant planet", "style": "short story" }
    },
    "extract_json": {
        "function": format_json_extraction_prompt,
        "description": "Extrai informações específicas de um texto e as retorna em formato JSON.",
        "required_args": ["text_to_parse", "fields"],
        "example_args": { "text_to_parse": "Event: AI Conference 2024, Location: Lisbon, Date: October 26th.", "fields": ["Event", "Location", "Date"] }
    }
}
Use code with caution.
Python
Passo 4: A API (api.py) - Versão Generalizada
A API foi ajustada para refletir sua nova natureza geral. As mudanças incluem: títulos, descrições, nomes de endpoints e todos os exemplos.
Generated python
# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, Any

import generation_engines
import prompt_templates

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
        modelo_a_usar = request.modelo or generation_engines.MODELO_TEXTO_PADRAO
        texto_gerado = generation_engines.gerar_texto(prompt=final_prompt, modelo=modelo_a_usar, temperatura=request.temperatura)
        return {"generated_text": texto_gerado}
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Serviço Indisponível: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Interno do Servidor: {e}")

@app.post("/generate/image", summary="Gerar Imagem", description="Gera imagens com base em uma descrição textual.")
async def create_image(request: ImageGenerationRequest):
    try:
        urls_imagens = generation_engines.gerar_imagem(prompt=request.prompt)
        if not urls_imagens:
             raise HTTPException(status_code=404, detail="Nenhuma imagem foi gerada. O prompt pode ter sido bloqueado ou houve um problema no serviço de origem.")
        return {"image_urls": urls_imagens}
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Serviço Indisponível: {e}")
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=f"Não Autorizado: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Interno do Servidor: {e}")
Use code with caution.
Python
Como Executar e Usar a API Geral
Inicie o servidor:
uvicorn api:app --reload
Acesse a Documentação: Abra http://127.0.0.1:8000/docs para ver a nova interface, com exemplos e descrições genéricas.
Exemplos de Uso (com curl):
Gerar texto com prompt direto:
Generated bash
curl -X 'POST' 'http://127.0.0.1:8000/generate/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique o conceito de computação quântica para um leigo."
  }'
Use code with caution.
Bash
Gerar texto usando o template summarize:
Generated bash
curl -X 'POST' 'http://127.0.0.1:8000/generate/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "template_name": "summarize",
    "template_args": {
      "text_to_summarize": "A Revolução Industrial foi a transição para novos processos de manufatura na Grã-Bretanha, Europa continental e Estados Unidos, no período de cerca de 1760 a algum momento entre 1820 e 1840. Essa transição incluiu a passagem de métodos de produção manuais para máquinas, novos processos de fabricação de produtos químicos e produção de ferro, o uso crescente de energia a vapor e energia hidráulica, o desenvolvimento de máquinas-ferramenta e a ascensão do sistema de fábrica mecanizada."
    }
  }'
Use code with caution.
Bash
Gerar imagem:
Generated bash
curl -X 'POST' 'http://127.0.0.1:8000/generate/image' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "um robô vintage lendo um livro em uma biblioteca empoeirada, pintura a óleo digital"
  }'
