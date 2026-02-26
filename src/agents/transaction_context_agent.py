from agent_framework import AgentExecutor
from agent_framework.azure import AzureOpenAIChatClient


class TransactionContextAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco.
Analiza las señales internas de la transacción proporcionada en el prompt para identificar posibles riesgos de fraude, incumplimiento o actividades sospechosas.
Proporciona un juicio sobre el nivel de riesgo asociado con la transacción, destacando cualquier señal de alerta o preocupación relevante.
Sé breve pero conciso.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "transaction_context"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
        )
        super().__init__(agent=agent, id=name)
