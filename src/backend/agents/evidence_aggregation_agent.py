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
Eres un analista de fraudes en transacciones de un banco, tu función es sintetizar la información que te proporcionan otros agentes.
Para cada agente agregado, genera un resumen independiente con los detalles más importantes, incluyendo datos concretos observados y una conclusión específica de ese agente.
Estructura la salida por agente.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "evidence_aggregation"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
        )
        self.agent = agent
        super().__init__(agent=agent, id=name)

    @handler
    async def aggregate(self, results: List[AgentExecutorResponse], ctx: WorkflowContext[str, str]) -> None:
        # Combine only each branch's final assistant analysis to avoid duplicated history/tokens
        combined: list[Message] = []
        for r in results:
            messages = list(getattr(r.agent_response, "messages", []) or [])
            assistant_messages = [m for m in messages if getattr(m, "role", None) == "assistant" and m.text]
            if assistant_messages:
                final_text = assistant_messages[-1].text
                combined_input = f"[{r.executor_id}]\n{final_text}"
                #print(f"Combined input for {r.executor_id}:\n{combined_input}\n")
                combined.append(Message("user", text=combined_input))

        response = await self.agent.run(combined)

        msgs = list(getattr(response, "messages", []) or [])
        assistant_messages = [m for m in msgs if getattr(m, "role", None) == "assistant" and m.text]
        summary_text = assistant_messages[-1].text if assistant_messages else ""

        await ctx.send_message(summary_text)
        await ctx.yield_output(summary_text)
