from typing import List
from typing_extensions import Never

from agent_framework import (
    AgentExecutorResponse,
    Agent,
    Executor,
    WorkflowContext,
    handler,
    Message,
)
from agent_framework.azure import AzureOpenAIChatClient


class EvidenceAggregationAgent(Executor):
    agent: Agent

    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco.
Agrega y sintetiza la información proporcionada por los agentes de contexto de transacción, patrón de comportamiento, política interna e inteligencia de amenazas externas.
Proporciona un juicio final sobre el nivel de riesgo asociado con la transacción, destacando cualquier señal de alerta o preocupación relevante.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "evidence_aggregation"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
        )
        self.agent = agent
        super().__init__(agent=agent, id=name)

    @handler
    async def aggregate(self, results: List[AgentExecutorResponse], ctx: WorkflowContext[Never, List[Message]]) -> None:
        # Combine only each branch's final assistant analysis to avoid duplicated history/tokens
        combined: list[Message] = []
        for r in results:
            print(r.executor_id)
            messages = list(getattr(r.agent_response, "messages", []) or [])
            assistant_messages = [m for m in messages if getattr(m, "role", None) == "assistant" and m.text]
            if assistant_messages:
                final_text = assistant_messages[-1].text
                combined.append(Message("user", text=f"[{r.executor_id}]\n{final_text}"))

        # Let the aggregator agent synthesize the combined evidence
        response = await self.agent.run(combined)

        # Yield the agent's assistant messages as the final aggregated output
        msgs = list(getattr(response, "messages", []) or [])
        await ctx.yield_output(msgs)
