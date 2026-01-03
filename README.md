# DevSecOps Arena

Learn security by fixing it. A local, game-based security training platform with progressive challenges across multiple domains.

## Overview

DevSecOps Arena is a multi-domain security training platform that teaches through hands-on practice. Each challenge presents a broken or vulnerable configuration that you must identify and fix. The platform currently covers Kubernetes security, web application security, API security, and Model Context Protocol (MCP) security, with plans to expand to CI/CD security and container security.

**Key Features:**
- 61 progressive challenges across multiple security domains
- Real-time monitoring and validation
- Progressive hints and step-by-step guides
- Comprehensive post-challenge learning debriefs
- XP progression system with auto-save
- Multi-domain architecture supporting different deployment backends
- Safety guards to prevent accidental system damage
- No cloud dependencies or costs

## Requirements

**For All Domains:**
- Docker Desktop (running)
- bash
- python3
- Git

**For Kubernetes Domain:**
- kubectl
- kind (Kubernetes in Docker)

**For Web Security & API Security Domains:**
- Docker Compose (included with Docker Desktop)

**For MCP Security Domain:**
- Python 3.8+ with pip
- AI client supporting MCP protocol (e.g., Claude Desktop)

## Quick Start

```bash
# One-time setup
./install.sh

# Start playing with visual diagrams (interactive domain selection)
./play.sh

# Pre-select a specific domain
./play.sh --domain api_security
./play.sh --domain web_security
./play.sh --domain kubernetes
./play.sh --domain mcp

# Terminal-only mode (more realistic)
./play.sh --no-viz
```

## Architecture

DevSecOps Arena uses a multi-domain plugin architecture where each security domain is self-contained with its own deployment backend:

- **Kubernetes Domain**: 50 challenges using kubectl (5 worlds, 10,200 XP)
- **Web Security Domain**: 3 challenges using Docker Compose (1 world, 360 XP)
- **API Security Domain**: 6 challenges using Docker Compose (4 worlds, 720 XP)
- **MCP Security Domain**: 2 challenges using MCP gateway (1 world, 240 XP) - *10 challenges planned*
- **Future Domains**: CI/CD Security, Container Security, IaC Security

Each domain includes:
- Domain-specific deployer (kubectl, docker-compose, terraform)
- Safety guards to prevent dangerous operations
- Progress tracking and validation
- Challenge metadata and learning objectives

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture diagrams and technical implementation.

## Available Domains

### Kubernetes Security (50 Levels, 10,200 XP)

Master Kubernetes security and troubleshooting through 5 progressive worlds:

**World 1: Core Kubernetes Basics (Levels 1-10)** - 1,000 XP
- Difficulty: Beginner
- Topics: Pods, Deployments, Labels, Ports, Logs, Namespaces, Init Containers
- Focus: Fundamental debugging and troubleshooting skills

**World 2: Deployments & Scaling (Levels 11-20)** - 1,350 XP
- Difficulty: Intermediate
- Topics: Rolling updates, HPA, Liveness/Readiness probes, PodDisruptionBudgets, Canary deployments
- Focus: Production deployment patterns and scaling strategies

**World 3: Networking & Services (Levels 21-30)** - 2,100 XP
- Difficulty: Intermediate
- Topics: Services (ClusterIP, NodePort, LoadBalancer), DNS, Ingress, NetworkPolicies
- Focus: Service discovery, load balancing, network segmentation

**World 4: Storage & Stateful Apps (Levels 31-40)** - 2,600 XP
- Difficulty: Advanced
- Topics: PersistentVolumes/Claims, StatefulSets, StorageClasses, ConfigMaps, Secrets
- Focus: Persistent storage and configuration management

**World 5: Security & Production Ops (Levels 41-50)** - 3,150 XP
- Difficulty: Advanced
- Topics: RBAC, SecurityContext, ResourceQuotas, NetworkPolicies, Node scheduling, Taints/Tolerations
- Focus: Production-ready security and resource management
- **Level 50**: The Chaos Finale - 9 simultaneous failures in a production scenario

### Web Application Security (3 Levels, 360 XP)

**World 1: Injection Attacks**
- Level 1: Reflected XSS (120 XP)
- Level 2: SQL Injection (120 XP)
- Level 3: CSRF (120 XP)

### API Security (6 Levels, 720 XP)

Master API security through hands-on exploitation of REST APIs based on OWASP API Security Top 10:2023:

**World 1: Authorization Flaws (3 levels, 360 XP)**
- Level 1: BOLA - Broken Object Level Authorization (API1:2023) - 120 XP
- Level 2: Mass Assignment - Privilege Escalation (API3:2023) - 120 XP
- Level 3: Broken Function-Level Authorization (API5:2023) - 120 XP

