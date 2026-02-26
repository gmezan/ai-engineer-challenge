# Project setup

## Objetivo

Este documento describe la secuencia operativa para levantar el proyecto:

1. Aprovisionar infraestructura con Terraform.
2. Cargar conocimiento en Azure AI Search.
3. Cargar datos iniciales en Azure Cosmos DB desde `src/resources`.
4. Ejecutar backend Python en `src/`.
5. Ejecutar frontend Next.js.

## Prerrequisitos

- Azure CLI autenticado con una cuenta con permisos sobre el grupo de recursos.
- Terraform >= 1.6.
- Python 3.12+.
- Node.js 20+.

Comandos recomendados de validación:

```bash
az login
az account show
terraform -version
python --version
node --version
```

## 1) Aprovisionamiento de infraestructura (Terraform)

Desde la raíz del repositorio:

```bash
cd infra
terraform init
terraform plan
terraform apply
```

Notas:

- El backend remoto de Terraform está configurado en `infra/providers.tf`; completar `resource_group_name` y `storage_account_name` antes de `terraform init` cuando se use estado remoto.
- La definición de recursos base está en `infra/main.tf`.

## 2) Configurar variables `.env` para backend y carga de datos

Crear o actualizar `src/.env` con las variables necesarias para ejecución local:

```dotenv
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<openai-resource>.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<chat-deployment-name>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=<embedding-deployment-name>
AZURE_OPENAI_API_KEY=<openai-key>

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
SEARCH_ENDPOINT=https://<search-service>.search.windows.net

# Cosmos DB
COSMOS_ENDPOINT=https://<cosmos-account>.documents.azure.com:443/

```

Notas:

- `src/knowledge/main.py` utiliza `SEARCH_ENDPOINT`.
- Los agentes de backend utilizan `AZURE_SEARCH_ENDPOINT`.
- Para evitar desalineación, se recomienda definir ambos valores con la misma URL.
- No versionar `.env` ni credenciales en Git.

## 3) Cargar conocimiento en Azure AI Search

El índice vectorial y la carga de políticas se ejecutan desde `src/knowledge/main.py`.

```bash
cd src/knowledge
python main.py
```

Resultado esperado:

- Se crea (o actualiza) el índice `fraud_policies_index`.
- Se cargan documentos desde `src/knowledge/fraud_policies.json`.
- Cada documento incluye embedding en el campo `rule_vector`.

## 4) Cargar datos iniciales en Cosmos DB desde `src/resources`

Subir los archivos de `src/resources` al contenedor correspondiente en Cosmos DB:

- `src/resources/transactions.json` → contenedor `transactions`
- `src/resources/customer_behaviors.json` → contenedor `customer_behaviors`

La carga puede realizarse por el mecanismo operativo definido por el equipo (portal, pipeline o utilitario interno), respetando el mapeo de archivo a contenedor.

## 5) Ejecutar backend Python (`src/`)

Desde la raíz del proyecto:

```bash
cd src
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Resultado esperado:

- API FastAPI disponible en `http://localhost:8888`.
- Endpoint AG-UI expuesto en `/`.

## 6) Ejecutar frontend

En otra terminal:

```bash
cd src/frontend
npm install
npm run dev
```

Resultado esperado:

- Frontend en `http://localhost:3000`.
- La ruta de CopilotKit (`src/frontend/src/app/api/copilotkit/route.ts`) consume el backend en `http://localhost:8888/`.

## Verificación rápida de punta a punta

1. Backend activo en `:8888`.
2. Frontend activo en `:3000`.
3. Enviar una transacción desde la UI.
4. Confirmar respuesta con decisión y explicación.

## Troubleshooting breve

- Error de autenticación Azure: ejecutar `az login` y validar suscripción activa con `az account show`.
- Error en carga de AI Search: validar `SEARCH_ENDPOINT`, `AZURE_OPENAI_ENDPOINT` y deployment de embeddings.
- Error en Cosmos: validar `COSMOS_ENDPOINT`, `COSMOS_KEY` y existencia de contenedores.
- Frontend sin respuesta: confirmar que `src/frontend/src/app/api/copilotkit/route.ts` apunta al backend local correcto.
