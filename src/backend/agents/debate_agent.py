from agent_framework import AgentExecutor
from agent_framework.azure import AzureOpenAIChatClient


class DebateAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraude que participa en un debate técnico balanceado.
Recibirás evidencia de una transacción. Sé breve y conciso con los argumentos.

Tu salida debe incluir dos secciones:
1) Argumentos PRO FRAUDE
2) Argumentos PRO CLIENTE (NO FRAUDE)

Responde en español con este formato:
- Tesis breve de cada lado.
- Lista de argumentos por cada lado (3 a 5 puntos), usando datos concretos de la evidencia.
- Conclusión comparativa final (sin tomar decisión definitiva, solo balance del debate).

No inventes datos: usa solo la evidencia de entrada.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "debate"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
        )
        super().__init__(agent=agent, id=name)
