# Solution Architecture

## Overview

This document describes the architecture for the AI Engineer Challenge solution. The solution leverages Azure services to build a scalable AI-powered application.

## Solution Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Client["Client Application"]
    end
    
    subgraph "Azure Services"
        App["Azure App Service<br/>or<br/>Azure Functions"]
        Cognitive["Azure OpenAI<br/>Cognitive Account"]
        Storage["Azure Storage"]
        CosmosDB["Azure Cosmos DB<br/>or<br/>Azure Database"]
    end
    
    subgraph "Monitoring & Observability"
        AppInsights["Application Insights"]
        Monitor["Azure Monitor"]
    end
    
    Client -->|HTTP/REST| App
    App -->|API Call| Cognitive
    App -->|Read/Write| Storage
    App -->|Query/Store| CosmosDB
    App -->|Telemetry| AppInsights
    Cognitive -->|Metrics| Monitor
    Storage -->|Metrics| Monitor
```

## Components

### Client Layer
- **Client Application**: Consumes the APIs provided by the application

### Azure Services
- **Azure OpenAI (Cognitive Account)**: Provides AI/ML capabilities using OpenAI models (GPT, Embedding, etc.)
- **Azure App Service/Functions**: Hosts the application logic and APIs
- **Azure Storage**: Handles data persistence (files, blobs, documents)
- **Azure Cosmos DB / Azure Database**: Stores structured application data

### Monitoring & Observability
- **Application Insights**: Collects application telemetry and diagnostics
- **Azure Monitor**: Provides monitoring and alerting for Azure resources

## Data Flow

1. Client requests are received by the application
2. Application processes requests using Azure OpenAI for AI capabilities
3. Data is persisted in Storage and CosmosDB as needed
4. Telemetry is sent to Application Insights
5. Responses are returned to the client

## AI Architecture Diagram

```mermaid
graph TB
    
    input["Input"]
    transaction_context_agent["Transaction Context<br/>Agent"]
    behavioral_pattern_agent["Behavioral Pattern<br/>Agent"]
    internal_policy_agent["Internal Policy RAG<br/>Agent"]
    external_threat_intel_agent["External Threat Intel<br/>Agent"]

    evidence_aggregation_agent["Evidence Aggregation<br/>Agent"]
    debate_agent["Debate<br/>Agents"]
    decision_arbiter_agent["Decision Arbiter<br/>Agent"]
    explainability_agent["Explainability<br/>Agent"]
    
    input -->transaction_context_agent
    input -->behavioral_pattern_agent
    input -->internal_policy_agent
    input -->external_threat_intel_agent

    transaction_context_agent -->evidence_aggregation_agent
    behavioral_pattern_agent -->evidence_aggregation_agent
    internal_policy_agent -->evidence_aggregation_agent
    external_threat_intel_agent -->evidence_aggregation_agent

    evidence_aggregation_agent -->debate_agent
    debate_agent -->decision_arbiter_agent
    decision_arbiter_agent -->explainability_agent
```

## Infrastructure as Code

The infrastructure is defined using Terraform with the following key resources:
- Azure Resource Group: `rg-ai-engineer-challenge`
- Azure OpenAI Cognitive Account
- Additional resources (to be defined)

## Deployment

Terraform configurations are stored in the `/infra` directory:
- `main.tf`: Main resource definitions
- `providers.tf`: Provider configuration and backend setup
- Backend: Azure Storage (state file storage)

## Next Steps

- [ ] Define additional Azure resources as needed
- [ ] Configure authentication and authorization
- [ ] Set up CI/CD pipelines
- [ ] Implement monitoring and alerting
- [ ] Document API specifications
