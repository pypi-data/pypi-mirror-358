from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    """Database Settings"""

    host: str
    port: int = 5432
    name: str
    user: str
    password: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
