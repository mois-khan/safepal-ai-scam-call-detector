# SafePal-AI — Real-Time Scam Call Detector

**SafePal-AI** is an AI-powered tool to detect scams in phone calls using real-time audio analysis, natural language processing, and speaker diarization.

(This is currently a prototype)

---

## Features

- **Real-time speech-to-text**  
  Converts audio to text in multiple languages.
- **Automatic English translation**  
  Returns all transcripts in English using Whisper.
- **Speaker diarization**  
  Displays “who said what,” when possible.
- **AI-powered scam detection**  
  Uses Gemini API and/or GPT-4o for smart analysis.
- **Clean UI**  
  Mobile/web frontend for easy use.

---

## Tech Stack

| Component         | Technology                  |
|-------------------|----------------------------|
| Frontend          | React.js(demo) / Flutter(app)         |
| Backend           | Python Flask               |
| STT & Translation | OpenAI Whisper             |
| Diarization       | AssemblyAI API             |
| Scam Detection    | Gemini API (Google) / openAI GPT-4o       |

---

## How It Works

1. **User uploads a phone call recording**  
2. **Whisper:**  
   - Transcribes and auto-translates all speech to English  
3. **AssemblyAI:**  
   - Performs speaker diarization (labels who spoke when)
4. **Gemini API:**  
   - Gives a “Scam/Not Scam” verdict and brief explanation
5. **Frontend shows:**  
   - Text transcript with speakers, scam verdict, and reason

---


## Credits

- Project by Mois Khan & Satwika Abbu for NxtWave Buildathon 2025  
- Powered by OpenAI Whisper, AssemblyAI, Gemini API

---


