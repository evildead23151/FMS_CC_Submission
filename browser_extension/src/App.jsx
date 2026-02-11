
import { useState, useEffect } from 'react'
import './index.css'

const GATEWAY_URL = 'http://localhost:8000';

function App() {
    const [url, setUrl] = useState('')
    const [status, setStatus] = useState('idle') // idle, loading, result, error
    const [result, setResult] = useState(null)

    useEffect(() => {
        // Attempt to get current tab URL if extension context
        if (chrome && chrome.tabs && chrome.tabs.query) {
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs[0]) setUrl(tabs[0].url);
            });
        } else {
            setUrl("http://example.com/demo-article"); // Dev mode fallback
        }
    }, []);

    const handleScan = async () => {
        setStatus('loading');
        setResult(null);
        try {
            const resp = await fetch(`${GATEWAY_URL}/scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    content_hash: btoa(url || "demo"), // Simple hash from URL for demo
                    text_content: `Analysis of ${url}`, // Simulated extraction for demo
                    media_urls: [],
                    timestamp: new Date().toISOString()
                })
            });

            const data = await resp.json();
            console.log("Scan Data:", data); // Debug
            setResult(data);
            setStatus('result');
        } catch (e) {
            console.error(e);
            setStatus('error');
        }
    };

    const getRiskScore = (res) => res?.tig_result?.risk_score || 0;
    const getConfidence = (res) => res?.tig_result?.confidence_score || 0;

    return (
        <div className="app-container">
            <header>
                <h1>TrustLens</h1>
                <div className="status-badge">LIVE LOCAL</div>
            </header>

            <main>
                <div className="scan-control">
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="Current URL..."
                    />
                    <button onClick={handleScan} disabled={status === 'loading'}>
                        {status === 'loading' ? 'Scanning...' : 'Analyze Page'}
                    </button>
                </div>

                {status === 'error' && (
                    <div className="card error">
                        Scanning Failed. Check Gateway (Port 8000).
                    </div>
                )}

                {status === 'result' && result && (
                    <div className="result-container">
                        <div className={`score-circle score-${getLevel(getRiskScore(result))}`}>
                            <span className="score-val">{Math.round(getRiskScore(result) * 100)}</span>
                            <span className="score-label">Risk</span>
                        </div>

                        <div className="verdict-box">
                            <h3>{result.trust_posture?.replace('_', ' ').toUpperCase()}</h3>
                            <p>Confidence: {Math.round(getConfidence(result) * 100)}%</p>
                        </div>

                        <div className="signals-list">
                            <h4>Signal Breakdown</h4>
                            {Object.entries(result.signals || {}).map(([name, data]) => (
                                <div key={name} className="signal-row">
                                    <span className="sig-name">{name}</span>
                                    <span className={`sig-val ${getSignalClass(data.risk_score)}`}>
                                        {data.risk_score !== undefined ? (data.risk_score * 100).toFixed(0) + '%' : 'N/A'}
                                    </span>
                                </div>
                            ))}
                        </div>

                        {result.tig_result?.explanation && (
                            <div className="explanation-box">
                                <p>{result.tig_result.explanation}</p>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    )
}

function getLevel(score) {
    if (score > 0.7) return 'high';
    if (score > 0.4) return 'medium';
    return 'low';
}

function getSignalClass(score) {
    if (score > 0.7) return 'risk-high';
    if (score > 0.4) return 'risk-med';
    return 'risk-low';
}

export default App
