# K8sQuest Architecture Overview

## Platform Architecture

```mermaid
graph TD
    A[K8sQuest Platform<br/>Kubernetes Training Game System]
    B[User Interaction Layer<br/>• ./play.sh Game Launcher<br/>• Rich TUI Colorful Terminal Interface<br/>• Interactive Menus & Commands]
    C[Game Engine engine.py<br/>• Mission Management<br/>• Progressive Hint System 3 tiers<br/>• XP Tracking & Persistence<br/>• Real-time Resource Monitoring<br/>• Command Validation]
    D[Safety Module<br/>safety.py<br/>• Pattern Match<br/>• RBAC Check<br/>• Confirmation]
    E[Mission Content<br/>Worlds 1-5<br/>• 50 Levels<br/>• Broken Configs<br/>• Solutions<br/>• Hints<br/>• Debriefs]
    F[Kubernetes Cluster<br/>kind - Local<br/>• k8squest namespace<br/>• RBAC Isolation<br/>• Safe Playground]

    A --> B
    B --> C
    C --> D
    C --> E
    E --> F
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User as User Input
    participant Engine as Game Engine
    participant K8s as Kubernetes

    User->>Engine: Play Level
    Engine->>K8s: Apply broken.yaml

    User->>Engine: Request Hint
    Engine->>User: Display Hint 1

    User->>K8s: kubectl commands
    Engine->>User: Safety Check<br/>Confirm/Block

    User->>Engine: Validate Solution
    Engine->>K8s: Run validate.sh
    K8s->>Engine: Pass/Fail
    Engine->>User: Show Debrief<br/>Award XP
```

## Level Structure (Template)

```
worlds/
└── world-X-name/
    └── level-Y-topic/
        ├── mission.yaml          ← Metadata (name, XP, difficulty, concepts)
        ├── broken.yaml          ← Intentionally broken K8s resources
        ├── solution.yaml        ← (Optional) Fixed version
        ├── validate.sh          ← Pass/fail test script
        ├── hint-1.txt           ← Observation hint
        ├── hint-2.txt           ← Direction hint
        ├── hint-3.txt           ← Near-solution hint
        └── debrief.md           ← Post-mission learning
                                   • What happened
                                   • How K8s behaved
                                   • Mental model
                                   • Real-world incident
                                   • Commands learned
```

## Safety System Architecture

```mermaid
graph TB
    A[Safety Guard Layers]

    B[Layer 1: Command Pattern Validation<br/>safety.py<br/>• Regex pattern matching<br/>• Dangerous commands: delete namespace, --all flags, etc.<br/>• Severity levels: CRITICAL block | WARNING confirm<br/>• Rich UI for user feedback]

    C[Layer 2: RBAC Enforcement<br/>Kubernetes<br/>• ServiceAccount: k8squest-player<br/>• Namespace: k8squest isolated<br/>• Role: Full access ONLY in k8squest namespace<br/>• ClusterRole: Read-only cluster-wide]

    D[Layer 3: Namespace Isolation<br/>Kubernetes<br/>• All operations scoped to k8squest namespace<br/>• System namespaces protected kube-system, default<br/>• Resource quotas can limit usage]

    A --> B
    B -->|if allowed| C
    C --> D
```

## World Progression Path

```mermaid
graph TD
    W1["WORLD 1: Core Kubernetes Basics (Levels 1-10)<br/>Difficulty: Beginner<br/>XP: 1,450<br/>Status: COMPLETE<br/><br/>Topics: Pods, Deployments, Labels, Ports, Logs,<br/>Namespaces, Init Containers"]

    W2["WORLD 2: Deployments & Scaling (Levels 11-20)<br/>Difficulty: Intermediate<br/>XP: 2,000<br/>Status: BLUEPRINTED<br/><br/>Topics: Rolling Updates, HPA, Probes, Rollbacks,<br/>Blue-Green, Canary, PDB, StatefulSets"]

    W3["WORLD 3: Networking & Services (Levels 21-30)<br/>Difficulty: Intermediate<br/>XP: 2,300<br/>Status: BLUEPRINTED<br/><br/>Topics: Services, Ingress, DNS, NetworkPolicy,<br/>Session Affinity, Cross-namespace"]

    W4["WORLD 4: Storage & Stateful Apps (Levels 31-40)<br/>Difficulty: Advanced<br/>XP: 2,600<br/>Status: BLUEPRINTED<br/><br/>Topics: PV/PVC, StatefulSets, StorageClass, ConfigMaps,<br/>Secrets, Volume Permissions"]

    W5["WORLD 5: Security & Production Ops (Levels 41-50)<br/>Difficulty: Advanced<br/>XP: 3,150<br/>Status: BLUEPRINTED<br/><br/>Topics: RBAC, SecurityContext, ResourceQuotas,<br/>LimitRanges, PSP, Node Affinity, Taints,<br/>CHAOS FINALE Level 50"]

    W1 --> W2
    W2 --> W3
    W3 --> W4
    W4 --> W5
```

## Technology Stack

| Component           | Technology                              |
|---------------------|----------------------------------------|
| Game Engine         | Python 3.x                              |
| UI Framework        | rich (Python TUI library)               |
| Kubernetes          | kind (Kubernetes in Docker)             |
| Container Runtime   | Docker Desktop                          |
| CLI Tool            | kubectl                                 |
| Data Format         | YAML (configs), JSON (progress)         |
| Scripting           | Bash (automation, validation)           |
| Testing             | Python unittest-style (pytest patterns) |
| Version Control     | Git (.gitignore configured)             |
| Isolation           | Python venv (dependency management)     |

## Key Metrics Dashboard

**K8sQuest Statistics**

| Metric                  | Value                               |
|------------------------|-------------------------------------|
| Total Levels           | 50 (10 complete, 40 blueprinted)   |
| Total XP Available     | 11,500                              |
| Worlds                 | 5                                   |
| Lines of Code (Engine) | ~1,500                              |
| Lines of Documentation | ~3,000+                             |
| Safety Test Coverage   | 20 tests, 100% passing              |
| Setup Time             | ~5 minutes                          |
| Avg Level Duration     | 10-15 minutes                       |
| Learning Outcomes      | CKA exam preparation level          |

Created for Kubernetes learners worldwide