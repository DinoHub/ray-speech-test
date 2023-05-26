# from https://github.com/DinoHub/peeps/blob/ray-pipeline/ray_pipeline/detector/detector.py

import base64
import logging
import numpy as np

import ray
from ray import serve
from starlette.requests import Request

from configs.asr_config import asr_config as config

LOGGER = logging.getLogger('ray.serve')
RUNTIME_ENV = {
    'container': {
        'image': 'dleongsh/ray-dory:v1.18.0',
        'run_options': ['--runtime=/usr/bin/nvidia-container-runtime']
    }
}

@serve.deployment(ray_actor_options={"num_cpus": config.num_cpus, "num_gpus": config.num_gpus})
class RaySpeechRecognizer:

    def __init__(self):

        from components.asr import SpeechRecognizer
        self.recognizer = SpeechRecognizer(config)
    
    def read_request(self, base64_string: str) -> np.ndarray:

        data = base64_string['data'][0]['data'].replace('data:audio/wav;base64,', '')
        msg = base64.b64decode(data)

        audio = np.frombuffer(msg, dtype=np.int16)
        audio = audio.astype(np.float32, order='C') / 32767

        return audio

    async def __call__(self, http_request: Request) -> str:
        
        base64_string: str = await http_request.json()
        audio = self.read_request(base64_string)
        text = self.recognizer.predict(audio)

        return text

entrypoint = RaySpeechRecognizer.bind()
