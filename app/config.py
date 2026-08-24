from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(REPO_ROOT / ".env"), extra="ignore")

    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-v4-flash"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    skills_dir: Path = REPO_ROOT / "skills"
    browse_root: Path | None = None
    host: str = "127.0.0.1"
    port: int = 8000
    app_title: str = "SDLC Skill Runner"
    http_referer: str = "http://localhost:8000"
    app_name: str = "SDLC Skill Runner"

    def resolved_browse_root(self) -> Path:
        root = self.browse_root
        if root is None or str(root).strip() in {"", ".", "./"}:
            return Path.home().resolve()
        return Path(root).expanduser().resolve()

    def default_workspace(self) -> Path:
        return self.resolved_browse_root()

    def resolved_skills_dir(self) -> Path:
        path = self.skills_dir
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path.resolve()


settings = Settings()
