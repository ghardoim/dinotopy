from pydantic import BaseModel, Field
from typing import List

class WhenLived(BaseModel):
    period: str = Field(..., description="Period in which the dinosaur lived")
    lived: str = Field(..., description="Time in which the dinosaur lived")

class TaxonomicDetails(BaseModel):
    taxonomy: List[str] = Field(..., description="The entire taxonomic tree of the dinosaur")
    named_by: str = Field(..., description="Just the name of who named the dinosaur")
    named_in: str = Field(..., description="Just the year in which the dinosaur was named")
    type_species: str = Field(..., description="Type of specimen of the dinosaur")

class Dinosaur(BaseModel):
    img_url: str = Field(..., description="URL of the image of the dinosaur")
    name: str = Field(..., description="Name of the dinosaur")
    pronunciation: str = Field(..., description="Pronunciation of the dinosaur's name")
    meaning: str = Field(..., description="Meaning of the dinosaur's name")
    diet: str = Field(..., description="Diet of the dinosaur")
    when_lived: WhenLived = Field(..., description="When the dinosaur lived")
    found_in: str = Field(..., description="Where the dinosaur was found")
    size: str = Field(..., description="Size of the dinosaur")
    type_of: str = Field(..., description="Type of the dinosaur")
    length: str = Field(..., description="Length of the dinosaur")
    description: str = Field(..., description="All text content about the dinosaur")
    details: TaxonomicDetails = Field(..., description="Taxonomic details of the dinosaur")