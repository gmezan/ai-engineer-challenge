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

Salida esperada de ejemplo:

```text
% python test.py
Query: transacción internacional desde dispositivo nuevo
Index: fraud_policies_index
Top K: 5
Results:
1. score=0.9213937
  chunk_id=2
  policy_id=FP-02
  version=2025.1
  rule=Transacción internacional y dispositivo nuevo → ESCALATE_TO_HUMAN
2. score=0.8676525
  chunk_id=4
  policy_id=FP-03
  version=2025.1
  rule=Transacción más de 30000 soles o 100000 dólares, e internacional → BLOCK
3. score=0.8475139
  chunk_id=3
  policy_id=FP-03
  version=2025.1
  rule=Transacción más de 30000 soles o 100000 dólares → ESCALATE_TO_HUMAN
4. score=0.84007776
  chunk_id=5
  policy_id=FP-04
  version=2025.1
  rule=Transacción promedio habitual y horario en rango → APPROVE
5. score=0.8107099
  chunk_id=1
  policy_id=FP-01
  version=2025.1
  rule=Monto > 3x promedio habitual y horario fuera de rango → CHALLENGE
```

