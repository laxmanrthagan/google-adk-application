import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  BookOpenCheck,
  Check,
  ChevronDown,
  CircleHelp,
  Clock3,
  Copy,
  Database,
  FileSearch,
  GitBranch,
  Layers3,
  ListChecks,
  LoaderCircle,
  MessageSquareText,
  RotateCcw,
  Search,
  Sparkles,
  Workflow,
  X,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
const HISTORY_KEY = "interview-studio-history";
const SAMPLE = {
  role: "Staff Platform Engineer",
  company: "Northstar",
  seniority: "Staff",
  job_description:
    "We are looking for a platform engineer to design reliable cloud services and internal APIs. You will lead architecture reviews, improve service observability and incident response, and partner with product teams to make technical trade-offs. Experience with Python, distributed systems, Kubernetes, and mentoring engineers is valuable.",
  question: "Design a reliable event platform for multiple product teams.",
  answer:
    "I led a migration from a shared service to separate APIs. I worked with three teams to decide how we would split ownership and set up better alerts. The new setup reduced incidents and made it easier for teams to deploy.",
};
const LOCAL_AGENTS = [
  { id: "basic", name: "Interview brief", kind: "Basic Agent", description: "A concise, direct interview-preparation response.", task: "Generate a focused interview brief", color: "coral" },
  { id: "llm", name: "Answer coach", kind: "LLM Agent", description: "Turns an interview answer into specific, actionable coaching.", task: "Coach an interview answer", color: "green" },
  { id: "sequential", name: "Study plan", kind: "Sequential Workflow", description: "Moves through role analysis, question selection, and a study plan in order.", task: "Build a role-specific study plan", color: "yellow" },
  { id: "parallel", name: "Role analysis", kind: "Parallel Workflow", description: "Inspects skills, interview risks, and likely questions concurrently.", task: "Analyze the role from three angles", color: "blue" },
  { id: "loop", name: "Answer rehearsal", kind: "Loop Workflow", description: "Iteratively reviews and improves an answer with a bounded revision loop.", task: "Refine an interview answer", color: "coral" },
  { id: "custom", name: "System design", kind: "Custom Agent", description: "Routes a design prompt through explicit architecture decisions and trade-offs.", task: "Work through a system design prompt", color: "green" },
  { id: "search", name: "Company research", kind: "Google Search Agent", description: "Finds current company context to ground interview preparation.", task: "Research a company or interview topic", color: "yellow" },
  { id: "tools", name: "Skill match", kind: "Function Tool Agent", description: "Uses a local function to compare a job description with your experience.", task: "Map experience to role requirements", color: "blue" },
  { id: "bigquery", name: "Question trends", kind: "BigQuery Agent", description: "Queries interview-question data with ADK's BigQuery integration.", task: "Explore interview-question trends", color: "green" },
];
const AGENT_ICONS = {
  basic: Sparkles,
  llm: MessageSquareText,
  sequential: ListChecks,
  parallel: Workflow,
  loop: RotateCcw,
  custom: GitBranch,
  search: Search,
  tools: Activity,
  bigquery: Database,
};

function readHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function App() {
  const [agents, setAgents] = useState(LOCAL_AGENTS);
  const [selectedId, setSelectedId] = useState("sequential");
  const [form, setForm] = useState(SAMPLE);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(readHistory);
  const [provider, setProvider] = useState("mock");
  const [serverOnline, setServerOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [copied, setCopied] = useState(false);

  const selectedAgent = agents.find((agent) => agent.id === selectedId) || agents[0];

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch(`${API_BASE}/api/agents`).then((response) => {
        if (!response.ok) throw new Error("Agent catalog unavailable");
        return response.json();
      }),
      fetch(`${API_BASE}/api/health`).then((response) => {
        if (!response.ok) throw new Error("API unavailable");
        return response.json();
      }),
    ])
      .then(([catalog, health]) => {
        if (!active) return;
        setAgents(catalog.agents);
        setProvider(health.provider);
        setServerOnline(true);
      })
      .catch(() => {
        if (active) setServerOnline(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 8)));
  }, [history]);

  useEffect(() => {
    if (!notice) return undefined;
    const timeout = window.setTimeout(() => setNotice(""), 2400);
    return () => window.clearTimeout(timeout);
  }, [notice]);

  function changeField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function runPreparation(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await fetch(`${API_BASE}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, agent_id: selectedId }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "The preparation run could not be completed.");
      }
      const saved = { ...payload, id: crypto.randomUUID(), createdAt: new Date().toISOString(), form };
      setResult(saved);
      setProvider(payload.provider);
      setServerOnline(true);
      setHistory((current) => [saved, ...current.filter((item) => item.agent.id !== selectedId)].slice(0, 8));
    } catch (runError) {
      setError(runError.message || "The API could not be reached.");
    } finally {
      setLoading(false);
    }
  }

  function restoreRun(item) {
    setSelectedId(item.agent.id);
    setResult(item);
    if (item.form) setForm(item.form);
    setError("");
  }

  async function copyResult() {
    if (!result) return;
    await navigator.clipboard.writeText(result.response);
    setCopied(true);
    setNotice("Copied to clipboard");
    window.setTimeout(() => setCopied(false), 1800);
  }

  function downloadResult() {
    if (!result) return;
    const markdown = `# ${result.agent.name}\n\n${result.response}\n`;
    const url = URL.createObjectURL(new Blob([markdown], { type: "text/markdown" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${result.agent.id}-interview-prep.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const ActiveIcon = AGENT_ICONS[selectedId] || Sparkles;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="Interview Studio home">
          <span className="brand-mark"><span /><span /><span /></span>
          <span className="brand-name">fieldnotes<span>.</span></span>
        </a>

        <div className="sidebar-label">PREPARATION</div>
        <nav className="agent-nav" aria-label="Preparation agents">
          {agents.map((agent, index) => {
            const Icon = AGENT_ICONS[agent.id] || Sparkles;
            return (
              <button
                className={`agent-link ${selectedId === agent.id ? "is-selected" : ""}`}
                key={agent.id}
                onClick={() => {
                  setSelectedId(agent.id);
                  setResult(null);
                  setError("");
                }}
                aria-current={selectedId === agent.id ? "page" : undefined}
              >
                <span className={`agent-link-icon tone-${agent.color}`}><Icon size={16} strokeWidth={1.8} /></span>
                <span className="agent-link-copy"><span>{agent.name}</span><small>{agent.kind}</small></span>
                <span className="agent-index">{String(index + 1).padStart(2, "0")}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-label history-label">RECENT RUNS</div>
          {history.length ? (
            <div className="history-list">
              {history.slice(0, 4).map((item) => (
                <button className="history-item" key={item.id} onClick={() => restoreRun(item)}>
                  <Clock3 size={13} />
                  <span>{item.agent.name}</span>
                  <span className="history-time">{new Date(item.createdAt).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span>
                </button>
              ))}
            </div>
          ) : <p className="history-empty">Your recent sessions will appear here.</p>}
          <div className="sidebar-account">
            <div className="avatar">S</div>
            <div><strong>Session workspace</strong><span>Private on this device</span></div>
            <ChevronDown size={15} />
          </div>
        </div>
      </aside>

      <main className="main-panel" id="top">
        <header className="topbar">
          <div className="breadcrumb"><span>WORKSPACE</span><span className="breadcrumb-slash">/</span><strong>Interview prep</strong></div>
          <div className="topbar-right">
            <span className={`connection-state ${serverOnline ? "connected" : "disconnected"}`}>
              <span className="state-dot" />{serverOnline ? "API connected" : "API offline"}
            </span>
            <span className="provider-badge"><span className="provider-glyph">G</span>{provider}</span>
            <button className="icon-button help-button" title="About this workspace" aria-label="About this workspace"><CircleHelp size={17} /></button>
          </div>
        </header>

        <section className="page-heading">
          <div className="eyebrow"><span className="eyebrow-rule" />YOUR NEXT CONVERSATION</div>
          <div className="heading-row">
            <div>
              <h1>Make the work <em>count.</em></h1>
              <p>Build a sharper story for the role you want.</p>
            </div>
            <button className="text-button sample-button" onClick={() => { setForm(SAMPLE); setNotice("Sample role loaded"); }}>
              <BookOpenCheck size={16} /> Load sample
            </button>
          </div>
        </section>

        <div className="workbench">
          <section className="input-column" aria-label="Interview context">
            <div className="section-title-row">
              <div className="section-number">01</div>
              <div><h2>Set the scene</h2><p>Give your agent the context that matters.</p></div>
            </div>

            <form className="context-form" onSubmit={runPreparation}>
              <div className="field-row">
                <label className="field"><span>ROLE</span><input name="role" value={form.role} onChange={changeField} placeholder="Senior software engineer" maxLength={160} /></label>
                <label className="field"><span>COMPANY</span><input name="company" value={form.company} onChange={changeField} placeholder="Company name" maxLength={160} /></label>
              </div>
              <label className="field seniority-field"><span>LEVEL</span>
                <select name="seniority" value={form.seniority} onChange={changeField}>
                  {["Intern", "Junior", "Mid-level", "Senior", "Staff", "Principal", "Executive"].map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
              <label className="field"><span>JOB DESCRIPTION <small>OPTIONAL</small></span>
                <textarea className="job-description" name="job_description" value={form.job_description} onChange={changeField} placeholder="Paste the role's responsibilities and requirements..." maxLength={12000} />
              </label>
              <label className="field"><span>INTERVIEW QUESTION</span>
                <textarea className="question-field" name="question" value={form.question} onChange={changeField} placeholder="What might they ask you?" maxLength={2000} />
              </label>
              <label className="field"><span>YOUR DRAFT <small>OPTIONAL</small></span>
                <textarea className="answer-field" name="answer" value={form.answer} onChange={changeField} placeholder="A rough answer is a good place to start..." maxLength={12000} />
              </label>

              <div className="selected-agent-card">
                <div className={`selected-agent-icon tone-${selectedAgent.color}`}><ActiveIcon size={18} /></div>
                <div className="selected-agent-text"><span>YOUR APPROACH</span><strong>{selectedAgent.name}</strong><small>{selectedAgent.description}</small></div>
                <span className="selected-agent-tag">{selectedAgent.kind}</span>
              </div>

              <button className="run-button" type="submit" disabled={loading || !serverOnline}>
                {loading ? <LoaderCircle className="spin" size={17} /> : <Sparkles size={17} />}
                <span>{loading ? "Preparing your session" : "Prepare for interview"}</span>
                {!loading && <ArrowRight size={17} className="run-arrow" />}
              </button>
              <div className="run-caption"><span className="privacy-mark"><Check size={11} /></span> Recent runs are saved locally in this browser.</div>
            </form>
          </section>

          <section className="result-column" aria-label="Preparation results">
            <div className="result-heading">
              <div className="section-title-row">
                <div className="section-number">02</div>
                <div><h2>Work it through</h2><p>{selectedAgent.task}</p></div>
              </div>
              {result && <span className="result-model">{result.model}</span>}
            </div>

            <div className={`result-surface ${result ? "has-result" : ""}`}>
              {error ? (
                <div className="error-state" role="alert">
                  <div className="error-symbol"><X size={19} /></div><h3>Couldn't complete the run</h3><p>{error}</p>
                  <button className="text-button" onClick={() => setError("")}>Dismiss</button>
                </div>
              ) : result ? (
                <>
                  <div className="result-toolbar">
                    <div className="result-agent-label"><span className="result-agent-dot" />{result.agent.name}<span className="toolbar-divider" />{new Date(result.createdAt).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</div>
                    <div className="result-actions">
                      <button className="icon-button" title="Copy response" aria-label="Copy response" onClick={copyResult}>{copied ? <Check size={16} /> : <Copy size={16} />}</button>
                      <button className="icon-button" title="Download Markdown" aria-label="Download Markdown" onClick={downloadResult}><ArrowDownToLine size={16} /></button>
                    </div>
                  </div>
                  <article className="markdown-output"><ReactMarkdown remarkPlugins={[remarkGfm]}>{result.response}</ReactMarkdown></article>
                  {result.data?.sources?.length > 0 && (
                    <div className="source-list">
                      <span className="source-list-title">SOURCES</span>
                      {result.data.sources.map((source) => (
                        <a key={source.url} href={source.url} target="_blank" rel="noreferrer">{source.title}<ArrowRight size={12} /></a>
                      ))}
                    </div>
                  )}
                  {result.data?.grounding_html && (
                    <iframe
                      className="search-suggestions"
                      title="Google Search suggestions"
                      sandbox=""
                      srcDoc={result.data.grounding_html}
                    />
                  )}
                  {result.steps?.length > 0 && (
                    <div className="workflow-trace">
                      <div className="trace-heading"><span><Layers3 size={14} />RUN TRACE</span><span>{result.steps.length} {result.steps.length === 1 ? "step" : "steps"}</span></div>
                      <ol>{result.steps.map((step, index) => <li key={`${step.name}-${index}`}><span className="trace-check"><Check size={11} /></span><div><strong>{step.name}</strong><p>{step.output}</p></div></li>)}</ol>
                    </div>
                  )}
                </>
              ) : loading ? (
                <div className="loading-state" aria-live="polite"><div className="loading-orbit"><span /><span /><span /></div><span className="loading-kicker">A LITTLE THINKING, IN ORDER</span><h3>Putting the pieces together</h3><p>Your {selectedAgent.kind.toLowerCase()} is working through the context.</p></div>
              ) : (
                <div className="empty-state">
                  <div className="empty-art" aria-hidden="true"><div className="art-paper"><span /><span /><span /><span /></div><div className="art-spark"><Sparkles size={20} /></div></div>
                  <span className="empty-kicker">A FRESH PAGE</span>
                  <h3>Your next good answer starts here.</h3>
                  <p>Choose an approach, add a little context, and your preparation will take shape here.</p>
                  <div className="empty-hint"><FileSearch size={15} /><span>Results are tailored to the role and draft you provide.</span></div>
                </div>
              )}
            </div>

            <div className="result-footnote"><span><Database size={13} /></span><span>Mock data is clearly labeled. Live integrations use your configured Google credentials.</span></div>
          </section>
        </div>

        <footer className="page-footer"><span>FIELDNOTES <b>·</b> INTERVIEW STUDIO</span><span>Built around your experience, not a script.</span></footer>
      </main>

      {notice && <div className="toast" role="status"><Check size={15} />{notice}</div>}
    </div>
  );
}

export default App;