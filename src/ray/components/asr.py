import logging
from typing import List, Union

import torch
import numpy as np
import pytorch_lightning as pl
from nemo.utils import model_utils
from nemo.collections.asr.models import ASRModel

class SpeechRecognizer:
    def __init__(self, config):

        self.device: Union[List[int], int] = [0] if (torch.cuda.is_available() and config.num_gpus > 0) else 1
        self.accelerator: str = 'gpu' if (torch.cuda.is_available() and config.num_gpus > 0) else 'cpu'
        self.map_location: str = torch.device(f'cuda:{self.device[0]}') if self.accelerator == 'gpu' else 'cpu'

        # Load model
        model_cfg = ASRModel.restore_from(restore_path=config.asr_model_path, return_config=True)
        classpath = model_cfg.target  # original class path
        imported_class = model_utils.import_class_by_path(classpath)  # type: ASRModel
        logging.info(f"Restoring model : {imported_class.__name__}")
        self.model = imported_class.restore_from(
            restore_path=config.asr_model_path, map_location=self.map_location,
        )

        trainer = pl.Trainer(devices=self.device, accelerator=self.accelerator)
        self.model.set_trainer(trainer)
        self.model = self.model.eval()

    ''' Main prediction function '''
    def predict(self, audio_tensor: Union[np.ndarray, torch.tensor]) -> str:
        
        if type(audio_tensor) is np.ndarray:
            audio_tensor = torch.tensor(audio_tensor)
        
        elif type(audio_tensor) is not torch.tensor:
            raise TypeError('Input is not an np array or tensor')
        
        audio_length_tensor = torch.tensor(audio_tensor.shape)
        audio_tensor = audio_tensor.unsqueeze(0)
        
        with torch.no_grad():
            
            logits, logits_len, greedy_predictions = self.model.forward(
                            input_signal=audio_tensor.to(self.map_location), 
                            input_signal_length=audio_length_tensor.to(self.map_location),
                        )
            
            hypotheses, all_hyp = self.model.decoding.ctc_decoder_predictions_tensor(
                            logits, decoder_lengths=logits_len,
                        )

        transcription = hypotheses[0]
        del logits, logits_len, greedy_predictions, all_hyp
            
        return transcription
