import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  FileText,
  History,
  Compass,
  FileCode,
  PenTool,
  Lock,
  ChevronRight,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Gavel
} from 'lucide-react';
import './App.css';

export default function App() {
  // Database States (fully static and unconnected to backend)
  const [cases, setCases] = useState([
    {
      "title": "Bachan Singh v. State of Punjab",
      "year": "1980",
      "court": "Supreme Court of India",
      "category": "criminal",
      "principle": "Rarest of rare doctrine for death penalty.",
      "text": "This is a third-party open dataset summary of Bachan Singh v. State of Punjab (1980). The Supreme Court of India upheld the constitutional validity of the death penalty for murder in Section 302 of the Indian Penal Code, but restricted its application to the 'rarest of rare' cases.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/307021/"
    },
    {
      "title": "Salem Advocate Bar Association, Tamil Nadu v. Union of India",
      "year": "2005",
      "court": "Supreme Court of India",
      "category": "civil_procedure_evidence",
      "principle": "Case management, costs, and speedy trial in civil procedure.",
      "text": "This is a third-party open dataset summary. The Court gave directions for the effective implementation of the amendments made to the Code of Civil Procedure in 1999 and 2002, focusing on speedy trial, awarding of costs, and case management.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/1712862/"
    },
    {
      "title": "Satyabrata Ghose v. Mugneeram Bangur & Co.",
      "year": "1954",
      "court": "Supreme Court of India",
      "category": "contract_property",
      "principle": "Doctrine of Frustration under Section 56 of the Indian Contract Act.",
      "text": "This is a third-party open dataset summary. The Supreme Court laid down the scope of the doctrine of frustration in Indian contract law, stating that 'impossible' does not merely mean physical or literal impossibility, but also impracticability from the point of view of the object and purpose of the parties.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/1410188/"
    },
    {
      "title": "Navtej Singh Johar v. Union of India",
      "year": "2018",
      "court": "Supreme Court of India",
      "category": "family_gender",
      "principle": "Decriminalization of consensual same-sex relations.",
      "text": "This is a third-party open dataset summary. The Supreme Court unanimously struck down parts of Section 377 of the Indian Penal Code, decriminalizing consensual same-sex sexual conduct between adults, recognizing it as a violation of fundamental rights to privacy, equality, and dignity.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/168671544/"
    },
    {
      "title": "Bangalore Water Supply and Sewerage Board v. A. Rajappa",
      "year": "1978",
      "court": "Supreme Court of India",
      "category": "labor_service",
      "principle": "Expansive definition of 'industry' under the Industrial Disputes Act.",
      "text": "This is a third-party open dataset summary. The Court gave a very broad interpretation to the term 'industry' under Section 2(j) of the Industrial Disputes Act, 1947, applying the 'triple test' to determine if an establishment is an industry.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/1644838/"
    },
    {
      "title": "Tata Consultancy Services v. State of Andhra Pradesh",
      "year": "2004",
      "court": "Supreme Court of India",
      "category": "commercial_corporate",
      "principle": "Software is goods.",
      "text": "This is a third-party open dataset summary. The Supreme Court held that canned software (off-the-shelf software) is 'goods' for the purpose of sales tax, as it has the attributes thereof (utility, capability of being bought and sold, and capability of being transmitted, transferred, delivered, stored and possessed).",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/106950/"
    },
    {
      "title": "Vodafone International Holdings BV v. Union of India",
      "year": "2012",
      "court": "Supreme Court of India",
      "category": "tax_finance",
      "principle": "Taxation of offshore share transfers.",
      "text": "This is a third-party open dataset summary. The Supreme Court held that the Indian Revenue Authorities do not have jurisdiction to tax an offshore transaction of transfer of shares between two non-resident companies, even if it indirectly results in the transfer of Indian assets.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/115852355/"
    },
    {
      "title": "M.C. Mehta v. Union of India (Oleum Gas Leak)",
      "year": "1986",
      "court": "Supreme Court of India",
      "category": "environment_land",
      "principle": "Absolute liability principle.",
      "text": "This is a third-party open dataset summary. The Supreme Court evolved the principle of 'absolute liability' for hazardous or inherently dangerous industries, departing from the English principle of strict liability in Rylands v. Fletcher.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/1486949/"
    },
    {
      "title": "Kesavananda Bharati v. State of Kerala",
      "year": "1973",
      "court": "Supreme Court of India",
      "category": "democracy_rights",
      "principle": "Basic Structure Doctrine.",
      "text": "This is a third-party open dataset summary. The Supreme Court held that while the Parliament has wide powers to amend the Constitution, it cannot alter or destroy its 'basic structure' or essential features.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/257876/"
    },
    {
      "title": "Novartis v. Union of India",
      "year": "2013",
      "court": "Supreme Court of India",
      "category": "education_ip",
      "principle": "Evergreening of patents under Section 3(d).",
      "text": "This is a third-party open dataset summary. The Supreme Court rejected Novartis' patent application for its anti-cancer drug Glivec, strictly interpreting Section 3(d) of the Patents Act to prevent the 'evergreening' of patents by pharmaceutical companies for minor modifications.",
      "source_name": "Third-Party/Open Dataset",
      "source_url": "https://indiankanoon.org/doc/165776436/"
    }
  ]);

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Form Configuration
  const [caseQuery, setCaseQuery] = useState('');
  const [perspectiveCount, setPerspectiveCount] = useState(4);
  const [judiciaryCorrupt, setJudiciaryCorrupt] = useState(false);
  const [specificRoles, setSpecificRoles] = useState('');
  
  // Notice alert state
  const [submittedDispatch, setSubmittedDispatch] = useState(null);

  // New Live Connection States
  const [threadId, setThreadId] = useState(null);
  const [liveLogs, setLiveLogs] = useState([]);
  const [liveState, setLiveState] = useState({
    perspectives: [],
    judiciary: {},
    conclusion: "",
    final_docs: []
  });
  const [sseStatus, setSseStatus] = useState("idle"); // idle, running, interrupted, complete, error
  const [hitlInput, setHitlInput] = useState("");
  const [expandedRags, setExpandedRags] = useState({});
  const [currentProgress, setCurrentProgress] = useState("");

  const backendUrl = window.location.port === "5173" || window.location.port === "5174" 
    ? "http://localhost:8000" 
    : (import.meta.env.VITE_BACKEND_URL || "");

  // Fetch Cases and History Lists
  const fetchData = async () => {
    try {
      const casesRes = await fetch(`${backendUrl}/api/cases`);
      const casesData = await casesRes.json();
      setCases(casesData);

      const historyRes = await fetch(`${backendUrl}/api/history`);
      const historyData = await historyRes.json();
      setHistory(historyData);
    } catch (e) {
      console.error("Failed to load backend databases:", e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Pre-fill setup form from landmark case select
  const selectCasePrecedent = (item) => {
    setCaseQuery(`Case: ${item.title}. Topic: ${item.principle}`);
    if (item.category) {
      setSpecificRoles(item.category.replace(/_/g, ' '));
    }
    // Scroll down to Dispatch Form
    const element = document.getElementById("dispatch-desk");
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Simple markdown-to-React elements formatter
  const formatMarkdown = (text) => {
    if (!text) return "";
    
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      let cleanLine = line.trim();
      if (!cleanLine) return <div key={idx} style={{ height: '8px' }} />;
      
      // Check if it's a bullet point
      const isBullet = cleanLine.startsWith("* ") || cleanLine.startsWith("- ");
      if (isBullet) {
        cleanLine = cleanLine.substring(2);
      }
      
      // Replace **bold** with <strong>bold</strong>
      const parts = cleanLine.split(/\*\*([^*]+)\*\*/g);
      const content = parts.map((part, pIdx) => {
        if (pIdx % 2 === 1) {
          return <strong key={pIdx}>{part}</strong>;
        }
        return part;
      });

      if (isBullet) {
        return (
          <li key={idx} style={{ marginLeft: '16px', listStyleType: 'disc', fontSize: '0.9em', marginTop: '4px' }}>
            {content}
          </li>
        );
      }
      
      return (
        <p key={idx} style={{ textIndent: '0px', marginTop: '6px', lineHeight: '1.4' }}>
          {content}
        </p>
      );
    });
  };

  // Submit handler to launch simulation
  const handleLaunchSimulation = async (e) => {
    e.preventDefault();
    if (!caseQuery.trim()) return;

    setLoading(true);
    setLiveLogs([]);
    setLiveState({
      perspectives: [],
      judiciary: {},
      conclusion: "",
      final_docs: []
    });
    setSseStatus("connecting");

    try {
      // 1. Start the debate on backend
      const res = await fetch(`${backendUrl}/api/debate/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: caseQuery,
          number_of_perspectives: parseInt(perspectiveCount),
          judiciary_corrupt: judiciaryCorrupt,
          specific_roles: specificRoles ? specificRoles.split(",").map(r => r.trim()) : []
        })
      });

      const data = await res.json();
      const newThreadId = data.thread_id;
      setThreadId(newThreadId);

      // Refresh list to show newly starting item in history
      fetchData();

      // 2. Open EventSource SSE stream
      const eventSource = new EventSource(`${backendUrl}/api/debate/stream/${newThreadId}`);
      setSseStatus("running");
      setCurrentProgress("Initializing Trial Connections...");

      eventSource.addEventListener("progress", (event) => {
        const payload = JSON.parse(event.data);
        setLiveLogs(prev => [...prev, `[PROGRESS] ${payload.message}`]);
        setCurrentProgress(payload.message);
      });

      eventSource.addEventListener("node_start", (event) => {
        const payload = JSON.parse(event.data);
        const node = payload.node;
        setLiveLogs(prev => [...prev, `[INIT] Node Execution Started: ${node.replace('_node', '').toUpperCase()}`]);
        
        const nodeMessages = {
          "query_refine_node": "Formulating Case & Structuring Legal Dispute...",
          "moderator_node": "Initializing Courtroom & Assigning Advocate Personas...",
          "p1_node": "Advocate 1 is drafting arguments...",
          "p2_node": "Advocate 2 is drafting arguments...",
          "p3_node": "Advocate 3 is drafting arguments...",
          "p4_node": "Advocate 4 is drafting arguments...",
          "p5_node": "Advocate 5 is drafting arguments...",
          "p6_node": "Advocate 6 is drafting arguments...",
          "p7_node": "Advocate 7 is drafting arguments...",
          "p8_node": "Advocate 8 is drafting arguments...",
          "judiciary_node": "Judiciary Bench is deliberating and drafting verdict...",
          "conclusion_node": "Court Clerk is drafting the final conclusion report..."
        };
        if (nodeMessages[node]) {
          setCurrentProgress(nodeMessages[node]);
        }
      });

      eventSource.addEventListener("node_update", (event) => {
        const payload = JSON.parse(event.data);
        setLiveLogs(prev => [...prev, `[UPDATE] Node Completed: ${payload.node.replace('_node', '').toUpperCase()}`]);
        
        setLiveState(prev => ({
          ...prev,
          perspectives: payload.perspectives || prev.perspectives,
          judiciary: payload.judiciary || prev.judiciary,
          conclusion: payload.conclusion || prev.conclusion,
          final_docs: payload.final_docs || prev.final_docs
        }));
      });

      eventSource.addEventListener("interrupt", (event) => {
        setSseStatus("interrupted");
        setCurrentProgress("");
        setLiveLogs(prev => [...prev, `[INTERRUPT] Awaiting Human Input gateway review...`]);
        eventSource.close();
        setLoading(false);
      });

      eventSource.addEventListener("complete", (event) => {
        setSseStatus("complete");
        setCurrentProgress("");
        setLiveLogs(prev => [...prev, `[COMPLETE] Chamber verdict finalized.`]);
        eventSource.close();
        setLoading(false);
        fetchData(); // Refresh history
      });

      eventSource.onerror = (err) => {
        console.error("SSE stream error:", err);
        setSseStatus("error");
        setLiveLogs(prev => [...prev, `[CRITICAL ERROR] Connection lost.`]);
        eventSource.close();
        setLoading(false);
      };

    } catch (err) {
      console.error("Launch error:", err);
      setSseStatus("error");
      setLoading(false);
    }
  };

  // Resume Handler for Human-in-the-Loop Interruption
  const handleResumeDebate = async (action) => {
    if (!threadId) return;
    setLoading(true);
    setSseStatus("running");

    try {
      await fetch(`${backendUrl}/api/debate/resume/${threadId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action, // "continue_debate" or "generate_conclusion" or "continue_debate_with_input"
          in_session_input: hitlInput
        })
      });
      setHitlInput("");

      // Reconnect stream
      const eventSource = new EventSource(`${backendUrl}/api/debate/stream/${threadId}`);
      setCurrentProgress("Re-establishing Trial Session Connection...");

      eventSource.addEventListener("progress", (event) => {
        const payload = JSON.parse(event.data);
        setLiveLogs(prev => [...prev, `[PROGRESS] ${payload.message}`]);
        setCurrentProgress(payload.message);
      });

      eventSource.addEventListener("node_start", (event) => {
        const payload = JSON.parse(event.data);
        const node = payload.node;
        setLiveLogs(prev => [...prev, `[INIT] Node Execution Started: ${node.replace('_node', '').toUpperCase()}`]);
        
        const nodeMessages = {
          "query_refine_node": "Formulating Case & Structuring Legal Dispute...",
          "moderator_node": "Initializing Courtroom & Assigning Advocate Personas...",
          "p1_node": "Advocate 1 is drafting arguments...",
          "p2_node": "Advocate 2 is drafting arguments...",
          "p3_node": "Advocate 3 is drafting arguments...",
          "p4_node": "Advocate 4 is drafting arguments...",
          "p5_node": "Advocate 5 is drafting arguments...",
          "p6_node": "Advocate 6 is drafting arguments...",
          "p7_node": "Advocate 7 is drafting arguments...",
          "p8_node": "Advocate 8 is drafting arguments...",
          "judiciary_node": "Judiciary Bench is deliberating and drafting verdict...",
          "conclusion_node": "Court Clerk is drafting the final conclusion report..."
        };
        if (nodeMessages[node]) {
          setCurrentProgress(nodeMessages[node]);
        }
      });

      eventSource.addEventListener("node_update", (event) => {
        const payload = JSON.parse(event.data);
        setLiveLogs(prev => [...prev, `[UPDATE] Node Completed: ${payload.node.replace('_node', '').toUpperCase()}`]);
        setLiveState(prev => ({
          ...prev,
          perspectives: payload.perspectives || prev.perspectives,
          judiciary: payload.judiciary || prev.judiciary,
          conclusion: payload.conclusion || prev.conclusion,
          final_docs: payload.final_docs || prev.final_docs
        }));
      });

      eventSource.addEventListener("interrupt", (event) => {
        setSseStatus("interrupted");
        setCurrentProgress("");
        eventSource.close();
        setLoading(false);
      });

      eventSource.addEventListener("complete", (event) => {
        setSseStatus("complete");
        setCurrentProgress("");
        eventSource.close();
        setLoading(false);
        fetchData();
      });

      eventSource.onerror = () => {
        setSseStatus("error");
        eventSource.close();
        setLoading(false);
      };
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="gazette-container">
      {/* Masthead Header Section */}
      <header className="gazette-masthead">
        <div className="masthead-info-bar">
          <div>VOL. I &bull; NO. I</div>
          <div>LONDON, TUESDAY, JUNE 30, 2026 &bull; LOCALPORT 5173</div>
          <div>PRICE: THREEPENCE</div>
        </div>

        <div className="masthead-title-wrap">
          <img src="/logo.png" alt="RabbitHole Stamp" className="masthead-logo" />
          <h1 className="masthead-title">The RabbitHole Chronicles</h1>
          <p className="masthead-subtitle">
            A Stateful Multi-Agent Machinery Compiled to Simulate, Verify, and Mediate Relational Cognitive Disputes.
          </p>
        </div>

        <hr className="double-rule" />
      </header>

      {/* Main 3-Column Newspaper grid */}
      <div className="gazette-columns">
        
        {/* Column 1: The Active Chamber (The Simulator Setup) */}
        <div className="gazette-col gazette-col-divider">
          <div className="gazette-article">
            <span className="article-category">I. The Primary Machinery</span>
            <h2 className="article-headline">Adversarial Cognition in the Virtual Courtroom</h2>
            <div className="article-meta">BY OUR PARLIAMENTARY CORRESPONDENT</div>
            
            <p className="article-body drop-cap">
              The Court gathers here to adjudicate matters of commercial, legal, and semantic import. 
              By employing parallel advocate agents, the chamber exposes factual contradictions, 
              verifies citations against our RAG registry, and delivers structured verdicts.
            </p>

            <div className="vintage-illustration-frame">
              <img 
                src="https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=60&w=400" 
                alt="Classical Courtroom Scale"
                className="vintage-illustration" 
              />
              <div className="illustration-caption">
                Fig 1.&mdash;The Scales of Judicial Arbitration, preserved under Sepia filter.
              </div>
            </div>

            <p className="article-body" style={{ fontStyle: 'italic' }}>
              "To initiate this automated clockwork debate, record your case guidelines within the Dispatch Desk form below."
            </p>
          </div>

          <hr className="single-rule" />

          {/* Dispatch Desk Form */}
          <div id="dispatch-desk" className="gazette-article" style={{ background: 'var(--bg-parchment-dark)', padding: '24px', border: '1px solid var(--border-ink)' }}>
            <span className="article-category" style={{ fontFamily: 'var(--font-typewriter)' }}>Dispatch Desk Setup</span>
            <h3 className="article-headline small">Register Case Dispatch</h3>

            {submittedDispatch ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontFamily: 'var(--font-typewriter)', fontSize: '0.85em', color: 'var(--text-ink)' }}>
                <div style={{ border: '2px dashed var(--stamp-red)', padding: '14px', borderRadius: '4px', position: 'relative' }}>
                  <div className="ink-stamp red" style={{ position: 'absolute', top: '10px', right: '10px', transform: 'rotate(-8deg)' }}>FILED</div>
                  <h4 style={{ fontWeight: 'bold', marginBottom: '8px' }}>DISPATCH REGISTERED</h4>
                  <p><strong>Topic:</strong> {submittedDispatch.query}</p>
                  <p><strong>Advocates:</strong> {submittedDispatch.perspectives} Agents</p>
                  <p><strong>Judiciary:</strong> {submittedDispatch.corruption}</p>
                  <p><strong>Target Roles:</strong> {submittedDispatch.roles}</p>
                </div>
                <button 
                  className="vintage-btn"
                  onClick={() => setSubmittedDispatch(null)}
                  style={{ width: '100%' }}
                >
                  Configure New Dispatch
                </button>
              </div>
            ) : (
              <form onSubmit={handleLaunchSimulation} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontFamily: 'var(--font-typewriter)', fontSize: '0.8em', fontWeight: 'bold' }}>DISPUTE QUERY TEXT</label>
                  <textarea 
                    className="text-input" 
                    rows={4}
                    style={{ background: 'rgba(255,255,255,0.7)', border: '1px solid var(--border-ink)', fontFamily: 'var(--font-mono)', padding: '10px', outline: 'none' }}
                    placeholder="e.g. Case of data privacy violations or smart contract disputes..."
                    value={caseQuery}
                    onChange={e => setCaseQuery(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontFamily: 'var(--font-typewriter)', fontSize: '0.8em', fontWeight: 'bold' }}>
                    ADVOCATE COUNT: <span style={{ fontFamily: 'var(--font-mono)' }}>{perspectiveCount}</span>
                  </label>
                  <input 
                    type="range" 
                    min={2} 
                    max={8}
                    className="range-input"
                    value={perspectiveCount}
                    onChange={e => setPerspectiveCount(e.target.value)}
                    style={{ width: '100%', accentColor: 'var(--text-ink)' }}
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontFamily: 'var(--font-typewriter)', fontSize: '0.8em', fontWeight: 'bold' }}>JUDICIARY PROFILE</label>
                  <select 
                    style={{ background: 'rgba(255,255,255,0.7)', border: '1px solid var(--border-ink)', fontFamily: 'var(--font-mono)', padding: '8px', outline: 'none' }}
                    value={judiciaryCorrupt ? "corrupt" : "fair"}
                    onChange={e => setJudiciaryCorrupt(e.target.value === 'corrupt')}
                  >
                    <option value="fair">Fair Arbitrator (Rule of Law)</option>
                    <option value="corrupt">Corrupt Arbitrator (Precedent Ignored)</option>
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontFamily: 'var(--font-typewriter)', fontSize: '0.8em', fontWeight: 'bold' }}>TARGET ADVOCATE ROLES</label>
                  <input 
                    type="text" 
                    placeholder="e.g. Compliance Officer, Privacy Activist"
                    style={{ background: 'rgba(255,255,255,0.7)', border: '1px solid var(--border-ink)', fontFamily: 'var(--font-mono)', padding: '8px', outline: 'none' }}
                    value={specificRoles}
                    onChange={e => setSpecificRoles(e.target.value)}
                  />
                </div>

                <button 
                  type="submit" 
                  className="vintage-btn"
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                >
                  <Gavel size={14} /> Submit Dispatch to Court
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Column 2: Live Courtroom Chamber */}
        <div className="gazette-col gazette-col-divider">
          <div className="gazette-article">
            <span className="article-category">II. Courtroom Chamber Feed</span>
            <h2 className="article-headline">The Chamber in Live Session</h2>
            <div className="article-meta">REALTIME TELEGRAPH WIRE SERVICE</div>

            {(sseStatus === "connecting" || sseStatus === "running") && (
              <div style={{ 
                background: 'rgba(179, 39, 39, 0.05)', 
                border: '1px dashed var(--stamp-red)', 
                padding: '12px 16px', 
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                borderRadius: '2px'
              }}>
                <span className="signal-lamp"></span>
                <span className="telegraph-flicker" style={{ fontSize: '0.85em', color: 'var(--text-ink)', fontWeight: 'bold' }}>
                  INCOMING DISPATCH: {currentProgress || "Connecting to virtual chamber..."}
                </span>
              </div>
            )}
            
            {sseStatus === "idle" ? (
              <div>
                <p className="article-body">
                  No active trial is registered in the chamber. Configure your query on the Dispatch Desk and submit it to launch live proceedings.
                </p>
                <div className="vintage-illustration-frame">
                  <img 
                    src="https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&q=60&w=400" 
                    alt="Vintage Books Library"
                    className="vintage-illustration" 
                  />
                  <div className="illustration-caption">
                    Fig 2.&mdash;A registry cabinet storing epistemic record binders.
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* 1. Live Ticker / Logs */}
                <div className="catalog-list" style={{ maxHeight: '180px', overflowY: 'auto', background: 'var(--bg-parchment-dark)', padding: '12px', border: '1px solid var(--border-ink)' }}>
                  <h4 style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8em', marginBottom: '8px' }}>TELEGRAPH FEED LOGS:</h4>
                  {liveLogs.map((log, idx) => (
                    <div key={idx} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7em', borderBottom: '1px dotted var(--border-ink-thin)', padding: '2px 0' }}>
                      {log}
                    </div>
                  ))}
                </div>

                {/* 2. RAG Source Documents */}
                {liveState.final_docs.length > 0 && (
                  <div style={{ background: 'rgba(255,255,255,0.4)', padding: '14px', border: '1px solid var(--border-ink)' }}>
                    <h4 style={{ fontFamily: 'var(--font-typewriter)', fontSize: '0.8em', marginBottom: '8px' }}>RAG Verification Registry Chunks:</h4>
                    {liveState.final_docs.map((doc, idx) => {
                      let sourceLabel = "Verification Registry Case Chunk";
                      if (doc.metadata.type === "recomposed_merged_brief") {
                        sourceLabel = "Synthesized Merged Brief (Local + Web)";
                      } else if (doc.metadata.type === "recomposed_web_brief") {
                        sourceLabel = "Synthesized Web Brief";
                      } else if (doc.metadata.type === "recomposed_local_brief") {
                        sourceLabel = "Synthesized Local Brief";
                      } else if (doc.metadata.source) {
                        sourceLabel = doc.metadata.source;
                      }

                      const isExpanded = expandedRags[idx];
                      const textToShow = isExpanded 
                        ? doc.page_content 
                        : (doc.page_content.substring(0, 250) + (doc.page_content.length > 250 ? "..." : ""));

                      return (
                        <div key={idx} style={{ fontSize: '0.85em', marginBottom: '8px', borderBottom: '1px dotted var(--border-ink-thin)', paddingBottom: '8px' }}>
                          <strong>Source:</strong> {sourceLabel}
                          <div style={{ fontStyle: 'italic', marginTop: '4px' }}>
                            {formatMarkdown(textToShow)}
                          </div>
                          {doc.page_content.length > 250 && (
                            <button 
                              onClick={() => setExpandedRags(prev => ({ ...prev, [idx]: !prev[idx] }))}
                              style={{ 
                                background: 'none', 
                                border: 'none', 
                                color: 'var(--stamp-blue)', 
                                cursor: 'pointer', 
                                fontFamily: 'var(--font-mono)', 
                                fontSize: '0.75em', 
                                padding: '4px 0 0', 
                                textDecoration: 'underline' 
                              }}
                            >
                              {isExpanded ? "[ SHOW LESS ]" : "[ READ FULL BRIEF ]"}
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* 3. Advocates / Perspectives Statements */}
                {liveState.perspectives.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <h4 style={{ fontFamily: 'var(--font-typewriter)', fontSize: '0.9em' }}>Advocacy Arguments:</h4>
                    {liveState.perspectives.map((p, idx) => (
                      <div key={idx} style={{ border: '1px solid var(--border-ink)', padding: '10px', background: 'rgba(255,255,255,0.4)' }}>
                        <strong>Advocate {p.id}: {p.role}</strong>
                        <div style={{ fontSize: '0.85em', marginTop: '4px' }}>{p.public_statement ? formatMarkdown(p.public_statement) : "Preparing statement..."}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* 4. Judiciary Deliberation */}
                {liveState.judiciary.verdict && (
                  <div style={{ border: '2px dashed var(--stamp-red)', padding: '14px', background: 'rgba(179, 39, 39, 0.05)', position: 'relative' }}>
                    <div className="ink-stamp red" style={{ position: 'absolute', top: '10px', right: '10px' }}>VERDICT</div>
                    <h4 style={{ fontFamily: 'var(--font-typewriter)' }}>JUDICIARY VERDICT:</h4>
                    <div style={{ fontSize: '0.9em', marginTop: '6px' }}><strong>Reasoning:</strong> {formatMarkdown(liveState.judiciary.reasoning)}</div>
                    <p style={{ fontSize: '0.95em', fontWeight: 'bold', marginTop: '6px' }}>Verdict: {liveState.judiciary.verdict}</p>
                  </div>
                )}

                {/* 5. Human-in-the-Loop Gateway (HITL) */}
                {sseStatus === "interrupted" && (
                  <div style={{ background: 'var(--bg-parchment-dark)', border: '2px solid var(--stamp-blue)', padding: '16px', borderRadius: '4px' }}>
                    <h4 style={{ fontFamily: 'var(--font-typewriter)', color: 'var(--stamp-blue)' }}>HUMAN GATEWAY REVIEW REQUEST</h4>
                    <p style={{ fontSize: '0.85em', margin: '6px 0 12px' }}>Review the verdict above. You can intervene with additional session context, continue trial, or draft the final verdict.</p>
                    <textarea 
                      className="text-input"
                      rows={2}
                      style={{ width: '100%', outline: 'none', padding: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.8em', marginBottom: '12px', background: 'rgba(255,255,255,0.7)', border: '1px solid var(--border-ink)' }}
                      placeholder="Type additional trial inputs here..."
                      value={hitlInput}
                      onChange={e => setHitlInput(e.target.value)}
                    />
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="vintage-btn" onClick={() => handleResumeDebate("continue_debate")}>Continue</button>
                      <button className="vintage-btn" onClick={() => handleResumeDebate("continue_debate_with_input")} disabled={!hitlInput.trim()}>Submit Input</button>
                      <button className="vintage-btn" onClick={() => handleResumeDebate("generate_conclusion")}>Finalize Trial</button>
                    </div>
                  </div>
                )}

                {/* 6. Final Conclusion */}
                {liveState.conclusion && (
                  <div style={{ border: '2px double var(--border-ink)', padding: '16px', background: 'rgba(255,255,255,0.7)' }}>
                    <h4 style={{ fontFamily: 'var(--font-typewriter)' }}>FINAL COURT CLERK DECISION SUMMARY</h4>
                    <div style={{ fontSize: '0.9em', marginTop: '6px' }}>{formatMarkdown(liveState.conclusion)}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Column 3: The Precedent Registry (History & Precedents) */}
        <div className="gazette-col">
          <div className="gazette-article">
            <span className="article-category">III. Reference Bulletins</span>
            <h2 className="article-headline">Landmark India Case Records</h2>
            <div className="article-meta">FROM THE HIGH COURT DESK</div>
            
            <p className="article-body">
              Select a historic precedent record below to load its facts directly into the dispatch desk configuration setup.
            </p>

            <div className="catalog-list">
              {cases.length > 0 ? (
                cases.map((c, i) => (
                  <div 
                    key={i} 
                    className="catalog-item"
                    style={{ cursor: 'pointer' }}
                    onClick={() => selectCasePrecedent(c)}
                  >
                    <div className="flex-between" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7em', color: 'var(--text-ink-muted)' }}>
                      <span>{c.category ? c.category.toUpperCase().replace(/_/g, ' ') : 'PRECEDENT'}</span>
                      <span>{c.year}</span>
                    </div>
                    <h4 className="catalog-title" style={{ fontSize: '1rem', marginTop: '6px' }}>{c.title}</h4>
                    <p className="catalog-desc" style={{ fontStyle: 'italic', fontSize: '0.85em' }}>
                      "{c.principle}"
                    </p>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
                      <span className="ink-stamp blue" style={{ fontSize: '0.55em', padding: '2px 6px' }}>LOAD BRIEF</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="article-body" style={{ fontStyle: 'italic', color: 'var(--text-ink-muted)' }}>
                  Awaiting dispatch log files...
                </div>
              )}
            </div>
          </div>

          <hr className="single-rule" />

          {/* Historical Logs */}
          <div className="gazette-article">
            <h3 className="article-headline small">Registry Telegram Dispatches</h3>
            <div className="article-meta">REALTIME TELEGRAPH WIRE</div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontFamily: 'var(--font-mono)', fontSize: '0.75em' }}>
              {history.length > 0 ? (
                history.map((h, idx) => (
                  <div key={idx} style={{ borderBottom: '1px dotted var(--border-ink-thin)', paddingBottom: '8px' }}>
                    <div className="flex-between" style={{ color: 'var(--text-ink-muted)' }}>
                      <span>TELEGRAM #{h.thread_id.substring(0,6).toUpperCase()}</span>
                      <span>{h.timestamp}</span>
                    </div>
                    <p style={{ marginTop: '4px', fontWeight: 'bold' }}>Title: {h.title}</p>
                    <p style={{ color: 'var(--text-ink-muted)', marginTop: '2px' }}>Status: {h.status.toUpperCase()}</p>
                  </div>
                ))
              ) : (
                <p style={{ fontStyle: 'italic', color: 'var(--text-ink-muted)' }}>No logs active on telegram wires.</p>
              )}
            </div>
          </div>
        </div>

      </div>

      <hr className="double-rule" style={{ marginTop: '60px' }} />

      {/* Gazette Footer */}
      <footer className="center-text" style={{ padding: '20px 0 40px', fontFamily: 'var(--font-mono)', fontSize: '0.75em', color: 'var(--text-ink-muted)' }}>
        THE RABBITHOLE CHRONICLES &bull; PRINTED LOCALLY VIA REACT ENGINE &bull; LONDON, SUNDAY, 1892.
      </footer>
    </div>
  );
}
