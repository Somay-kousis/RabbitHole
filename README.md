# RabbitHole

RabbitHole is an AI exploration engine for understanding complex topics through multiple perspectives, timelines, contradictions, and knowledge graphs.

Instead of giving a single answer, RabbitHole helps users explore how events, people, policies, incentives, and narratives connect.

## Core Modes

### 1. Courtroom

A multi-agent debate system where different roles argue around a topic.

Example roles:

* Company / billionaire side
* Environmental activist
* Honest lawyer
* Corrupt officer
* Judiciary
* Journalist
* Local citizen

The goal is not to declare one winner immediately, but to expose incentives, evidence, weak arguments, and hidden assumptions.

### 2. Timeline

Builds a chronological chain of events.

Example:

```txt
2000 → lung cancer deaths reported
2006 → local protests begin
2026 → company expansion / policy change
```

This helps users see how a topic evolved instead of treating it as one isolated incident.

### 3. Contradiction Finder

Takes a claim, post, tweet, screenshot, or statement and checks it against previous statements, records, meetings, and available evidence.

Goal:

```txt
What was said?
When was it said?
What contradicts it?
How strong is the contradiction?
```

### 4. Knowledge Graph

Shows what must be understood before understanding the main issue.

Example:

```txt
To understand Policy X:
- Understand Incident Y
- Understand Company Z
- Understand the tradeoff being claimed
- Understand who benefits from the tradeoff
```

## Current Build Plan

### Phase 0 — Project Skeleton

* Backend folder structure
* Documentation
* Docker placeholders
* Test folders
* Scripts folder

### Phase 1 — LangGraph Skeleton + Ollama

* Use Ollama/local LLM
* Build graph with stub nodes
* Keep all modes as pass-through nodes first
* Test every graph path before adding complex logic

### Phase 2 — Research Layer

* Add basic retrieval
* Add LlamaIndex
* Add source collection
* Add evidence cards

### Phase 3 — Feature Modes

Build modes one by one:

1. Timeline
2. Courtroom
3. Knowledge Graph
4. Contradiction Finder

### Phase 4 — Memory

Add memory for:

* User interests
* Previous explorations
* Recurring entities
* Trusted and distrusted sources
* Saved rabbit holes

### Phase 5 — Prompt Optimization

Use DSPy for:

* Claim classification
* Source grading
* Debate quality
* Contradiction detection
* Final answer formatting

### Phase 6 — API

Expose the system using FastAPI.

Planned endpoints:

```txt
/rabbit/start
/rabbit/continue
/rabbit/timeline
/rabbit/courtroom
/rabbit/contradiction
/rabbit/graph
```

### Phase 7 — Infrastructure

* Docker
* Docker Compose
* Redis
* Postgres
* Nginx
* Terraform later

## Repository Structure

```txt
RabbitHole/
├── app/
│   ├── api/
│   ├── core/
│   ├── general/
│   ├── courtroom/
│   ├── timeline/
│   ├── contradiction_finder/
│   └── knowledge_graph/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── vectorstores/
│
├── docs/
│   ├── architecture.md
│   ├── decision.md
│   └── roadmap.md
│
├── infra/
│   ├── postgres/
│   └── terraform/
│
├── scripts/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Tech Stack

Current / planned:

* Python
* LangGraph
* LangChain
* LlamaIndex
* Ollama
* FastAPI
* Redis
* Postgres
* Docker
* Terraform
* DSPy

## Status

Current status: **backend scaffold created**

Next step:

```txt
Build the LangGraph skeleton with stub nodes.
```

## Philosophy

RabbitHole is not a chatbot that says:

```txt
Here is the answer.
```

It is an exploration system that says:

```txt
Here are the narratives.
Here is the timeline.
Here are the contradictions.
Here are the incentives.
Here is what you need to understand next.
```
