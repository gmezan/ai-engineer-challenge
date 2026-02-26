
import asyncio
import json
import os
from typing import Any
from datetime import datetime, timezone

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from agent_framework import (
    FileCheckpointStorage,
    InMemoryCheckpointStorage,
    Message,
    Workflow,
    WorkflowBuilder,
    WorkflowEvent)
from fastapi import FastAPI
import uvicorn
from agents.debate_agent import DebateAgent
from agents.decision_arbiter_agent import DecisionArbiterAgent
from agents.explainability_agent import ExplainabilityAgent
from agents.input_transaction_executor import InputTransactionExecutor
from models.Transaction import Transaction
from agent_framework.azure import AzureOpenAIChatClient
from agents.evidence_aggregation_agent import EvidenceAggregationAgent
from agents.behavioral_pattern_agent import BehavioralPatternAgent
from agents.external_threat_intel_agent import ExternalThreatIntelAgent
from agents.internal_policy_agent import InternalPolicyAgent
from agents.transaction_context_agent import TransactionContextAgent

from agent_framework_ag_ui import AgentFrameworkAgent, add_agent_framework_fastapi_endpoint

from agent_framework.openai import OpenAIResponsesClient
from agent_framework import WorkflowEvent


load_dotenv()

client = AzureOpenAIChatClient(credential=DefaultAzureCredential())
checkpoint_storage = FileCheckpointStorage('./checkpoints')

UI_VISIBLE_EXECUTORS = {
    "EvidenceAggregationAgent",
    "DecisionArbiterAgent",
    "ExplainabilityAgent",
    "HumanInterventionExecutor",
}


def ui_event_filter(event: WorkflowEvent) -> bool:
    """
    Return True if this event should be sent to the frontend.
    """
    # Always allow final output
    if event.type == "output":
        return True

    executor_id = getattr(event, "executor_id", None)
    if not executor_id:
        return False

    return executor_id in UI_VISIBLE_EXECUTORS

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
concurrent_agents = [transaction_context, behavioral_pattern, internal_policy, external_threat_intel]

debate_agent = DebateAgent(client)

decision_arbiter = DecisionArbiterAgent(client)
explainability_agent = ExplainabilityAgent(client)

# Aggregator agent
evidence_aggregation = EvidenceAggregationAgent(client)

input_message = "Transaccion T-1001"


workflow: Workflow = WorkflowBuilder(start_executor=start_executor, checkpoint_storage=checkpoint_storage) \
    .add_fan_out_edges(start_executor, concurrent_agents) \
    .add_fan_in_edges(concurrent_agents, evidence_aggregation) \
    .add_edge(evidence_aggregation, debate_agent) \
    .add_fan_in_edges([debate_agent, evidence_aggregation], decision_arbiter) \
    .add_edge(decision_arbiter, explainability_agent) \
    .build()


app = FastAPI(title="CopilotKit + Microsoft Agent Framework (Python)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ui_agent = AgentFrameworkAgent(
    agent=workflow.as_agent(),
    require_confirmation=False
)


add_agent_framework_fastapi_endpoint(
    app=app,
    agent=ui_agent,
    path="/",
)


if __name__ == "__main__":
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8888"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
