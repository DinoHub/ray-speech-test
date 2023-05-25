from pydantic import BaseSettings, Field

class BaseConfig(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    num_replicas: int = 1
    num_cpus: int = 4
    num_gpus: int = 0

    # KNative assigns a $PORT environment variable to the container
    port: int = Field(default=8080, env="PORT",description="App Server Port")
    asr_model_path: str = '../models/stt_en_conformer_ctc_large.nemo'

config = BaseConfig()