from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Асинхронный менеджер контекста для жизненного цикла приложения"""
    # Создание таблиц при запуске
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # Очистка при завершении (опционально)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


app = FastAPI(lifespan=lifespan)


@app.get("/recipes/", response_model=List[schemas.RecipeListItem])
async def read_recipes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[schemas.RecipeListItem]:
    result = await db.execute(
        select(models.Recipe)
        .order_by(models.Recipe.views.desc(), models.Recipe.cooking_time.asc())
        .offset(skip)
        .limit(limit)
    )
    recipes = result.scalars().all()
    return [schemas.RecipeListItem.model_validate(recipe) for recipe in recipes]


@app.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
async def read_recipe(
    recipe_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.Recipe:
    result = await db.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe = result.scalars().first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views = 0 if recipe.views is None else recipe.views
    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)
    return schemas.Recipe.model_validate(recipe)


@app.post("/recipes/", response_model=schemas.Recipe, status_code=201)
async def create_recipe(
    recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)
) -> schemas.Recipe:
    db_recipe = models.Recipe(
        name=recipe.name,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        description=recipe.description,
    )
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return schemas.Recipe.model_validate(db_recipe)
