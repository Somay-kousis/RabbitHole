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

  const [history, setHistory] = useState([
    {
      "thread_id": "92763d3a-6625-490c-96b8-d27c94ced05b",
      "title": "Case: Bachan Singh v. State of Punjab. Topic: Rarest of rare doctrine for death ...",
      "timestamp": "Tue Jun 30 15:29:17 IST 2026",
      "status": "running"
    },
    {
      "thread_id": "713a29b4-82a7-47b1-912c-0e78c439af82",
      "title": "Case: Kesavananda Bharati v. State of Kerala. Topic: Basic Structure Doctrine",
      "timestamp": "Mon Jun 29 11:15:42 IST 2026",
      "status": "completed"
    },
    {
      "thread_id": "c39a816b-12d4-4bb8-86d9-7681c3e1aa01",
      "title": "Case: Novartis v. Union of India. Topic: Evergreening of patents",
      "timestamp": "Sun Jun 28 17:02:10 IST 2026",
      "status": "completed"
    }
  ]);

  const [loading, setLoading] = useState(false);

  // Form Configuration
  const [caseQuery, setCaseQuery] = useState('');
  const [perspectiveCount, setPerspectiveCount] = useState(4);
  const [judiciaryCorrupt, setJudiciaryCorrupt] = useState(false);
  const [specificRoles, setSpecificRoles] = useState('');
  
  // Notice alert state
  const [submittedDispatch, setSubmittedDispatch] = useState(null);

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

  // Mock submit handler for vintage homepage
  const handleLaunchSimulation = (e) => {
    e.preventDefault();
    if (!caseQuery.trim()) return;

    // Save configuration state locally or send alert
    setSubmittedDispatch({
      query: caseQuery,
      perspectives: perspectiveCount,
      corruption: judiciaryCorrupt ? "CORRUPT BENCH" : "NEUTRAL PRECEDENCE",
      roles: specificRoles || "Standard Legal Suite"
    });
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

        {/* Column 2: Archived Machinery (The Locked Modules) */}
        <div className="gazette-col gazette-col-divider">
          <div className="gazette-article">
            <span className="article-category">II. Archived Machinery</span>
            <h2 className="article-headline">Locked Inventions & Proprietary Claims</h2>
            <div className="article-meta">DECREE OF PATENT OFFICE, 1892</div>
            
            <p className="article-body">
              The following processing devices remain in lockup, pending legal compatibility certifications and funding limits.
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

            <div className="catalog-list">
              {/* Engine 2 */}
              <div className="catalog-item disabled">
                <div className="flex-between">
                  <span className="catalog-title">02 / Contradiction Finder</span>
                  <span className="ink-stamp red">Pending Patent</span>
                </div>
                <p className="catalog-desc">
                  Scans legal documents, smart contracts, or transcripts to map and flag logical contradictions, overrides, and logic loopholes.
                </p>
              </div>

              {/* Engine 3 */}
              <div className="catalog-item disabled">
                <div className="flex-between">
                  <span className="catalog-title">03 / Epistemic Graph</span>
                  <span className="ink-stamp blue">Under Injunction</span>
                </div>
                <p className="catalog-desc">
                  Draws factual topological mesh structures linking courtroom claims directly to reference files.
                </p>
              </div>

              {/* Engine 4 */}
              <div className="catalog-item disabled">
                <div className="flex-between">
                  <span className="catalog-title">04 / Persona Sandbox</span>
                  <span className="ink-stamp red">Restricted</span>
                </div>
                <p className="catalog-desc">
                  Modular agent Motives customization console to configure temperature thresholds and target motives.
                </p>
              </div>
            </div>

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
