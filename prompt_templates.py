def format_summary_prompt(text_to_summarize: str) -> str:
    """Formata um prompt para resumir um bloco de texto."""
    return f"Please provide a concise summary of the following text:\n\n---\n{text_to_summarize}\n---\n\nSummary:"

def format_creative_writing_prompt(topic: str, style: str) -> str:
    """Formata um prompt para escrita criativa com base em um tópico e estilo."""
    return f"Write a {style} about the following topic: {topic}. Be creative and engaging."

def format_json_extraction_prompt(text_to_parse: str, fields: list) -> str:
    """Formata um prompt para extrair dados de um texto para um formato JSON."""
    fields_str = ", ".join([f'\"{field}\"' for field in fields])
    return f"""From the text below, extract the following fields: {fields_str}.
Return ONLY a valid JSON object with these fields. If a field is not found, use null.

Text: \"{text_to_parse}\"\n\nJSON Output:\n"""

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
