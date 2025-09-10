import React, { useState } from "react";
import axios from "axios";

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

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif", border: "1px solid #ddd", borderRadius: 8, padding: 24 }}>
      <h2>Scam Call Detector</h2>
      <form onSubmit={handleUpload}>
        <input type="file" accept="audio/*" onChange={e => setAudioFile(e.target.files[0])} />
        <button type="submit" disabled={loading} style={{ marginLeft: 10 }}>
          {loading ? "Analyzing..." : "Upload & Analyze"}
        </button>
      </form>
      {transcript && (
        <>
          <h4>Transcript</h4>
          <div style={{ background: "#f7f7f7", padding: 12, borderRadius: 4 }}>{transcript}</div>
          <h4>Scam Verdict: {verdict ? <span style={{ color: verdict === "Scam" ? "red" : "green" }}>{verdict}</span> : ""}</h4>
          <div><b>Explanation:</b> {explanation}</div>
        </>
      )}
    </div>
  );
}

export default App;
