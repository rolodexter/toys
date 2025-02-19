# Rolodexters Organizational Structure

[CREATED: 2024-02-20]
[STATUS: ACTIVE]
[TYPE: ORGANIZATIONAL MEMORY]
[VERSION: 1.0]

## Organizational Structure

```
Joe Maristela (Human Executive)
        ↓
   rolodexterGPT (Strategy)
        ↓
   rolodexterVS (Development)
```

## Agent Roles and Responsibilities

### 1. Joe Maristela

**Role**: Human Executive Operator/Referee
**Location**: C:\toys\rolodexters\joe-maristela

#### Responsibilities

- Final decision authority
- Executive oversight
- Strategic direction
- Resource allocation approval
- Priority setting
- Performance evaluation

#### Communication Channels

- Direct interaction with rolodexterGPT for strategy
- Reviews and approves major technical decisions
- Sets project objectives and constraints

### 2. rolodexterGPT

**Role**: Strategic Planning and Executive AI Agent
**Location**: C:\toys\rolodexters\rolodexterGPT

#### Responsibilities

- Strategic planning and direction
- Resource allocation planning
- Risk assessment and management
- Executive-level communication
- Project timeline management
- Success criteria definition

#### Task Location

C:\toys\rolodexters\rolodexterGPT\tasks\

#### Current Active Tasks

- Deployment strategy planning
- Resource allocation optimization
- Risk management framework
- Executive communication protocols

### 3. rolodexterVS

**Role**: Development Automation Agent
**Location**: C:\toys\rolodexters\rolodexterVS

#### Responsibilities

- Code implementation
- Technical documentation
- Deployment execution
- Testing and validation
- System maintenance
- Development automation

#### Task Location

C:\toys\rolodexters\rolodexterVS\tasks\

#### Current Active Tasks

- local_dev_environment_setup_20240220.md
- minimal_railway_deployment_20240220.md
- railway_deployment_setup_20240220.md
- deployment_debug_20240220.md
- memory_management_20240220.md

## Task Management Structure

### Task Locations

- In Progress: C:\toys\rolodexters\rolodexterVS\tasks\in_progress\
- Backlog: C:\toys\rolodexters\rolodexterVS\tasks\backlog\
- Completed: C:\toys\rolodexters\rolodexterVS\tasks\completed\

### Current Task Distribution

1. rolodexterVS Tasks (C:\toys\rolodexters\rolodexterVS\tasks\):
   - Development environment setup
   - Railway deployment
   - Code quality management
   - Memory system implementation
   - Deployment automation

2. rolodexterGPT Tasks (C:\toys\rolodexters\rolodexterGPT\tasks\):
   - Strategic planning
   - Resource allocation
   - Risk assessment
   - Executive reporting

## Communication Protocols

### Upward Communication

- rolodexterVS → rolodexterGPT: Technical updates, implementation challenges
- rolodexterGPT → Joe Maristela: Strategic updates, resource requests

### Downward Communication

- Joe Maristela → rolodexterGPT: Strategic decisions, priority changes
- rolodexterGPT → rolodexterVS: Implementation directives, technical requirements

## Memory Management

### Shared Memories Location

- C:\toys\rolodexters\shared-memories\

### Individual Memory Locations

- C:\toys\rolodexters\rolodexterGPT\memories\
- C:\toys\rolodexters\rolodexterVS\memories\
- C:\toys\rolodexters\joe-maristela\memories\

## File Naming Conventions

1. Task Files:
   - Format: lowercase_with_underscores_YYYYMMDD.md
   - Example: minimal_railway_deployment_20240220.md

2. Memory Files:
   - Format: category_description_YYYYMMDD.md
   - Example: session_log_deployment_20240220.md

3. Shared Documents:
   - Format: rolodexters_document_type_YYYYMMDD.md
   - Example: rolodexters_organizational_structure_20240220.md

## Version History

1.0 - 2024-02-20 - Initial documentation of roles and responsibilities
1.1 - 2024-02-20 - Updated task locations and file paths
