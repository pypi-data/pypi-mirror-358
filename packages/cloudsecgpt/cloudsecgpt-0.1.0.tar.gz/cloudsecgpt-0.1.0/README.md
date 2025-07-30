<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/MrCloudSec/CloudSecGPT/blob/main/docs/images/logo-horizontal-dark.png" />
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/MrCloudSec/CloudSecGPT/blob/main/docs/images/logo-horizontal-light.png" />
    <img src="https://github.com/MrCloudSec/CloudSecGPT/blob/main/docs/images/social-preview.png" alt="CloudSecGPT logo" width="70%">
  </picture>
</p>

**CloudSecGPT** super‑charges raw cloud‑security findings with AI.
Give it an OCSF/ASFF/Parquet export – or pull live from **AWS Security Hub**, **GCP Security Command Center**, or **Azure Defender** – and it spits out:

* **Risk score (1‑10)** for every finding
* One‑line **summary**, business **impact** & concise **remediation**
* Copy‑‑pasteable **CLI fix command**
* **Groups** to slash alert fatigue
* A gorgeous self‑contained **HTML report**
* An interactive **chat** so you can ask “_why?_” & “_how do I fix this?_” on the fly

---

## ✨ Feature Matrix

| Pillar | Highlights |
|--------|------------|
| **Sources** | • JSON-OCSF/JSON-ASFF/Parquet<br>• `--security-hub` live pull<br>• `--gcp-scc` org / folder / project<br>• `--azure-defender` subscription |
| **Analyze** | Enriches every finding → `risk_score`, `summary`, `why`, `cli_fix`, `remediation` |
| **Groups** | Groups by *resource_type + summary* → noise ↓, signal ↑ |
| **Outputs** | 3 artefacts in `--out` dir:<br>`analyzed.csv` · `grouped.csv` · `report.html` |
| **Chat** | `cloudsecgpt chat` → conversational Q&A with full context |
| **LLM back‑ends** | `openai` · `bedrock` · `ollama` (local) · **MCP** client |
| **Smart cache** | File + prompt hashed (BLAKE2b) → no double billing |
| **Progress UI** | Tidy Rich bar with live findings counter |

---

## 📦 Install

```bash
pip install cloudsecgpt
```

(Requires Python ≥ 3.9)

Developers:

```bash
git clone https://github.com/MrCloudSec/CloudSecGPT.git
cd CloudSecGPT && poetry install
```

## ⚙️ Quick start

```bash
export OPENAI_API_KEY=...
cloudsecgpt analyze --file path/to/JSON-OCSF/JSON-ASFF/Parquet \
  [--provider openai] [--model gpt-4o-mini] \
  [--batch 20] [--workers 8] \
  [--out ./out]
```

* `./out/analyzed_<timestamp>.csv` – full table sorted by highest risk
* `./out/grouped_<timestamp>.csv` – de‑duplicated view
* `./out/report_<timestamp>.html`  – share‑ready report (logo, chart, sticky headers)

![analyze.gif](docs/images/analyze.gif)

### Live pulls

```bash
# AWS Security Hub via AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and optional AWS_SESSION_TOKEN env vars
cloudsecgpt analyze --security-hub [-o out/]

# GCP SCC (auto‑detect single org) via GOOGLE_APPLICATION_CREDENTIALS env var or gcloud auth application-default login
cloudsecgpt analyze --gcp-scc [org/folder/projectID] [-o out/]

# Azure Defender (single subscription auto) via AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID env vars or az login
cloudsecgpt analyze --azure-defender [subscriptionID] [-o out/]
```

![security-hub.gif](docs/images/securityhub.gif)

### Chat mode

```bash
# Chat with the context of a file
cloudsecgpt chat findings.json

# Chat with the context of Security Hub via AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and optional AWS_SESSION_TOKEN env vars
cloudsecgpt chat --security-hub

# Chat with the context of GCP SCC via GOOGLE_APPLICATION_CREDENTIALS env var or gcloud auth application-default login
cloudsecgpt chat --gcp-scc

# Chat with the context of Azure Defender via AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID env vars or az login
cloudsecgpt chat --azure-defender
```

Ask anything – context is streamed from the analyzed findings.

![chat.png](docs/images/chat.png)

---

## 🐳 Docker

```bash
# Pull and run
docker run --rm -v $(pwd):/data -e OPENAI_API_KEY=your_key \
  mrcloudsec/cloudsecgpt:latest analyze /data/findings.parquet -o /data/out
```

```bash
# Build locally
git clone https://github.com/MrCloudSec/CloudSecGPT.git
cd CloudSecGPT && docker build -t cloudsecgpt .
docker run --rm -v $(pwd):/data cloudsecgpt analyze /data/findings.parquet -o /data/out
```

---

## 🔌 Providers

| Flag | Notes |
|------|-------|
| **openai**  | `OPENAI_API_KEY` env var |
| **bedrock** | standard AWS creds via `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and optional `AWS_SESSION_TOKEN` env vars |
| **ollama**  | `ollama serve` on `localhost:11434` |
| **mcp**     | Any Model‑Context‑Protocol host (`--host` + optional `--api-key`) |

---

## 🧑‍💻 Extend

```python
class MyModel:
    def call(self, messages: list[dict[str, str]]) -> str:
        ...
```

Register it in `core.get_model()` – done.

---

## 🛡️ Why CloudSecGPT?

* 👀 Single‑pane view across **AWS / Azure / GCP / K8s**
* ⚡ Cut triage time with instant clustering
* 🧠 Explain *why it matters* – not just “what”
* 🗣️ Talk to your findings like ChatGPT
* 👐 Open‑source, pluggable, works offline with local LLMs

---

## 🤝 Contributing

PRs & issues welcome! Pre‑commit hooks run **Black**, **Flake8** & **Bandit**.

---

## 📜 License

Apache‑2.0 © 2025 [**@MrCloudSec**](https://www.linkedin.com/in/mistercloudsec/)
