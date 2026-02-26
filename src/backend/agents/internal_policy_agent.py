from agent_framework import AgentExecutor
from agent_framework.azure import AzureOpenAIChatClient


class InternalPolicyAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco.
Consulta las políticas internas del banco relacionadas con la detección de fraudes.
En base a la transacción proporcionada y las políticas internas, evalúa si la transacción cumple con los criterios de seguridad establecidos o si presenta riesgos de fraude.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "internal_policy"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
        )
        super().__init__(agent=agent, id=name)