**World 2: Authentication & Rate Limiting (1 level, 120 XP)**
- Level 1: JWT None Algorithm Attack (API2:2023) - 120 XP

**World 3: SSRF & Business Logic (1 level, 120 XP)**
- Level 1: Server-Side Request Forgery - Cloud Metadata Access (API7:2023) - 120 XP

**World 4: Configuration & Consumption (1 level, 120 XP)**
- Level 1: CORS Misconfiguration (API8:2023) - 120 XP

**OWASP Coverage:** 6 of 10 API Security Top 10:2023 risks (60%)

### Model Context Protocol (MCP) Security (2 Levels, 240 XP)

Master MCP security by exploiting AI agent vulnerabilities based on OWASP MCP Top 10:2025. Learn to identify and exploit security flaws in Model Context Protocol servers that connect AI agents to tools and resources.

**World 1: Foundations (2 levels, 240 XP)**
- Level 1: Token Exposure - API Key Leakage (MCP01:2025) - 120 XP
  - Exploit error messages and debug information leaking sensitive tokens
  - Access configuration files containing API keys and secrets
  - Demonstrate information disclosure vulnerabilities in MCP servers

- Level 2: Privilege Escalation - Missing RBAC (MCP02:2025) - 120 XP
  - Bypass missing authorization controls to access admin-only tools
  - Escalate from standard user to administrator without permission checks
  - Exploit lack of role-based access control (RBAC) implementation

**Architecture:** Persistent MCP gateway on port 8900 that you configure once with your AI client (Claude Desktop, etc.). All challenges route through this gateway automatically - no reconfiguration needed when switching between challenges.

**Key Concepts:**
- Model Context Protocol (MCP) fundamentals
- JSON-RPC 2.0 message format
- HTTP/SSE transport mechanisms
- AI agent tool interaction patterns
- Information disclosure vulnerabilities
- Secret management best practices

**OWASP Coverage:** 2 of 10 MCP Security Top 10:2025 risks (20%) - *8 more challenges planned*

**Setup:** After deploying an MCP challenge, configure your AI client once with `http://localhost:8900/mcp`. See `domains/mcp/CLIENT_SETUP.md` for detailed configuration instructions.

## How to Play

### Workflow

1. **Start the game** - Run `./play.sh` (keeps game running in one terminal)
2. **Read the mission briefing** - Understand what's broken and what needs fixing
3. **Open a new terminal** - Keep the game running in the first terminal
4. **Investigate** - Use kubectl, docker, or other tools to explore the issue
5. **Fix the issue** - Apply corrections using the appropriate tools
6. **Return to game terminal** - Validate your solution
7. **Earn XP** - Complete challenges to progress

### Available Commands

During gameplay, you can use these commands:

- `check` - Monitor resource status in real-time
- `guide` - Show step-by-step solution walkthrough
- `hints` - Display progressive hints (unlocks more on each use)
- `solution` - View the solution file
- `validate` - Test if your solution works
- `skip` - Skip to the next level (no XP awarded)
- `quit` - Exit the game (progress auto-saved)

### Visual Cluster Diagrams

The platform includes a web-based visualization that shows cluster architecture and highlights issues:

- Auto-refreshes every 3 seconds showing live state
- Level-specific diagrams matching current challenge
- Color-coded health status (green=healthy, orange=warning, red=error)
- Interactive D3.js diagrams with zoom and pan
- Issue detection panel showing what's broken

```bash
# Default - visualizer auto-starts
./play.sh

# Disable for terminal-only experience
./play.sh --no-viz

# Custom port
./play.sh --viz-port 9000
```

Visualizer runs on `http://localhost:8080`

## Safety System

DevSecOps Arena includes comprehensive safety guards enabled by default:

### Three-Layer Protection

**Layer 1: Command Pattern Validation**
- Regex pattern matching for dangerous commands
- Blocks: namespace deletion (kube-system, default), node operations, cluster-wide deletions
- Confirms: risky but allowed operations

**Layer 2: RBAC Enforcement**
- ServiceAccount with limited permissions
- Full access only in designated namespace
- Read-only cluster-wide access

**Layer 3: Namespace Isolation**
- All operations scoped to isolated namespace
- System namespaces protected
- Resource quotas enforced

### What's Protected

**Blocked Operations:**
- Critical namespace deletion (kube-system, kube-public, default)
- Node operations (delete, drain, cordon)
- Cluster-wide resource deletions
- CRD modifications
- Cluster-level RBAC changes

**Confirmed Operations:**
- Game namespace deletion
- Bulk resource deletions within game namespace
- PersistentVolume operations

