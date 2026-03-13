# yt-summarizer

**Resumidor de videos de YouTube con IA — Serverless en AWS**

GitHub: https://github.com/EmmaLedesma/youtube-summarizer

[![AWS](https://img.shields.io/badge/AWS-us--east--1-orange)](https://aws.amazon.com)
[![Terraform](https://img.shields.io/badge/terraform-1.14+-purple)](https://terraform.io)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![Bedrock](https://img.shields.io/badge/AWS_Bedrock-Claude_3.5_Haiku-teal)](https://aws.amazon.com/bedrock/)

---

## 📌 Problema que Resuelve

Seguir el ritmo de clases, conferencias y tutoriales en video lleva tiempo. Este proyecto nació de una necesidad real: poder resumir videos de YouTube en segundos, extrayendo los puntos clave sin ver el video completo.

La solución es una aplicación serverless end-to-end en AWS: el usuario pega una URL, elige el idioma del resumen, y Claude AI (via AWS Bedrock) devuelve un resumen estructurado con puntos clave, tópicos y tipo de contenido. Los resultados se cachean en DynamoDB para no repetir llamadas a la IA.

---

## 🏗️ Arquitectura

```
Browser
  │
  ├─ Supadata API ──────────────────► transcript text
  │  (IP residencial del usuario,
  │   evita bloqueos de YouTube)
  │
  └─ POST { videoId, transcriptText, language }
          │
          ▼
    API Gateway (REST)
          │
          ▼
    Lambda (Python 3.12)
          │
          ├─ DynamoDB.query()  ──► caché hit → respuesta inmediata
          │
          └─ Bedrock (Claude 3.5 Haiku)
                    │
                    └─ DynamoDB.putItem() → guarda resultado
                    └─ response → Browser

Frontend estático: S3 + CloudFront (OAC, HTTPS, SPA fallback)
Infraestructura: 100% Terraform (módulos locales)
```

### Flujo Detallado

```
[Usuario pega URL + elige idioma]
        │
        ▼
[Browser extrae transcript via Supadata API]
        │
        ▼
[Lambda verifica caché en DynamoDB]
        │
        ├──► [Caché hit] → respuesta en < 500ms
        │
        └──► [Caché miss] → Bedrock Claude 3.5 Haiku
                                    │
                                    └──► Guarda en DynamoDB (TTL 90 días)
                                    └──► Respuesta al browser
```

---

## 🚀 Recursos AWS Provisionados

| Recurso | Nombre | Módulo Terraform |
|---------|--------|-----------------|
| Lambda Function | `yt-summarizer-dev-summarizer` | lambda |
| IAM Role | `yt-summarizer-dev-summarizer-role` | lambda |
| CloudWatch Log Group | `/aws/lambda/yt-summarizer-dev-summarizer` | lambda |
| API Gateway REST API | `yt-summarizer-dev-api` | api-gateway |
| DynamoDB Table | `yt-summarizer-dev-summaries` | dynamodb |
| S3 Bucket (frontend) | `yt-summarizer-dev-frontend` | storage |
| CloudFront Distribution | `E16INCGHSKTQTT` | storage |
| CloudFront OAC | `yt-summarizer-dev-oac` | storage |
| Secrets Manager | `yt-summarizer/dev/supadata-key` | — |

**Total: 9 recursos principales en AWS**

---

## ✅ Features Implementadas

- **Resumen estructurado con IA** — resumen ejecutivo, puntos clave detallados, tópicos y tipo de contenido
- **Selector de idioma** — el usuario elige el idioma del resumen (Español, English, Português, y más)
- **Caché inteligente** — DynamoDB guarda resultados 90 días con TTL automático
- **Frontend responsivo** — S3 + CloudFront con HTTPS, OAC y SPA fallback
- **Progress steps** — UI que muestra el estado de cada etapa del proceso
- **Historial de sesión** — los videos resumidos en la sesión quedan accesibles

---

## 🛠️ Stack Técnico

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML + CSS + Vanilla JS |
| CDN / Hosting | Amazon CloudFront + S3 |
| API | Amazon API Gateway (REST) |
| Compute | AWS Lambda (Python 3.12) |
| IA | AWS Bedrock — Claude 3.5 Haiku |
| Base de datos | Amazon DynamoDB (PAY_PER_REQUEST) |
| Transcript | Supadata API (browser-side) |
| IaC | Terraform 1.14 — módulos locales |
| Secretos | AWS Secrets Manager |

---

## 📁 Estructura del Proyecto

```
youtube-summarizer/
├── terraform/
│   ├── main.tf                    # Provider + módulos
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── lambda/                # Lambda + IAM + CloudWatch
│       ├── api-gateway/           # REST API + CORS
│       ├── dynamodb/              # Tabla + TTL + PITR
│       └── storage/               # S3 + CloudFront (OAC)
│
├── backend/
│   └── summarizer/
│       ├── handler.py             # Lambda handler
│       ├── bedrock_client.py      # Cliente Bedrock (Converse API)
│       ├── transcript.py          # Módulo transcript (legacy)
│       ├── requirements.txt
│       └── build.ps1              # Script de empaquetado ZIP
│
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js                     # Supadata + fetch a Lambda
```

---

## ⚡ Quick Start

### Requisitos
- Terraform >= 1.14
- AWS CLI configurado
- Python 3.12
- Cuenta en [Supadata](https://supadata.ai) (plan gratuito — 100 req/mes)

### 1. Clonar y configurar

```bash
git clone https://github.com/EmmaLedesma/youtube-summarizer
cd youtube-summarizer
```

### 2. Configurar variables

```hcl
# terraform/terraform.tfvars
aws_region  = "us-east-1"
aws_profile = "tu-perfil"
project_name = "yt-summarizer"
environment  = "dev"
```

### 3. Deploy de infraestructura

```bash
cd terraform
terraform init
terraform apply
```

### 4. Build y deploy de la Lambda

```powershell
cd backend/summarizer
powershell -ExecutionPolicy Bypass -File build.ps1

aws lambda update-function-code \
  --function-name yt-summarizer-dev-summarizer \
  --zip-file fileb://summarizer.zip
```

### 5. Deploy del frontend

```bash
aws s3 sync frontend/ s3://yt-summarizer-dev-frontend --delete

aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

### 6. Configurar la API key de Supadata

```bash
aws secretsmanager create-secret \
  --name "yt-summarizer/dev/supadata-key" \
  --secret-string '{"supadata_api_key":"tu-key"}'
```

---

## 🔐 Seguridad

- **Least privilege IAM** — Lambda solo puede invocar Bedrock, leer/escribir su tabla DynamoDB y leer su secret
- **S3 privado** — bucket del frontend sin acceso público, solo CloudFront via OAC
- **HTTPS forzado** — CloudFront redirige HTTP → HTTPS, TLSv1.2_2021
- **Sin credenciales en código** — API key en Secrets Manager / variable de entorno Lambda
- **PITR habilitado** — DynamoDB con Point-in-Time Recovery

---

## 🔮 Mejoras Futuras

- 🔄 GitHub Actions CI/CD — deploy automático en push a master
- 📊 CloudWatch Dashboard — métricas de uso, latencia y errores
- 🔒 OIDC keyless auth para GitHub Actions
- 🧾 Endpoint `/history` — historial persistente por usuario
- 📱 PWA — instalable en móvil
- 🌍 Multi-idioma en la UI

---

## 🧗 El Camino hasta Acá — Storytelling del Proceso

Este proyecto tiene una historia de construcción que vale la pena contar, porque refleja exactamente los obstáculos reales que se encuentran al trabajar con APIs de terceros en la nube.

**La idea original era simple:** el frontend extrae el transcript de YouTube y lo manda a Lambda para resumirlo con Bedrock. Implementamos la extracción en el browser usando `youtube-transcript-api` — funcionaba perfecto en local.

**Primer golpe de realidad:** al deployar la Lambda, YouTube bloqueaba todas las requests desde IPs de AWS. No es un problema de configuración ni de permisos — YouTube detecta y bloquea activamente rangos de IP de cualquier cloud provider (AWS, GCP, Azure, todos). Pasamos a una arquitectura híbrida: el frontend extrae el transcript desde el browser (IP residencial del usuario) y lo manda a Lambda.

**Segundo golpe:** el browser tampoco podía acceder a YouTube directamente por política de CORS. YouTube no permite requests cross-origin desde dominios externos. Probamos múltiples enfoques — CORS proxies gratuitos, el endpoint `/api/timedtext`, la YouTube Data API v3 — cada uno con su propio bloqueo o limitación.

**El quiebre:** descubrimos que **Supadata**, una API de transcripts de terceros, tiene CORS abierto para browsers. Desde el browser del usuario (IP residencial), Supadata funciona sin restricciones. La arquitectura final quedó así: el browser llama a Supadata, obtiene el transcript, y lo manda a Lambda para el resumen con Bedrock.

**Bonus de Terraform:** en el camino también tuvimos que lidiar con la recreación manual de la Lambda cuando Terraform perdió el estado por un conflicto de nombres de módulos (`module.lambda_summarizer` vs `module.lambda`), y con el problema clásico de OneDrive bloqueando archivos durante el empaquetado del ZIP en Windows.

El resultado es una arquitectura que aprovecha exactamente la naturaleza del problema: **el transcript se extrae con la IP del usuario** (nunca bloqueada), y **el resumen se genera en la nube** (donde está la potencia de cómputo y la IA). Cada capa hace lo que mejor sabe hacer.

---

## 💼 Este Proyecto Demuestra

### 🔹 AWS Serverless End-to-End
- API Gateway + Lambda + DynamoDB + S3 + CloudFront + Bedrock — stack serverless completo
- Caché con TTL en DynamoDB — evita llamadas repetidas a la IA
- CloudFront con OAC — distribución segura de frontend sin exponer S3

### 🔹 Terraform IaC Profesional
- Módulos locales reutilizables con interfaz clara (variables/outputs)
- Naming convention consistente via variables
- Default tags en provider — propagados automáticamente a todos los recursos

### 🔹 Integración de IA Generativa
- AWS Bedrock Converse API — agnóstica al modelo, portable a otros LLMs
- Prompt engineering para JSON estructurado con campos específicos
- Manejo de errores diferenciado (AccessDeniedException, JSONDecodeError)

### 🔹 Resolución de Problemas Reales
- Arquitectura adaptada a las restricciones reales de YouTube y cloud providers
- Debugging con CloudWatch Logs y AWS CLI
- Manejo de encoding en Windows (PowerShell + OneDrive + UTF-8)

---

## 📝 Licencia

Proyecto orientado al aprendizaje y desarrollo de portfolio profesional.
Uso libre.

_Code made by Emma Ledesma_
🔗 https://www.linkedin.com/in/emmanuel-ledesmam/

---

# ===========================
# English Version
# ===========================

# yt-summarizer

**AI-powered YouTube video summarizer — Serverless on AWS**

GitHub: https://github.com/EmmaLedesma/youtube-summarizer

[![AWS](https://img.shields.io/badge/AWS-us--east--1-orange)](https://aws.amazon.com)
[![Terraform](https://img.shields.io/badge/terraform-1.14+-purple)](https://terraform.io)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![Bedrock](https://img.shields.io/badge/AWS_Bedrock-Claude_3.5_Haiku-teal)](https://aws.amazon.com/bedrock/)

---

## 📌 Problem Statement

Keeping up with lectures, conferences, and video tutorials takes time. This project was born from a real need: summarizing YouTube videos in seconds, extracting key points without watching the full video.

The solution is a fully serverless application on AWS: the user pastes a URL, picks the summary language, and Claude AI (via AWS Bedrock) returns a structured summary with key points, topics, and content type. Results are cached in DynamoDB to avoid repeating AI calls.

---

## 🏗️ Architecture

```
Browser
  │
  ├─ Supadata API ──────────────────► transcript text
  │  (user's residential IP,
  │   bypasses YouTube blocks)
  │
  └─ POST { videoId, transcriptText, language }
          │
          ▼
    API Gateway (REST)
          │
          ▼
    Lambda (Python 3.12)
          │
          ├─ DynamoDB.query()  ──► cache hit → immediate response
          │
          └─ Bedrock (Claude 3.5 Haiku)
                    │
                    └─ DynamoDB.putItem() → saves result
                    └─ response → Browser

Static frontend: S3 + CloudFront (OAC, HTTPS, SPA fallback)
Infrastructure: 100% Terraform (local modules)
```

---

## 🚀 Provisioned AWS Resources

| Resource | Name | Terraform Module |
|----------|------|-----------------|
| Lambda Function | `yt-summarizer-dev-summarizer` | lambda |
| IAM Role | `yt-summarizer-dev-summarizer-role` | lambda |
| CloudWatch Log Group | `/aws/lambda/yt-summarizer-dev-summarizer` | lambda |
| API Gateway REST API | `yt-summarizer-dev-api` | api-gateway |
| DynamoDB Table | `yt-summarizer-dev-summaries` | dynamodb |
| S3 Bucket (frontend) | `yt-summarizer-dev-frontend` | storage |
| CloudFront Distribution | `E16INCGHSKTQTT` | storage |
| CloudFront OAC | `yt-summarizer-dev-oac` | storage |
| Secrets Manager | `yt-summarizer/dev/supadata-key` | — |

**Total: 9 core AWS resources**

---

## ✅ Implemented Features

- **AI-structured summary** — executive summary, detailed key points, topics, and content type
- **Language selector** — user chooses summary language (Spanish, English, Portuguese, and more)
- **Smart cache** — DynamoDB stores results for 90 days with automatic TTL
- **Responsive frontend** — S3 + CloudFront with HTTPS, OAC and SPA fallback
- **Progress steps** — UI showing the status of each processing stage
- **Session history** — videos summarized in the session remain accessible

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + CSS + Vanilla JS |
| CDN / Hosting | Amazon CloudFront + S3 |
| API | Amazon API Gateway (REST) |
| Compute | AWS Lambda (Python 3.12) |
| AI | AWS Bedrock — Claude 3.5 Haiku |
| Database | Amazon DynamoDB (PAY_PER_REQUEST) |
| Transcript | Supadata API (browser-side) |
| IaC | Terraform 1.14 — local modules |
| Secrets | AWS Secrets Manager |

---

## 🔐 Security

- **Least privilege IAM** — Lambda can only invoke Bedrock, read/write its DynamoDB table, and read its secret
- **Private S3** — frontend bucket with no public access, only CloudFront via OAC
- **Forced HTTPS** — CloudFront redirects HTTP → HTTPS, TLSv1.2_2021
- **No credentials in code** — API key in Secrets Manager / Lambda environment variable
- **PITR enabled** — DynamoDB with Point-in-Time Recovery

---

## 🧗 The Road to Here — Build Storytelling

This project has a construction history worth telling, because it reflects the real obstacles encountered when working with third-party APIs in the cloud.

**The original idea was simple:** the frontend extracts the YouTube transcript and sends it to Lambda to summarize it with Bedrock. We implemented browser-side extraction using `youtube-transcript-api` — it worked perfectly locally.

**First reality check:** when deploying to Lambda, YouTube blocked all requests from AWS IP ranges. This isn't a configuration or permissions issue — YouTube actively detects and blocks cloud provider IP ranges (AWS, GCP, Azure, all of them). We moved to a hybrid architecture: the frontend extracts the transcript from the browser (user's residential IP) and sends it to Lambda.

**Second hit:** the browser couldn't access YouTube directly due to CORS policy. YouTube doesn't allow cross-origin requests from external domains. We tried multiple approaches — free CORS proxies, the `/api/timedtext` endpoint, the YouTube Data API v3 — each with its own block or limitation.

**The breakthrough:** we discovered that **Supadata**, a third-party transcript API, has open CORS for browsers. From the user's browser (residential IP), Supadata works without restrictions. The final architecture: the browser calls Supadata, gets the transcript, and sends it to Lambda for Bedrock summarization.

**Terraform bonus:** along the way we also had to deal with manual Lambda recreation when Terraform lost state due to a module naming conflict (`module.lambda_summarizer` vs `module.lambda`), and the classic OneDrive file locking issue during ZIP packaging on Windows.

The result is an architecture that leverages exactly the nature of the problem: **the transcript is extracted with the user's IP** (never blocked), and **the summary is generated in the cloud** (where the compute power and AI live). Each layer does what it does best.

---

## 💼 This Project Clearly Demonstrates

### 🔹 AWS Serverless End-to-End
- API Gateway + Lambda + DynamoDB + S3 + CloudFront + Bedrock — complete serverless stack
- DynamoDB cache with TTL — avoids repeated AI calls
- CloudFront with OAC — secure frontend distribution without exposing S3

### 🔹 Professional Terraform IaC
- Reusable local modules with clean interface (variables/outputs)
- Consistent naming convention via variables
- Default tags in provider — automatically propagated to all resources

### 🔹 Generative AI Integration
- AWS Bedrock Converse API — model-agnostic, portable to other LLMs
- Prompt engineering for structured JSON with specific fields
- Differentiated error handling (AccessDeniedException, JSONDecodeError)

### 🔹 Real Problem Solving
- Architecture adapted to the real constraints of YouTube and cloud providers
- Debugging with CloudWatch Logs and AWS CLI
- Encoding handling on Windows (PowerShell + OneDrive + UTF-8)

---

## 🔮 Future Improvements

- 🔄 GitHub Actions CI/CD — automatic deploy on push to master
- 📊 CloudWatch Dashboard — usage metrics, latency and errors
- 🔒 OIDC keyless auth for GitHub Actions
- 🧾 `/history` endpoint — persistent history per user
- 📱 PWA — installable on mobile
- 🌍 Multi-language UI

---

## 📝 License

Educational project designed for learning and professional portfolio building.
Free to use and modify.

_Code made by Emma Ledesma_
🔗 https://www.linkedin.com/in/emmanuel-ledesmam/