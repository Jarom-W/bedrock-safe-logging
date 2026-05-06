from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

#This class loads in the environment vars from .env or your shell session.
class Settings(BaseSettings):
    #Create a settings class that inherits the BaseSettings class from Pydantic. This inheritance allows the Settings class to have the 
    #SettingsConfigDict class passed in as an element

    model_config = SettingsConfigDict( #Settings config dict allows us to source from local .env file
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    aws_profile: str = Field(default="dev-bedrock", alias="AWS_PROFILE") #Field is a class to store a field in the Settings class under BaseSettings inheritance
    aws_region: str = Field(default="us-west-1", alias="AWS_REGION") # Region

    bedrock_model_id: str = Field(
        default="us.amazon.nova-lite-v1:0",
        alias="BEDROCK_MODEL_ID", #Using nova-lite
    )
    #Toggles
    safe_logging: bool = Field(default=True, alias="SAFE_LOGGING") 
    log_prompts: bool = Field(default=False, alias="LOG_PROMPTS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    provider_mode: str = Field(default="live", alias="PROVIDER_MODE")
    replay_jsonl_path: str = Field(default="events.jsonl", alias="REPLAY_JSONL_PATH")


settings = Settings() #Initialize an instance of the Settings() class effectively pulling out the environment variables

