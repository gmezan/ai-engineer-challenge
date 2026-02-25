import yaml
from pathlib import Path
from agent_framework.azure import AzureOpenAIChatClient


class AgentFactory:
    def __init__(self, config_path: str | Path = "agents.yaml"):
        self.config_path = Path(config_path)
        self._agents_config = self._load_config()
        self._client = AzureOpenAIChatClient()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        return config.get("agents", {})

    def get_agent_config(self, agent_name: str) -> dict:
        """
        Get the configuration for a specific agent by name.
        
        Args:
            agent_name: Name of the agent to retrieve.
        
        Returns:
            Dictionary containing the agent's name and instructions.
        
        Raises:
            ValueError: If the agent name is not found in the configuration.
        """
        if agent_name not in self._agents_config:
            available = list(self._agents_config.keys())
            raise ValueError(
                f"Agent '{agent_name}' not found. Available agents: {available}"
            )
        
        return self._agents_config[agent_name]

    def create_agent(self, agent_name: str):
        """
        Create and return an agent instance by name.
        
        Args:
            agent_name: Name of the agent to create.
        
        Returns:
            An initialized agent instance from AzureOpenAIChatClient.
        
        Raises:
            ValueError: If the agent name is not found.
        """
        config = self.get_agent_config(agent_name)
        return self._client.as_agent(
            name=config["name"] if "name" in config else agent_name,
            instructions=config["instructions"]
        )

    def list_agents(self) -> list[str]:
        """Return a list of all available agent names."""
        return list(self._agents_config.keys())