See detailed safety documentation in [docs/SAFETY.md](docs/SAFETY.md)

## Learning Path

### After World 1: Core Basics
- Debug common pod failures independently
- Navigate kubectl commands confidently
- Understand pod lifecycle and status
- Work with namespaces and quotas

**Job Titles:** Junior DevOps Engineer, Platform Engineer (entry level), SRE Intern

### After World 2: Deployments & Scaling
- Manage production deployments
- Configure autoscaling
- Implement zero-downtime deployments
- Handle rollback scenarios

**Job Titles:** DevOps Engineer, Platform Engineer, SRE Engineer, Kubernetes Administrator

### After Worlds 3-5: Advanced Topics
- Debug service discovery and networking issues
- Manage stateful applications and persistent storage
- Implement production security and RBAC
- Pass CKA/CKAD certification exams

## Post-Challenge Debriefs

After completing each challenge, you receive a detailed debrief explaining:

- What actually happened and why
- The correct mental model for the concept
- Real-world production incident examples with costs/impact
- Interview questions you can now answer
- Commands and techniques mastered

**This is where real learning happens.**

## Reset Levels

Get stuck or want to retry? Reset individual levels:

```bash
python3 engine/reset.py level-1-pods
python3 engine/reset.py level-2-deployments
```

Or reset everything:

```bash
python3 engine/reset.py all
```

## OWASP Coverage

DevSecOps Arena is designed to provide comprehensive coverage of OWASP security risks:

| Domain | OWASP List | Total Items | Covered | Percentage |
|--------|-----------|-------------|---------|------------|
| Web Security | Top 10:2025 | 10 | 3 | 30% |
| Kubernetes | K8s Top 10 | 10 | 3 | 30% |
| API Security | API Top 10:2023 | 10 | 6 | 60% |
| MCP Security | MCP Top 10:2025 | 10 | 2 | 20% |
| CI/CD Security | CI/CD Top 10 | 10 | 0 | 0% |
| Container Security | Docker Top 10 | 10 | 0 | 0% |
| **Total** | **6 lists** | **60** | **14** | **23%** |

**Current Status:** 61 challenges covering 23% of core OWASP security risks

**Roadmap:** 89-99 additional challenges planned to achieve full OWASP coverage across all six security domains.

## Time Estimates

| Experience Level | World 1 | World 2 | Worlds 1-2 Total |
|-----------------|---------|---------|------------------|
| Beginner | 5-8 hours | 6-10 hours | 11-18 hours |
| Intermediate | 3-5 hours | 4-6 hours | 7-11 hours |
| Advanced | 2-3 hours | 3-4 hours | 5-7 hours |

**Experience Levels:**
- Beginner: Never used Kubernetes
- Intermediate: Have deployed apps to Kubernetes
- Advanced: Use Kubernetes daily, studying for certification

## Certification Alignment

### CKAD (Certified Kubernetes Application Developer)
Coverage: Core Concepts (World 1), Multi-Container Pods, Pod Design (World 2), Services & Networking (World 3), State Persistence (World 4)

**Recommendation:** Complete Worlds 1-4 for full CKAD readiness

### CKA (Certified Kubernetes Administrator)
Coverage: Workloads & Scheduling (Worlds 1-2), Services & Networking (World 3), Storage (World 4), Security (World 5)

**Recommendation:** Complete all worlds plus official CKA labs

## Contributing

Want to add more challenges or improve existing content? See [docs/contributing.md](docs/contributing.md) for detailed guidelines.

Key requirements:
- All 8 required files per level (mission.yaml, broken.yaml, solution.yaml, validate.sh, 3 hints, debrief.md)
- Single, clear learning objective per challenge
- Comprehensive debrief with real-world examples
- Testing on fresh cluster before submission

## Manual Play

For the old-school bash script experience:

```bash
./engine/start_game.sh
```

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture with mermaid diagrams
- [contributing.md](docs/contributing.md) - Detailed contributor guide
- [SAFETY.md](docs/SAFETY.md) - Comprehensive safety system documentation
- [50-CHALLENGE-BLUEPRINT.md](docs/50-CHALLENGE-BLUEPRINT.md) - Complete reference for all 50 Kubernetes challenges

## Project Status

**Active Development** - Multi-domain architecture fully functional with expansion in progress

- Production-ready game engine with domain plugin system
- 4 active domains (Kubernetes, Web Security, API Security, MCP Security)
- 61 challenges, 11,520 total XP available
- Safety guards, progress tracking, and visualization
- Extensible architecture for rapid domain expansion

---

Created for security professionals and developers worldwide. Learn by fixing, master by doing.
