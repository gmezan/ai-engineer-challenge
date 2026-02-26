from typing import Any, List
import json
from typing_extensions import Never

from agent_framework import AgentExecutorResponse, Agent, Executor, Message, WorkflowContext, handler
from agent_framework.azure import AzureOpenAIChatClient
from pydantic import BaseModel


class InternalCitation(BaseModel):
    policy_id: str
    chunk_id: str
    version: str


class ExternalCitation(BaseModel):
    url: str
    summary: str


class DecisionArbiterOutput(BaseModel):
    decision: str
    confidence: float
    signals: list[str]
    citations_internal: list[InternalCitation]
    citations_external: list[ExternalCitation]
    explanation_customer: str
    explanation_audit: str


class DecisionArbiterAgent(Executor):
    agent: Agent

    INSTRUCTIONS = """
Eres un árbitro de decisión en un sistema de análisis de fraude transaccional.
Recibirás toda la evidencia recopilada por múltiples agentes (contexto transaccional,
patrones de comportamiento, políticas internas, inteligencia externa y debate).

Tu tarea es tomar una decisión final única y justificada.

Responde ÚNICAMENTE como un objeto JSON válido con esta estructura exacta:
{
    "decision": "ALLOW|CHALLENGE|BLOCK|ESCALATE_TO_HUMAN",
    "confidence": 0.0,
    "signals": ["..."],
    "citations_internal": [ // Solo los policies concluyentes
        {
            "policy_id": "...",
            "chunk_id": "...",
            "version": "..."
        }
    ],
    "citations_external": [
        {
            "url": "https://...",
            "summary": "..."
        }
    ],
    "explanation_customer": "...",
    "explanation_audit": "..."
}

Reglas:
- decision debe ser exactamente ALLOW, CHALLENGE, BLOCK o ESCALATE_TO_HUMAN.
- confidence debe estar entre 0.0 y 1.0.
- signals debe listar patrones clave, eg: "Monto fuera de rango" , "Horario no habitual" , "Alerta externa" 
- citations_internal y citations_external deben incluir solo citas realmente usadas; pueden ser listas vacías si no hay evidencia.
- explanation_customer debe ser clara y entendible para el cliente.
- explanation_audit debe ser trazable, técnica y resumir el razonamiento.
- No incluyas texto fuera del JSON.

No inventes información. Usa solo la evidencia entregada.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "decision_arbiter"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            default_options={"response_format": DecisionArbiterOutput},
        )
        self.agent = agent
        super().__init__(agent=agent, id=name)

    @handler
    async def aggregate(self, results: List[Any], ctx: WorkflowContext[dict[str, Any], dict[str, Any]]) -> None:
        combined: list[Message] = []
        for item in results:
            if isinstance(item, AgentExecutorResponse):
                messages = list(getattr(item.agent_response, "messages", []) or [])
                assistant_messages = [m for m in messages if getattr(m, "role", None) == "assistant" and m.text]
                if assistant_messages:
                    final_text = assistant_messages[-1].text
                    combined.append(Message("user", text=f"[{item.executor_id}]\n{final_text}"))
                continue

            if isinstance(item, str) and item.strip():
                combined.append(Message("user", text=f"[evidence_aggregation]\n{item}"))
                continue

            if isinstance(item, list):
                msg_list = [m for m in item if isinstance(m, Message) and getattr(m, "text", "")]
                if msg_list:
                    combined.append(Message("user", text=f"[evidence_aggregation]\n{msg_list[-1].text}"))

        arbitration = await self.agent.run(combined)
        output_messages = list(getattr(arbitration, "messages", []) or [])
        assistant_messages = [m for m in output_messages if getattr(m, "role", None) == "assistant" and m.text]
        decision_obj: dict[str, Any] = {}
        if assistant_messages:
            raw_text = assistant_messages[-1].text
            try:
                decision_obj = json.loads(raw_text)
            except Exception:
                decision_obj = {"raw": raw_text}

        await ctx.send_message(decision_obj)
        await ctx.yield_output(decision_obj)
