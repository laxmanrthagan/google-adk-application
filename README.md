# Interview Studio

A one-page interview-preparation workbench built with React and Google's official Python Agent Development Kit. It demonstrates nine distinct ADK agent patterns and runs offline in mock mode by default.

## Requirements

- Python 3.10 or newer
- Node.js 20.19 or newer
- npm

The backend pins `google-adk==2.11.0`. The app was verified with that SDK on Python 3.14.6.

## Run locally

In one terminal, install and start the API:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend_adk/requirements.txt
uvicorn backend_adk.main:app --reload --port 8000
```

In a second terminal, start the React workbench:

```sh
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (normally `http://localhost:5173`). `AI_PROVIDER=mock` is the default; no credentials or cloud project are needed. The API is available at `http://localhost:8000`, with its OpenAPI docs at `/docs`.

## Enable Gemini

Set `AI_PROVIDER=gemini` and provide a Gemini Developer API key before starting the backend:

```sh
export AI_PROVIDER=gemini
export GOOGLE_API_KEY="your-key"
export GEMINI_MODEL=gemini-2.5-flash
uvicorn backend_adk.main:app --reload --port 8000
```

`GEMINI_API_KEY` is also accepted. Keep keys in the server environment; they are never sent to the browser. The Search agent uses ADK's Google Search tool and requires a compatible Gemini model.

## Enable Vertex AI

Configure Google Cloud Application Default Credentials, then start with:

```sh
gcloud auth application-default login
export AI_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION=us-central1
export GEMINI_MODEL=gemini-2.5-flash
uvicorn backend_adk.main:app --reload --port 8000
```

Enable the Vertex AI API and grant the identity model access. BigQuery additionally requires BigQuery read permissions and a configured project/ADC. The BigQuery toolset is configured to block writes. Set `AI_PROVIDER=mock` again to return to offline mode.

## Agent map

| Workbench agent | ADK capability | Interview-preparation task |
| --- | --- | --- |
| Interview brief | `Agent` | Prioritized preparation brief |
| Answer coach | LLM-powered `Agent` | Specific coaching for a draft answer |
| Study plan | `SequentialAgent` | Role signals, likely questions, then practice plan |
| Role analysis | `ParallelAgent` | Concurrent skill, question, and risk analyses |
| Answer rehearsal | `LoopAgent` | Bounded critique-and-revision loop |
| System design | Custom `BaseAgent` | Conditional architecture/behavioral routing |
| Company research | Google Search tool | Current, grounded research |
| Skill match | Local function tool | Transparent keyword overlap, not a qualification score |
| Question trends | BigQuery `BigQueryToolset` | Read-only interview-question exploration |

ADK 2.11.0 marks `SequentialAgent`, `ParallelAgent`, and `LoopAgent` as deprecated in favor of graph-based `Workflow`. This project uses those template agents intentionally because demonstrating those specific agent types is part of the workbench; expect SDK deprecation warnings when those three live builders are instantiated.

Every request, including mock requests, runs through Google ADK agents, an ADK `Runner`, and an ADK session service. Mock mode supplies an ADK `BaseLlm` implementation and local ADK function tools; Search prompts and BigQuery rows are explicitly labeled as illustrative, and no live web search or cloud query occurs. Recent runs, including the role context used for those runs, are stored in this browser's local storage and are not uploaded to a separate history service.