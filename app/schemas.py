from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class RecipeListItem(BaseModel):
    id: int
    name: str
    cooking_time: int
    views: int

    model_config = ConfigDict(from_attributes=True)
