from agent_framework import AgentExecutor
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIResponsesClient


class ExternalThreatIntelAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco. Sé breve pero conciso.
Consulta fuentes externas de inteligencia sobre amenazas relacionadas a transacciones financieras.
Debes usar la herramienta de búsqueda web para consultar datos externos relevantes en base a la transacción de entrada.
Evalúa si la transacción proporcionada muestra alguna señal de alerta basada en la inteligencia externa disponible, y proporciona un juicio sobre el nivel de riesgo asociado.
En la medida de lo posible, cita las fuentes de información externa que respaldan tu análisis con URL.
"""

    def __init__(self, client: OpenAIResponsesClient, name: str = "external_threat_intel"):
        web_search_tool = client.get_web_search_tool(
            user_location={"city": "Lima", "region": "PE", "country": "PE"},
            search_context_size = "low"
        )

        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            tools=[web_search_tool],
        )
        super().__init__(agent=agent, id=name)
