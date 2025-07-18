# Datafyme

## Overview

Datafyme is a  agentic reporting system built with Django and modern LLM-based agents. It supports database documentation, relation extraction, and advanced analytical reporting via agentic workflows. The system is fully containerized and integrates with PostgreSQL, Neo4j, and Milvus for advanced data and knowledge management.


### Demo Video (Click the image below)

[![Main screen](/images/main_screen.png)](https://drive.google.com/file/d/15dOJHVeKP_wKUV9zrb_SawSX-Eg7ws9e/view?usp=sharing)

**Data Source Support**: Currently supports PostgreSQL as the primary data source. Support for additional database types (MySQL, SQL Server, Oracle, etc.) is planned for future releases.


## Authors

- [Botond Hegedus](https://www.linkedin.com/in/botond-heged%C3%BCs-690982262/)
- [Oliver Suhajda](https://www.linkedin.com/in/suhajda-oliv%C3%A9r-477535295/)
---

## Tech Stack

- **Python 3.12**
- **Django 5.1.1**
- **FastAPI (via Uvicorn)**
- **LangChain, LangGraph** (LLM agent orchestration)
- **PostgreSQL** (main DB)
- **Neo4j** (graph DB for relations)
- **Milvus** (vector DB for semantic search)
- **Docker Compose** (multi-service orchestration)

---

## Dockerized Architecture

The system is fully containerized. Main services:

- `backend`: Django
- `worker`: Background task runner (dbloader, async jobs)
- `django-db`: Main PostgreSQL database
- `mock-db`: Mock/test PostgreSQL database
- `neo4j`: Graph database for entity/relation storage
- `standalone` (Milvus): Vector database for semantic search
- `minio`, `etcd`: Milvus dependencies
- `nginx`: Serves static files and acts as reverse proxy
- `python-code-runner`: Isolated code execution service

---

## High-Level Architecture

```mermaid
flowchart TD
  subgraph Backend
    direction TB
    DBLoader["DBLoader (dbloader)"]
    VectorLoader["VectorLoader (vector_loader)"]
    RelationFinder["RelationFinder (graph_loader)"]
    Neo4JInstance["Neo4JInstance (graph_db)"]
    TableDocumentationModel["TableDocumentationModel (db_configurator)"]
    TableDocument["TableDocument (vectordb)"]
    DatabaseManager["DatabaseManager (common.db.manager)"]
    DatabaseSource["DatabaseSource (db_configurator)"]
    DBLoader -->|uses| VectorLoader
    DBLoader -->|uses| RelationFinder
    VectorLoader -->|stores| TableDocumentationModel
    VectorLoader -->|stores| TableDocument
    RelationFinder -->|creates| Neo4JInstance
    DBLoader -->|uses| DatabaseManager
    DBLoader -->|uses| DatabaseSource
  end
  subgraph ReporterAgent
    direction TB
    ReporterGraph["Reporter Graph (StateGraph)"]
    SQLAgentGraph["SQL Agent Graph (StateGraph)"]
    VisAgentGraph["Visualization Agent Graph (StateGraph)"]
    Nodes["Nodes: filter, summarize, router, create_sql, run_sql, refine, visualize, Q&A"]
    ReporterGraph -->|invokes| SQLAgentGraph
    ReporterGraph -->|invokes| VisAgentGraph
    ReporterGraph -->|executes| Nodes
  end
  Backend -->|provides data| ReporterAgent
  classDef box fill:#fff,stroke:#333,stroke-width:2px;
  class Backend,ReporterAgent box;
```

---

## dbloader: Purpose & Agentic Workflow

### Purpose

- **dbloader** is responsible for:
  - Extracting table schemas and relations from a database
  - Generating rich documentation for each table using LLM agents
  - Storing documentation in both the main DB and a vector DB (Milvus)
  - Discovering and storing table relations in Neo4j (graph DB)

### Agentic Workflow

```mermaid
flowchart TD
  subgraph dbloader Agentic Workflow
    direction TB
    Start["Start: DBLoader.load()"]
    ExtractSchemas["Extract Table Schemas"]
    VectorLoader["VectorLoader: Generate Table Docs (LLM agent)"]
    SaveDocs["Save Docs to DB & VectorDB"]
    ExtractRelations["Extract Table Relations"]
    RelationFinder["RelationFinder: Find Relations (LLM agent)"]
    SaveRelations["Save Relations to Neo4j"]
    End["End"]
    Start --> ExtractSchemas --> VectorLoader --> SaveDocs --> ExtractRelations --> RelationFinder --> SaveRelations --> End
  end
```

- **VectorLoader**: Uses an LLM agent to generate technical and business documentation for each table.
- **RelationFinder**: Uses an LLM agent to infer foreign key/public key relations from DDLs.
- **All results** are stored in the appropriate DBs for later semantic search and graph analysis.

---

## reporter_agent: Purpose & Agentic Workflow

### Purpose

- **reporter_agent** orchestrates the analytical reporting workflow:
  - Receives user questions (in natural language)
  - Determines if a SQL query or simple Q&A is needed
  - Generates, refines, and executes SQL queries using LLM agents
  - Visualizes results (charts, tables, text) using agentic subgraphs

### Agentic Workflow

#### Main Reporter Agent Workflow

```mermaid
flowchart TD
    Start([Start: User Question]) --> FilterChat[Check Message Relevance]
    
    FilterChat -->|Relevant| SummarizeHistory[Summarize Chat History]
    FilterChat -->|Not Relevant| BasicChat[Generate Basic Response]
    BasicChat --> End([End: Return Response])
    
    SummarizeHistory --> TaskRouter{Is SQL Query Needed?}
    
    TaskRouter -->|Yes| CreateSQL[Generate SQL Query]
    TaskRouter -->|No| SecondRouter{New Chart Needed?}
    
    SecondRouter -->|Yes| CreateSQL
    SecondRouter -->|No| QandA[Generate Q&A Response]
    QandA --> End
    
    CreateSQL --> RunSQL[Execute SQL Query]
    
    RunSQL --> CheckResult{Check SQL Result}
    CheckResult -->|Success + Data| CreateViz[Create Visualization]
    CheckResult -->|Error| RefineSQL[Refine SQL Query]
    CheckResult -->|Empty Result| RefineEmpty[Refine for Empty Result]
    
    RefineSQL --> RunSQL
    RefineEmpty --> RunSQL
    
    CreateViz --> End
    
    style Start fill:#e1f5fe
    style End fill:#f3e5f5
    style FilterChat fill:#fff3e0
    style TaskRouter fill:#fff8e1
    style SecondRouter fill:#fff8e1
    style CheckResult fill:#fff8e1
    style CreateSQL fill:#e8f5e8
    style CreateViz fill:#e8f5e8
    style QandA fill:#e8f5e8
```

#### SQL Agent Subgraph

```mermaid
flowchart TD
    SQLStart([SQL Agent Start]) --> HybridSearch[Hybrid Search: Find Relevant Tables from vector store]
    
    HybridSearch --> GetDDLs[Extract Table DDLs]
    GetDDLs --> Reranker[Rerank Tables by Relevance]
    
    Reranker --> CheckTables{Tables Found?}
    CheckTables -->|No| RefineQuestion[Refine User Question]
    CheckTables -->|Yes| RelationGraph[Get neighbor tables from graph db]
    
    RefineQuestion --> HybridSearch
    
    RelationGraph --> GetFinalDDLs[Get Final DDL Structures]
    GetFinalDDLs --> CreateQuery[Generate SQL Query]
    
    CreateQuery --> SQLEnd([Return SQL + Description])
    
    style SQLStart fill:#e1f5fe
    style SQLEnd fill:#f3e5f5
    style HybridSearch fill:#fff3e0
    style Reranker fill:#fff3e0
    style CheckTables fill:#fff8e1
    style RelationGraph fill:#e8f5e8
    style CreateQuery fill:#e8f5e8
```

#### Visualization Agent Subgraph

```mermaid
flowchart TD
    VizStart([Visualization Agent Start]) --> DecideRep{Decide Representation Type}
    
    DecideRep -->|TEXT| CreateFinalText[Create Text Response]
    DecideRep -->|TABLE| CreateFinalTable[Create Table Response]
    DecideRep -->|CHART| DecideChart[Decide Chart Type]
    
    DecideChart --> PopulateChart[Populate Chart Data]
    PopulateChart --> ValidateChart{Validate Chart Data}
    
    ValidateChart -->|Invalid| PopulateChart
    ValidateChart -->|Valid| CreateFinalChart[Create Final Chart]
    
    CreateFinalText --> VizEnd([Return Visualization])
    CreateFinalTable --> VizEnd
    CreateFinalChart --> VizEnd
    
    style VizStart fill:#e1f5fe
    style VizEnd fill:#f3e5f5
    style DecideRep fill:#fff8e1
    style ValidateChart fill:#fff8e1
    style DecideChart fill:#fff3e0
    style PopulateChart fill:#e8f5e8
    style CreateFinalText fill:#e8f5e8
    style CreateFinalTable fill:#e8f5e8
    style CreateFinalChart fill:#e8f5e8
```



- **StateGraph**: The workflow is implemented as a state machine (LangGraph), with nodes for filtering, summarizing, routing, SQL generation, execution, refinement, and visualization.
- **SQL Agent Graph**: Specialized subgraph for robust SQL generation and refinement.
- **Visualization Agent Graph**: Specialized subgraph for deciding representation and generating charts/tables.

---

## Deploy Guide

### Prerequisites

- Docker and Docker Compose installed
- Access to the project repository

### Environment Setup

**CRITICAL**: Before starting any services, you must create `.env` files for each service based on the provided `.env.example` templates.

#### 1. Create Environment Files

Navigate to each service directory and create `.env` files:

```bash
# Backend service
cp docker/dev/backend/.env.example docker/dev/backend/.env

# Database service  
cp docker/dev/database/.env.example docker/dev/database/.env

# Neo4j service
cp docker/dev/neo4j/.env.example docker/dev/neo4j/.env

# Vector database service
cp docker/dev/vectordb/.env.example docker/dev/vectordb/.env

# Any other services with .env.example files
# Check each subdirectory in docker/dev/ for additional .env.example files
```

### Deployment Steps

#### Local Development

```bash
# Navigate to development environment
cd docker/dev

# Start all services
docker compose up --build

# Or start in detached mode
docker compose up --build -d
```

### Post-Deployment Setup

#### 1. Create superuser
```bash
docker compose exec backend python manage.py createsuperuser
```

#### 2. Verify Services

Check that all services are running correctly:

```bash
# Check service status
docker compose ps

# Check logs for any errors
docker compose logs backend
docker compose logs django-db
docker compose logs neo4j
docker compose logs standalone  # Milvus
```

#### 3. Access Points

- **Main Application**: `http://localhost:8000` (or your configured port)
- **Django Admin**: `http://localhost:8000/admin`
- **Neo4j Browser**: `http://localhost:7474`

#### 4. First Startup Note

⚠️ **Important**: The first startup will be significantly slower as the system needs to download the BAAI/bge-m3 embedding model (~2GB). This is a one-time download that will be cached for subsequent startups.



