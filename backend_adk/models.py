from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    agent_id: str
    role: str = Field(default="Senior Software Engineer", max_length=160)
    company: str = Field(default="", max_length=160)
    seniority: str = Field(default="Senior", max_length=80)
    job_description: str = Field(default="", max_length=12000)
    question: str = Field(default="", max_length=2000)
    answer: str = Field(default="", max_length=12000)


class RunResponse(BaseModel):
    agent: dict[str, str]
    response: str
    steps: list[dict[str, str]]
    data: dict[str, object]
    provider: str
    model: str
