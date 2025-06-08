from pydantic import BaseModel


class RecipeBase(BaseModel):
    name: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int
    views: int

    class Config:
        orm_mode = True


class RecipeListItem(BaseModel):
    id: int
    name: str
    cooking_time: int
    views: int

    class Config:
        orm_mode = True
