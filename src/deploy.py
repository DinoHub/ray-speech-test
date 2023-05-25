from starlette.requests import Request

import os
import base64
import logging
from typing import Any, List, Optional, Union

import ray
from ray import serve

import torch
import librosa
import numpy as np
import gradio as gr
import soundfile as sf
import pytorch_lightning as pl
from nemo.utils import model_utils
from nemo.collections.asr.models import ASRModel

from config import config, BaseConfig

DEVICE: Union[List[int], int] = [0] if (torch.cuda.is_available() and config.num_gpus >= 1) else 1
ACCELERATOR: str = 'gpu' if (torch.cuda.is_available() and config.num_gpus >= 1) else 'cpu'
MAP_LOCATION: str = torch.device(f'cuda:{DEVICE[0]}') if ACCELERATOR == 'gpu' else 'cpu'

@serve.deployment(ray_actor_options={"num_cpus": config.num_cpus, "num_gpus": config.num_gpus})
class Transcriber:
    def __init__(self) -> ASRModel:

        # Load model
        model_cfg = ASRModel.restore_from(restore_path=config.asr_model_path, return_config=True)
        classpath = model_cfg.target  # original class path
        imported_class = model_utils.import_class_by_path(classpath)  # type: ASRModel
        logging.info(f"Restoring model : {imported_class.__name__}")
        self.model = imported_class.restore_from(
            restore_path=config.asr_model_path, map_location=MAP_LOCATION,
        )

        trainer = pl.Trainer(devices=DEVICE, accelerator=ACCELERATOR)
        self.model.set_trainer(trainer)
        self.model = self.model.eval()

    ''' Main prediction function '''
    def predict(self, filepath: str) -> str:

        with torch.no_grad():

            transcriptions = self.model.transcribe(
                paths2audio_files=[filepath,],
                batch_size=1,
                num_workers=0,
                return_hypotheses=False,
            )

        return transcriptions[0]
    
    def read_request(self, base64_string: str) -> str:

        data = base64_string['data'][0]['data'].replace('data:audio/wav;base64,', '')
        filepath = data[:15] + '.wav'
        msg = base64.b64decode(data)

        audio = np.frombuffer(msg, dtype=np.int16)
        audio = audio.astype(np.float32, order='C') / 32767
        sf.write(filepath, audio, 16000)

        return filepath

    async def __call__(self, http_request: Request) -> str:
        
        base64_string: str = await http_request.json()
        filepath = self.read_request(base64_string)

        text = self.predict(filepath)
        os.remove(filepath)

        return text

entrypoint = Transcriber.bind()