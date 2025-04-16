from pydantic import BaseModel, Field

class ScrapeRequest(BaseModel):
    search_term: str = Field(default="software engineer")
    location: str = Field(default="India")
    results_wanted: int = Field(default=20, ge=1, le=100)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
