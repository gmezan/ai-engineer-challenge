# Casos de transacción esperados

Este documento propone transacciones de prueba para cubrir los resultados `APPROVE`, `CHALLENGE`, `ESCALATE_TO_HUMAN` y `BLOCK`, tomando como referencia:

- comportamiento histórico (`customer_behaviors`)
- reglas de política (`fraud_policies`)

## Consideraciones base

- `CU-001`: promedio `500`, horario habitual `08:00-20:00`, país habitual `PE`, dispositivo habitual `D-01`.
- `CU-002`: promedio `1200`, horario habitual `09:00-22:00`, país habitual `PE`, dispositivo habitual `D-02`.

## 1) Caso esperado: APPROVE

```json
{
	"transaction_id": "T-2001",
	"customer_id": "CU-001",
	"amount": 480.0,
	"currency": "PEN",
	"country": "PE",
	"channel": "web",
	"device_id": "D-01",
	"timestamp": "2025-12-17T10:30:00",
	"merchant_id": "M-010"
}
```

**Por qué debería caer en APPROVE**

Cumple la regla de normalidad (`FP-04`): monto cercano al promedio habitual, horario dentro de rango, país y dispositivo conocidos.

## 2) Caso esperado: CHALLENGE

```json
{
	"transaction_id": "T-2002",
	"customer_id": "CU-001",
	"amount": 2000.0,
	"currency": "PEN",
	"country": "PE",
	"channel": "mobile",
	"device_id": "D-01",
	"timestamp": "2025-12-17T02:15:00",
	"merchant_id": "M-011"
}
```

**Por qué debería caer en CHALLENGE**

Activa `FP-01`: el monto supera 3x el promedio de `CU-001` (3 x 500 = 1500) y además ocurre fuera del horario habitual.

## 3) Caso esperado: ESCALATE_TO_HUMAN

```json
{
	"transaction_id": "T-2003",
	"customer_id": "CU-002",
	"amount": 5000.0,
	"currency": "PEN",
	"country": "CL",
	"channel": "web",
	"device_id": "D-99",
	"timestamp": "2025-12-17T11:20:00",
	"merchant_id": "M-012"
}
```

**Por qué debería caer en ESCALATE_TO_HUMAN**

Activa `FP-02`: operación internacional y dispositivo nuevo para el cliente. El monto no requiere bloqueo por umbral alto, por lo que corresponde revisión humana.

## 4) Caso esperado: BLOCK

```json
{
	"transaction_id": "T-2004",
	"customer_id": "CU-001",
	"amount": 45000.0,
	"currency": "PEN",
	"country": "US",
	"channel": "mobile",
	"device_id": "D-77",
	"timestamp": "2025-12-17T23:50:00",
	"merchant_id": "M-013"
}
```

**Por qué debería caer en BLOCK**

Activa la regla de mayor severidad de `FP-03`: monto mayor a 30,000 PEN y transacción internacional. Aunque el umbral alto también puede detonar escalamiento, este patrón combinado corresponde a bloqueo.

## Nota de uso

Para pruebas controladas, cargar estos objetos en el contenedor `transactions` y ejecutar cada `transaction_id` de forma individual desde la UI o backend.
