
import asyncio
import json
import os
from typing import Any
from datetime import datetime, timezone

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from agent_framework import (
    Message,
    Workflow,
    WorkflowBuilder,
    WorkflowEvent)
from agents.debate_agent import DebateAgent
from agents.decision_arbiter_agent import DecisionArbiterAgent
from agents.input_transaction_executor import InputTransactionExecutor
from models.Transaction import Transaction
from agent_framework.azure import AzureOpenAIChatClient
from agents.evidence_aggregation_agent import EvidenceAggregationAgent
from agents.behavioral_pattern_agent import BehavioralPatternAgent
from agents.external_threat_intel_agent import ExternalThreatIntelAgent
from agents.internal_policy_agent import InternalPolicyAgent
from agents.transaction_context_agent import TransactionContextAgent

from agent_framework.openai import OpenAIResponsesClient

load_dotenv()

client = AzureOpenAIChatClient(credential=DefaultAzureCredential())


def _build_openai_responses_client() -> OpenAIResponsesClient:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    model_id = os.getenv("OPENAI_RESPONSES_MODEL_ID") or os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("AZURE_OPENAI_BASE_URL")

    if not base_url:
        endpoint = (os.getenv("AZURE_OPENAI_ENDPOINT") or "").rstrip("/")
        if endpoint:
            base_url = f"{endpoint}/openai/v1"

    return OpenAIResponsesClient(
        model_id=model_id,
        api_key=api_key,
        base_url=base_url,
    )


client_openai = _build_openai_responses_client()

# Start executor
start_executor = InputTransactionExecutor(client)

# Concurrent agents
transaction_context = TransactionContextAgent(client)
behavioral_pattern = BehavioralPatternAgent(client)
internal_policy = InternalPolicyAgent(client)
external_threat_intel = ExternalThreatIntelAgent(client_openai)
concurrent_agents = [transaction_context, behavioral_pattern, internal_policy] #external_threat_intel]

debate_agent = DebateAgent(client)

decision_arbiter = DecisionArbiterAgent(client)

# Aggregator agent
evidence_aggregation = EvidenceAggregationAgent(client)

input_message = "Transaccion T-1001"


def _print_messages_trace(messages: list[Message], title: str) -> None:
    print(f"{title} (count={len(messages)})")
    for index, msg in enumerate(messages, start=1):
        payload = msg.to_dict() if hasattr(msg, "to_dict") else {
            "role": getattr(msg, "role", None),
            "author_name": getattr(msg, "author_name", None),
            "text": getattr(msg, "text", None),
        }
        print(f"  - message[{index}] role={getattr(msg, 'role', 'unknown')} author={getattr(msg, 'author_name', None)}")
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _trace_event(event: WorkflowEvent) -> None:
    print("\n" + "=" * 80)
    print(f"TRACE event.type={event.type} executor_id={getattr(event, 'executor_id', None)}")
    data = getattr(event, "data", None)

    if isinstance(data, list) and data and all(isinstance(item, Message) for item in data):
        _print_messages_trace(data, "TRACE output message list")
        return

    if hasattr(data, "agent_response"):
        executor_id = getattr(data, "executor_id", "unknown")
        print(f"TRACE AgentExecutorResponse from executor={executor_id}")
        agent_response = getattr(data, "agent_response", None)
        response_messages = list(getattr(agent_response, "messages", []) or [])
        if response_messages:
            _print_messages_trace(response_messages, "TRACE agent_response.messages")

        full_conversation = list(getattr(data, "full_conversation", []) or [])
        if full_conversation:
            _print_messages_trace(full_conversation, "TRACE full_conversation")
        return

    if hasattr(data, "to_dict"):
        print(json.dumps(data.to_dict(), ensure_ascii=False, indent=2, default=str))
        return

    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))

async def main() -> None:
    workflow: Workflow = WorkflowBuilder(start_executor=start_executor) \
        .add_fan_out_edges(start_executor, concurrent_agents) \
        .add_fan_in_edges(concurrent_agents, evidence_aggregation) \
        .add_edge(evidence_aggregation, debate_agent) \
        .add_fan_in_edges([debate_agent, evidence_aggregation], decision_arbiter) \
        .build()
    output_evt: WorkflowEvent  | None = None
    events = await workflow.run(message=input_message)

    for event in events:
        #_trace_event(event)
        if (event.type == "output"):
            output_evt = event

    print("===== Final Aggregated Conversation (messages) =====")
    messages: list[Message] | Any = output_evt.data

    for i, msg in enumerate(messages, start=1):
        name = msg.author_name if msg.author_name else "user"
        print(f"{'-' * 60}\n\n{i:02d} [{name}]:\n{msg.text}")


if __name__ == "__main__":
    asyncio.run(main())