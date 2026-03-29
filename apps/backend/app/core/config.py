from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://insurance_user:insurance_pass@localhost:5432/insurance_portfolio"

    nextauth_url: str = "http://localhost:3000"
    nextauth_secret: str = "change-me-in-production"

    email_server_host: str = "smtp.postmarkapp.com"
    email_server_port: int = 587
    email_server_user: str = ""
    email_server_pass: str = ""
    email_from: str = "noreply@yourdomain.com"

    s3_endpoint_url: str = "http://localhost:4566"
    s3_access_key: str = "localstack_key"
    s3_secret_key: str = "localstack_secret"
    s3_bucket_name: str = "policy-documents"
    s3_region: str = "ap-southeast-1"

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    google_docai_project_id: str = ""
    google_docai_location: str = "us"
    google_docai_processor_id: str = ""
    google_application_credentials: str = ""

    encryption_key: str = ""

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    mas_disclaimer_version: str = "1.0.0"
    privacy_policy_version: str = "1.0.0"

    log_level: str = "INFO"
    sentry_dsn: str = ""


settings = Settings()
