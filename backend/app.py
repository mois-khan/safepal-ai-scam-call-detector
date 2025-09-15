from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import requests
import os
import tempfile
from dotenv import load_dotenv
import time

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
CORS(app)

model = whisper.load_model("medium")  

def scam_detector(transcript_text):
    import openai

    client = openai.OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    prompt = (
        "Analyze the following phone call transcript. Is the caller trying to scam or defraud the receiver? "
        "Answer only 'Scam' or 'Not Scam', and then briefly explain your reasoning, but don't be too lengthy.\n\n"
        f"Transcript:\n{transcript_text.strip()}"
    )

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a scam detection expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def get_assemblyai_diarization(audio_path, polling_timeout_sec=40):
    # print("File exists?", os.path.exists(audio_path))
    # print("File size:", os.path.getsize(audio_path), "bytes")

    headers = {'authorization': ASSEMBLYAI_API_KEY}
    # 1. Upload to AssemblyAI
    with open(audio_path, 'rb') as f:
        upload_resp = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers=headers,
            files={'file': f}
        )
    upload_json = upload_resp.json()
    print("AssemblyAI upload response:", upload_json)
    audio_url = upload_json['upload_url']

    # 2. Request transcript + diarization
    transcript_req = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        headers=headers,
        json={'audio_url': audio_url, 'speaker_labels': True}
    )
    transcript_json = transcript_req.json()
    print("AssemblyAI transcript request:", transcript_json)
    transcript_id = transcript_json['id']

    # 3. Robust polling with timeout
    start = time.time()
    while True:
        try:
            poll = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers, timeout=10)
            result = poll.json()
            status = result.get('status', str(result))
            # print("Polling result:", status)
            if status == 'completed':
                print("AssemblyAI diarization done.")
                return result.get('utterances', [])
            elif status == 'failed':
                print("Failed result:", result)
                raise Exception("Diarization/transcription failed: " + str(result))
            
        except Exception as e:
            print(f"Polling exception: {e}")

        if time.time() - start > polling_timeout_sec:
            print("Polling timed out after", polling_timeout_sec, "seconds.")
            raise TimeoutError("AssemblyAI diarization polling timed out.")
        
        time.sleep(5) 

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # print("Received upload...")
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400
    
    audio_file = request.files['file']
    filename = audio_file.filename

    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    audio_file.save(tmp_path)

    # print("Saved file:", tmp_path)
    # print("Size:", os.path.getsize(tmp_path), "bytes")

    try:
        # print("Starting Whisper transcription...")
        whisper_result = model.transcribe(tmp_path, task='translate', language='en')
        # print("Whisper transcription done.")
        transcript_text = whisper_result['text']

        print(transcript_text)

        # print("Starting AssemblyAI diarization...")
        try:
            utterances = get_assemblyai_diarization(tmp_path)
            dialogue_transcript = "\n\n".join([f"Speaker {u['speaker']}: {u['text']}" for u in utterances])

        except Exception as diar_error:
            # Use simple Whisper transcript with a message if AssemblyAI fails
            print(f"AssemblyAI failed: {diar_error}")
            dialogue_transcript = "Speaker diarization unavailable.\n" + transcript_text

        scam_reason = scam_detector(transcript_text)
        verdict = "Scam" if scam_reason.lower().startswith("scam") else "Not Scam"

        return jsonify({
            'transcript': dialogue_transcript,
            'Verdict': verdict,
            'Reason': scam_reason
        })
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
