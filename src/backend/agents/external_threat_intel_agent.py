from agent_framework import AgentExecutor
from agent_framework.azure import AzureOpenAIChatClient


class ExternalThreatIntelAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco.
Consulta fuentes externas de inteligencia sobre amenazas relacionadas a transacciones financieras.
Evalúa si la transacción proporcionada muestra alguna señal de alerta basada en la inteligencia externa disponible, y proporciona un juicio sobre el nivel de riesgo asociado.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "external_threat_intel"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
        )
        super().__init__(agent=agent, id=name)
