from config import Settings

def test_default_config_loads() -> None:
    settings = Settings()
    assert settings.aws_region
    assert settings.bedrock_model_id
