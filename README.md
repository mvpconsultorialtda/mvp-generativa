# Como Usar a API de Geração de Texto e Imagem

Esta API permite gerar textos e imagens a partir de prompts diretos ou templates prontos, utilizando provedores reais como OpenRouter/Mistral para texto e Bing Image Creator para imagens. Veja abaixo como estruturar o .env e realizar requisições.

---

## Utilizando a API em Produção (Vercel, Render, etc.)

Ao fazer o deploy desta API em plataformas como Vercel, Render ou outros serviços de nuvem, você torna possível consumir os endpoints de geração de texto e imagem de qualquer lugar, seja de aplicações web, mobile, automações, chatbots ou outros sistemas.

### Vantagens de ter a API deployada:
- **Acesso global:** Permite que qualquer sistema autorizado envie requisições HTTP para gerar textos ou imagens sob demanda.
- **Integração fácil:** Pode ser consumida por frontends (React, Vue, Angular), apps mobile (Flutter, React Native), scripts Python, automações no Zapier, Make, etc.
- **Escalabilidade:** O serviço pode ser escalado conforme o volume de requisições, aproveitando a infraestrutura da nuvem.
- **Centralização:** Todas as regras de rotação de chaves, templates e controle de uso ficam centralizadas, facilitando manutenção e segurança.

### Exemplos de uso após deploy

Se sua API está publicada em `https://minha-api.vercel.app` ou `https://minha-api.onrender.com`, basta trocar a URL base nos exemplos:

```bash
curl -X POST 'https://minha-api.vercel.app/generate/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique o conceito de computação quântica para um leigo."
  }'
```

Ou para imagens:

```bash
curl -X POST 'https://minha-api.onrender.com/generate/image' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "um robô vintage lendo um livro em uma biblioteca empoeirada, pintura a óleo digital"
  }'
```

Você pode consumir a API de qualquer ambiente que consiga fazer requisições HTTP, inclusive navegadores, servidores, automações e integrações de terceiros.

---

## 1. Estrutura do arquivo .env

No arquivo `.env` na raiz do projeto, adicione suas chaves de API seguindo o padrão abaixo:

```
# Chaves para geração de texto (OpenRouter/Mistral)
MISTRALAI_MISTRAL_7B_INSTRUCT_FREE_KEY_1=sua_chave_1
MISTRALAI_MISTRAL_7B_INSTRUCT_FREE_KEY_2=sua_chave_2
# ...até N

# Chaves para geração de imagem (Bing Image Creator)
BING_AUTH_COOKIE_1=valor_cookie1
BING_AUTH_COOKIE_SRCHHPGUSR_1=valor_cookie_srch1
BING_AUTH_COOKIE_2=valor_cookie2
BING_AUTH_COOKIE_SRCHHPGUSR_2=valor_cookie_srch2
# ...até N
```

- Para texto, cada chave corresponde a uma conta/modelo do OpenRouter/Mistral.
- Para imagem, cada par de cookies corresponde a uma conta Bing válida.
- O sistema faz a rotação automática dessas chaves e bloqueia temporariamente as que apresentarem erro.

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
curl -X POST 'https://minha-api.vercel.app/generate/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explique o conceito de computação quântica para um leigo."
  }'
```

### b) Usando um template de prompt

Primeiro, consulte os templates disponíveis:

```bash
curl -X GET 'https://minha-api.vercel.app/templates/text'
```

Depois, envie uma requisição usando o nome do template e os argumentos necessários:

```bash
curl -X POST 'https://minha-api.vercel.app/generate/text' \
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
curl -X POST 'https://minha-api.vercel.app/generate/image' \
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
- O sistema faz rotação automática das chaves e bloqueio temporário das que apresentarem erro, garantindo robustez e alta disponibilidade.
