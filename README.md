# FALCON: Fault-handling Agentic LLMs for Controlled Operations 🚀

[![Python Version](https://img.shields.io/badge/python-3.12%2B-brightgreen.svg)](https://www.python.org/downloads/release/python-3120/)
[![OpenModelica](https://img.shields.io/badge/OpenModelica-4.0.0-cyan)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview
**FALCON** is a research prototype that explores the integration of **Large Language Models (LLMs)** with simulation-based **Digital Twins** for autonomous fault handling in process plants. Specifically, it evaluates whether LLM agents can interpret system representations like **natural language descriptions**, **OpenModelica code**, and **engineering diagrams** to generate safe and effective **corrective control actions**.

This repository supports a closed-loop interaction between LLM-based agents and a plant simulation model built in OpenModelica, enabling both reasoning and validation of control actions under fault conditions.

📌 **Note:** The OpenModelica model used in this project is adapted from the benchmark process plant simulation introduced in [Ehrhardt et al. (2022)](https://doi.org/10.1109/ETFA52439.2022.9921462) and can be found in the corresponding [original repository](https://github.com/j-ehrhardt/benchmark-for-diagnosis-reconf-planning). We thank the authors for making it publicly available.

---

## Representing Process Plants for LLM Agents 🧠

FALCON examines how LLMs perform when prompted with different representations of a chemical process plant. These include:

### 🔤 1. **Text-Based Descriptions**
A concise, natural language description of the plant’s **structure**, **function**, and **behavior**. This format provides a human-readable summary, often more accessible for LLMs to reason over due to the linguistic nature of their training.

Example prompt snippet:
```
The system consists of four tanks: B201–B204. Liquid flows through controllable valves and is pumped from B201–B203 into B204.
```

### 📄 2. **OpenModelica Code Representation**
Raw Modelica code that formally defines plant components and their dynamic interactions. While structurally precise, this representation proved more difficult for LLMs to interpret due to limited exposure to Modelica in their training corpus.

Example excerpt:
```modelica
model Plant
  Tank B201, B202, B203, B204;
  Valve valve_in0, valve_in1;
  ...
equation
  connect(valve_in0.outlet, B201.inlet);
  ...
end Plant;
```

### 🛠️ 3. **P&ID + State Graph Representation**
This format uses a **vectorized representation** of engineering diagrams:
- A **P&ID (Piping and Instrumentation Diagram)** that encodes the plant's structure as a graph (nodes and edges), representing tanks, valves, and pumps.
- A **State Graph** that defines the expected **control sequence** and associated **transition conditions** (e.g., tank level thresholds).

Example state transition:
```
fill_tank_B201 → fill_tank_B202 [if B201 > 0.032m]
```

This hybrid approach brings together both structural and behavioral context in a graph-like form, which the LLM can interpret with moderate effectiveness.

---

## Features ✨
- 🧠 **LLM Reasoning Loop**: Modular agentic framework using GPT-4o/4o-mini to plan, validate, and reprompt.
- 🔁 **Closed-Loop Simulation**: OpenModelica is orchestrated from Python to simulate actions and verify outcomes.
- 🧪 **Fault Scenarios**: Test fault-handling logic in the presence of plant anomalies (e.g., clogging).
- 🧩 **Prompt Engineering**: Flexible design to insert structured or unstructured plant data into LLM prompts.

---

## Getting Started 🚀

### Prerequisites
- **OpenModelica** v1.13+ ([Installation Guide](https://openmodelica.org/))
- **Python >= 3.10 && <3.13** ([Python Download](https://www.python.org/))

### Installation
```bash
git clone https://github.com/AISL-at-Imperial-College-London/fault-handling-agentic-llms-for-controlled-operations.git
cd fault-handling-agentic-llms-for-controlled-operations

python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

## Project Structure 📁
```
├── code/                       # Python orchestration scripts
│   ├── crew/                   # CrewAI prompt templates and roles        
│   ├── logs/                   # Logs of LLM-agent interactions
│   ├── results/                # Control Performance Results
│   ├── simulation/             # Simulation files
│   ├── main.py                 # Script to initiate LLM based control actions
│   └── validation_script.py    # Script to validate the results from digital twin
├── models/          # Modelica components (source: benchmark repo)
└── README.md        # This file
```

---

## Usage ⚙️

### Run OpenModelica Simulation
```bash
python code/simulation/mixer_sim.py
```

### Start LLM-Based Control Loop
```bash
python code/main.py
```

---

## Results and Case Studies 📊

We evaluate LLM performance across the three representation formats. 


### Table: Performance of GPT-4o across different input representations

| **Metrics**                    | **Text** | **Modelica Code** | **SM + P&ID** |
|-------------------------------|:--------:|:-----------------:|:-------------:|
| **Actions Summary**           |          |                   |               |
| &nbsp;&nbsp;No. of Actions    |   15     |        12         |      14       |
| &nbsp;&nbsp;No. of Expected Actions | 15  |        15         |      15       |
| **Action Quality**            |          |                   |               |
| &nbsp;&nbsp;No. of Correct Actions | 15  |        12         |      14       |
| &nbsp;&nbsp;No. of Incorrect Valve Actions | 0 |     0           |      0        |
| &nbsp;&nbsp;No. of Incorrect Pump Actions | 0 |     0           |      0        |
| &nbsp;&nbsp;No. of Missed Valve Actions   | 0 |     0           |      0        |
| &nbsp;&nbsp;No. of Missed Pump Actions    | 0 |     3           |      1        |
| **Efficiency**                |          |                   |               |
| &nbsp;&nbsp;No. of Reprompts  |   1      |        6          |      5        |
| **Token Usage**               |          |                   |               |
| &nbsp;&nbsp;No. of Tokens (K) | 16.2     |       81.4        |     27.2      |

---

### Table: Performance of GPT-4o-mini across different input representations

| **Metrics**                    | **Text** | **Modelica Code** | **SM + P&ID** |
|-------------------------------|:--------:|:-----------------:|:-------------:|
| **Actions Summary**           |          |                   |               |
| &nbsp;&nbsp;No. of Actions    |   13     |        14         |      14       |
| &nbsp;&nbsp;No. of Expected Actions | 15  |        15         |      15       |
| **Action Quality**            |          |                   |               |
| &nbsp;&nbsp;No. of Correct Actions | 13  |        12         |      13       |
| &nbsp;&nbsp;No. of Incorrect Valve Actions | 0 |     2           |      1        |
| &nbsp;&nbsp;No. of Incorrect Pump Actions | 0 |     0           |      0        |
| &nbsp;&nbsp;No. of Missed Valve Actions   | 0 |     0           |      0        |
| &nbsp;&nbsp;No. of Missed Pump Actions    | 2 |     3           |      2        |
| **Efficiency**                |          |                   |               |
| &nbsp;&nbsp;No. of Reprompts  |   6      |       10          |      9        |
| **Token Usage**               |          |                   |               |
| &nbsp;&nbsp;No. of Tokens (K) | 33.9     |      113.0        |     40.5      |

- ✅ **Text-Based**: Highest accuracy and fewest reprompts.
- 🔧 **Modelica Code**: Correct but more error-prone; hard to parse.
- 🧩 **P&ID + State Graph**: Balanced; rich structural detail with moderate complexity.

---

## Citation & Contact 📬

For academic use, please cite:

```
@article{gill2025llm,
  title={Leveraging LLM Agents and Digital Twins for Fault Handling in Process Plants},
  author={Gill, Milapji Singh and Vyas, Javal and Markaj, Artan and Gehlhoff, Felix and Mercangöz, Mehmet},
  journal={arXiv preprint arXiv:},
  year={2025}
}
```

**Contact:**  
Javal Vyas – j.vyas24@imperial.ac.uk  
LinkedIn: [Javal Vyas](https://www.linkedin.com/in/javal-vyas/)
