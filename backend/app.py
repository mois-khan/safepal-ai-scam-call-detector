from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import tempfile
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
CORS(app)  

model = whisper.load_model("medium")


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400
    
    audio_file = request.files['file']
    filename = audio_file.filename

    tmp_path = os.path.join('temp', filename)
    os.makedirs('temp', exist_ok=True)

    audio_file.save(tmp_path)

    try:
        transcript = model.transcribe(tmp_path, task='transcribe', language='en')

        scam_detection = scam_detector(transcript)
        verdict = "Scam" if scam_detection.lower().startswith("scam") else "Not Scam"

        return jsonify(
            {'transcript': transcript['text'], 
            'Reason': scam_detection, 
            "Verdict": verdict}
        )
    
    finally:
        os.remove(tmp_path)


def scam_detector(transcript):

    client = OpenAI(
        api_key = api_key,
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    prompt = (

        "Analyze the following phone call transcript. Is the caller trying to scam or defraud the receiver?"
        "Answer only 'Scam' or 'Not Scam', and then briefly explain your reasoning. But don't give too lengthy an explanation.\n\n"
        f"Transcript:\n{transcript['text'].strip()}"
    )

    # print(transcript['text'].strip())

    response = client.chat.completions.create(
        model = "gemini-2.5-flash",
        messages = [
            {"role": "system", "content": "You are a scam detection expert."},

            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content

    # print(result)
    return result

    # if result.lower().startswith("scam"):
    #     return "Scam⚠️," + result
    # else:
    #     return "Not Scam✅," + result


if __name__ == '__main__':
    app.run(debug=True, port=5000)
