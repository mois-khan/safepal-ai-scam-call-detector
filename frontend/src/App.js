import React, { useState } from "react";
import axios from "axios";
import "./index.css";

function App() {
  const [audioFile, setAudioFile] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [verdict, setVerdict] = useState("");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!audioFile) return;
    setLoading(true);
    setTranscript("");
    setVerdict("");
    setExplanation("");

    const formData = new FormData();
    formData.append("file", audioFile);

    try {
      const res = await axios.post("http://localhost:5000/transcribe", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTranscript(res.data.transcript);
      setVerdict(res.data.Verdict);
      setExplanation(res.data.Reason);
    } catch (err) {
      alert("Error: " + (err.response?.data?.error || err.message));
    }
    setLoading(false);
  };


const formatTranscript = txt =>
  txt.split('\n').map((line, idx) => {
    if (!line.trim()) return <div key={idx} style={{ height: 8 }} />;
    if (line.startsWith("Speaker A:"))
      return <div className="speakerA" key={idx}>{line}</div>;
    if (line.startsWith("Speaker B:"))
      return <div className="speakerB" key={idx}>{line}</div>;
    return <div key={idx}>{line}</div>;
  });


  return (
    <div className="app-container">
      <div className="simple-card">
        <h1>Scam Call Detector</h1>
        <form onSubmit={handleUpload} className="upload-row">
          <label className="input-file-label">
            Choose File
            <input
              type="file"
              accept="audio/*"
              onChange={e => setAudioFile(e.target.files[0])}
            />
          </label>
          {audioFile &&
            <span className="audio-filename">{audioFile.name}</span>
          }
          <button type="submit" disabled={loading} className="upload-btn">
            {loading ? "Analyzing..." : "Upload & Analyze"}
          </button>
        </form>
        {transcript && (
          <div className="result-row">
            <div className="transcript-card">
              <div className="section-title">Transcript</div>
              <div className="transcript-content">
                {formatTranscript(transcript)}
              </div>
            </div>
            <div className="verdict-card">
              <div className="section-title">Verdict</div>
              <div className={verdict === "Scam" ? "verdict-badge" : "verdict-badge verdict-safe"}>
                {verdict}
              </div>
              <div className="explanation-callout">
                <div className="explanation-title">Explanation</div>
                <div className="explanation-text">
                  {explanation}
                </div>
             </div>

            </div>
          </div>
        )}
      </div>
      <div style={{
        textAlign: "center",
        fontSize: "12px",
        color: "#7d9bae",
        marginTop: 18
      }}>
        © {new Date().getFullYear()} SafePal &bull; Scam Detector Presentation
      </div>
    </div>
  );
}

export default App;
