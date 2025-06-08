from fastapi.testclient import TestClient

from app import schemas


def test_create_recipe(client: TestClient) -> None:
    recipe_data = {
        "name": "Тестовый рецепт",
        "cooking_time": 30,
        "ingredients": "ингредиенты",
        "description": "описание",
    }

    response = client.post("/recipes/", json=recipe_data)
    assert response.status_code == 201
    data = response.json()

    assert data["name"] == recipe_data["name"]
    assert data["cooking_time"] == recipe_data["cooking_time"]
    assert data["ingredients"] == recipe_data["ingredients"]
    assert data["description"] == recipe_data["description"]
    assert data["views"] == 0
    assert isinstance(data["id"], int)


def test_read_recipes(client: TestClient) -> None:
    # Сначала создаем тестовый рецепт
    client.post(
        "/recipes/",
        json={
            "name": "Тест",
            "cooking_time": 10,
            "ingredients": "тест",
            "description": "тест",
        },
    )

    response = client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert schemas.RecipeListItem(**data[0])


def test_read_recipe(client: TestClient) -> None:
    # Создаем рецепт
    create_res = client.post(
        "/recipes/",
        json={
            "name": "Для теста",
            "cooking_time": 15,
            "ingredients": "тест",
            "description": "тест",
        },
    )
    recipe_id = create_res.json()["id"]

    # Проверяем получение
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == recipe_id
    assert data["views"] == 1
    assert schemas.Recipe(**data)
