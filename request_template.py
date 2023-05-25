import requests
import base64

AUDIO_PATH = 'A1004r.wav'

with open(AUDIO_PATH, 'rb') as audio_str:
    byte_string = base64.b64encode(audio_str.read()).decode('utf-8')


resp = requests.post("http://localhost:8000/", json={
        "data": [
            {"name":'audio.wav',"data":f"data:audio/wav;base64,{byte_string}"},
        ]
    })

print(resp.content)