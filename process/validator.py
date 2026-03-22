from pydantic import BaseModel, Field

class ConceptSchema(BaseModel):
    title: str = Field(..., description="The name of the AI concept")
    summary: str = Field(..., description="1-sentence summary")
    explanation: str = Field(..., description="ELI5 explanation")
    analogy: str = Field(..., description="A simple real-world analogy")
    example: str = Field(..., description="A practical use case")

class ExtractedTerm(BaseModel):
    term: str
    context: str
    source: str