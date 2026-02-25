
import asyncio
from typing import Any
from datetime import datetime

from dotenv import load_dotenv
from agent_factory import AgentFactory
from agent_framework.orchestrations import ConcurrentBuilder
from agent_framework import (
    Message,
    Workflow,
    WorkflowEvent)
from models.Transaction import Transaction


load_dotenv()

# Initialize the agent factory
factory = AgentFactory(config_path="agents.yaml")

# Create agents by name
transaction_context = factory.create_agent("transaction_context")
behavioral_pattern = factory.create_agent("behavioral_pattern")
internal_policy = factory.create_agent("internal_policy")
external_threat_intel = factory.create_agent("external_threat_intel")


async def main() -> None:
    # Create a sample transaction for analysis
    sample_transaction = Transaction(
        transaction_id="TXN-2025-001234",
        customer_id="CUST-5678",
        amount=1500.00,
        currency="USD",
        country="US",
        channel="online",
        device_id="device-9876",
        timestamp=datetime.now(),
        merchant_id="MERCHANT-555",
    )

    workflow : Workflow = ConcurrentBuilder(participants =
        [transaction_context, behavioral_pattern, internal_policy, external_threat_intel]).build()

    output_evt: WorkflowEvent  | None = None
    events = await workflow.run(message=str(sample_transaction))

    for event in events:
        if (event.type == "output"):
            output_evt = event

    print("===== Final Aggregated Conversation (messages) =====")
    messages: list[Message] | Any = output_evt.data

    for i, msg in enumerate(messages, start=1):
        name = msg.author_name if msg.author_name else "user"
        print(f"{'-' * 60}\n\n{i:02d} [{name}]:\n{msg.text}")


if __name__ == "__main__":
    asyncio.run(main())