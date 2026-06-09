# ⚡ Super Yooper Gemini Auto-Researcher

An autonomous, long-horizon software engineering optimization system driven by Gemini models. This repository implements a robust, fault-tolerant **Karpathy Loop** (Propose → Code → Run → Evaluate → Git Commit/Rollback) designed specifically to run continuously for weeks at a time on zero-cost infrastructure without exhausting local system resources.

## 📐 Architectural Philosophy

Instead of relying on heavy, resource-intensive agentic graph frameworks or local vector databases that cause memory bloat, this architecture splits the operational stack cleanly between cloud intelligence and local git transactional states. 

It is specifically engineered to respect hardware constraints—fully capable of executing seamlessly on a machine with as little as **4 GB of RAM** (such as an HP 15 laptop) or inside a **GCP Always-Free `e2-micro` instance**.


```

```
                   [ Google Gemini Cloud API ]
                                │
                    (Generates Code Mutations)
                                ▼
[ Remote Ubuntu VM ] ──> [ Python Wrapper Loop ] ──> [ Immutable Evaluator ]
     (GCP Free Tier)             │                             │
                            (Git Commit)                 (Test Execution)
                                 ▼                             ▼
[ Chrome Dashboard ] <── [ GitHub Repository ] <───── [ Success / Rollback ]

```

(Static Telemetry UI)      (Passive Data Router)

```

## 🛠️ Complete System Specification

### 1. The Core State Machine (`loop.py`)
A stateless Python wrapper handling transaction orchestration. It manages API payloads, reads local states, handles filesystem boundaries, and implements rigorous local resource optimization (`del` variable pipelines coupled with explicit `gc.collect()` sweeps) to prevent memory leaks over thousands of iterations.

### 2. The Immutable Judge (`evaluator.py`)
The testing harness defining success. The agent is strictly forbidden from editing this asset. It executes the mutated code under a strict 30-second isolation timeout, measuring execution latency, test assertion compliance, and cyclomatic code complexity.

### 3. Git-as-Memory Pipeline
We eliminate heavy memory databases by using Git as our transactional state tracking engine:
* **On Success:** The code is retained and a checkpoint commit is logged.
* **On Failure/Regression:** The runtime throws a safe error, and the wrapper executes a hard rollback: `git reset --hard HEAD~1` to keep the workspace completely clean.

### 4. Zero-Config Remote Telemetry (`dashboard.html`)
A minimalist, dark-mode browser dashboard styled around Google's developer aesthetic. The dashboard requires **zero hosting configurations**. It runs completely locally inside Chrome (`file:///` protocol) and polls GitHub's free public raw API to stream runtime stats and terminal logs dumped by the runner into a stateless `status.json` file.

## 🗂️ Repository Structure

```text
├── software_under_test.py   # The target module the agent is optimizing
├── evaluator.py             # Immutable testing and benchmarking harness
├── loop.py                  # Python state machine wrapper & API runner
├── instructions.md          # System directives and execution guardrails for Gemini
├── status.json              # Real-time state metrics pushed automatically by the loop
└── dashboard.html           # Beautiful visual chrome panel for monitoring telemetry

```

## 🚀 Recommended Low-RAM Deployment (GCP Free Tier)

To offload execution entirely from physical laptop hardware, configure this loop to run indefinitely inside Google Cloud Platform's Always Free perimeter:

1. Provision an **Compute Engine `e2-micro` Virtual Machine** (1 GB RAM, 30 GB Standard Persistent Disk) in `us-central1`, `us-east1`, or `us-west1`.
2. Install a clean **Ubuntu Server Minimal** image to avoid any graphical interface overhead (idle RAM consumption remains $< 150\text{ MB}$).
3. Configure your Gemini API key inside Google AI Studio to separate model inference tokens from cloud billing structures.
4. Clone this repository onto the instance and spin up your loop inside a persistent background terminal environment using **`tmux`**:
```bash
tmux new -s ai-agent
python3 loop.py

```


5. Press `Ctrl + B`, then `D` to detach. You can now close your laptop and shut down Chrome; the agent will run autonomously in the cloud for weeks.

## 🛡️ Built-in Circuit Breakers

* **Hardware Interruption:** Automatic evaluation stops if system thermal boundaries are exceeded or hardware constraints throttle.
* **Algorithmic Stagnation Escalation:** The loop uses high-speed **Gemini 2.5 Flash** for rapid, iterative sweeps. If the codebase faces an algorithmic plateau for more than 5 consecutive cycles, the wrapper escalates to a deep-reasoning instance of **Gemini 2.5 Pro** with an elevated `thinkingLevel` to resolve the bottleneck before returning to Flash execution.

```

---

You can drop the text above straight into your repository's description input and your main markdown file. It explicitly presents your professional background in systems architecture and DevOps by focusing heavily on resource management, transactional engineering, and cloud deployment boundaries.

```
