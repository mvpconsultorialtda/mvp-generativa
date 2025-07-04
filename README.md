# Como Usar a API de Geração de Texto e Imagem

Esta API permite gerar textos e imagens a partir de prompts diretos ou templates prontos. Veja abaixo como realizar requisições para cada funcionalidade.

## 1. Estrutura do arquivo .env

No arquivo `.env` na raiz do projeto, adicione suas chaves de API seguindo o padrão abaixo:

```
# Chaves para geração de texto
TEXTO_KEY_1=chave_texto_1
TEXTO_KEY_2=chave_texto_2
...
TEXTO_KEY_50=chave_texto_50

# Chaves para geração de imagem
IMAGEM_KEY_1=chave_imagem_1
IMAGEM_KEY_2=chave_imagem_2
...
IMAGEM_KEY_50=chave_imagem_50
```

Cada chave deve ser fornecida pelo serviço de IA que você utiliza (ex: OpenAI, Azure, etc). O sistema faz a rotação automática dessas chaves.

---

## 2. Iniciando o servidor

Execute o comando abaixo no terminal para iniciar a API:

```bash
uvicorn api:app --reload
```

Acesse a documentação interativa em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 3. Gerar texto

Você pode gerar texto de duas formas:

### a) Usando um prompt direto

```bash
curl -X POST 'http://127.0.0.1:8000/generate/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique o conceito de computação quântica para um leigo."
  }'
```

### b) Usando um template de prompt

Primeiro, consulte os templates disponíveis:

```bash
curl -X GET 'http://127.0.0.1:8000/templates/text'
```

Depois, envie uma requisição usando o nome do template e os argumentos necessários:

```bash
curl -X POST 'http://127.0.0.1:8000/generate/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "template_name": "summarize",
    "template_args": {
      "text_to_summarize": "A Revolução Industrial foi a transição para novos processos de manufatura..."
    }
  }'
```

---

## 4. Gerar imagem

Envie um prompt descritivo para gerar uma imagem:

```bash
curl -X POST 'http://127.0.0.1:8000/generate/image' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "um robô vintage lendo um livro em uma biblioteca empoeirada, pintura a óleo digital"
  }'
```

A resposta trará uma lista de URLs de imagens geradas.

---

## 5. Observações
- Consulte `/docs` para exemplos interativos e documentação detalhada dos parâmetros.
- Para usar templates, sempre confira os argumentos obrigatórios usando o endpoint `/templates/text`.
- Os endpoints retornam mensagens de erro detalhadas caso algum parâmetro esteja incorreto ou ausente.
