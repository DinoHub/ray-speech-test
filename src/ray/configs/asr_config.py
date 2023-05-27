from pydantic import BaseSettings, Field

class ASRBaseConfig(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    num_replicas: int = 1
    num_cpus: int = 4
    num_gpus: float = 0.0

    asr_model_path: str = '/asr/models/stt_en_conformer_ctc_medium.nemo'

asr_config = ASRBaseConfig()