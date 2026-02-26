# Knowledge - Índice vectorial de políticas de fraude

Se implementa un índice vectorial en Azure AI Search a partir del contenido de `fraud_policies.json`.

## Resumen

- Se utiliza autenticación con **Azure CLI** para Azure AI Search (`az login`).
- Se utiliza **Azure OpenAI** para generar embeddings.
- Se crea (o recrea, en caso necesario) el índice `fraud_policies_index` con:
  - `policy_id` (clave)
  - `rule` (texto)
  - `rule_vector` (vector con embedding del campo `rule`)
  - `version`
- Se cargan los documentos del JSON **sin chunking**.
- Se incluye `test.py` para probar una búsqueda vectorial y mostrar resultados.

## Archivos importantes

- `main.py`: crea el índice y carga los documentos con embeddings.
- `test.py`: ejecuta una búsqueda vectorial de prueba.
- `fraud_policies.json`: datos fuente.
- `requirements.txt`: dependencias.

## Variables de entorno

Mínimas para ejecutar:

- `SEARCH_ENDPOINT`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`

También se utilizan variables estándar de Azure OpenAI (por ejemplo endpoint y api version, según la configuración local).

Puedes usar un archivo `.env`.

## Cómo ejecutar

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Inicio de sesión en Azure (si corresponde para Search):

```bash
az login
```

3. Crear índice y cargar datos:

```bash
python main.py
```

4. Probar búsqueda vectorial:

```bash
python test.py
```

## Nota rápida

Si cambias el modelo/deployment de embeddings, recuerda ajustar dimensiones del vector para que coincidan con el índice.
