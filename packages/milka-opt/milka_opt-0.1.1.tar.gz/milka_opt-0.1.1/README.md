# Global_Meth_Package

**Global_meth_Package** — это Python-библиотека, реализующая популярные методы глобальной оптимизации, такие как:
- Метод ветвей и границ
- Сеточный поиск
- Метод Монте-Карло
- Имитация отжига
- Генетический алгоритм

Библиотека создана в учебно-исследовательских целях, легко расширяема, адаптирована под общее API.


## Установка

Установить из PyPI:

```bash
pip install milka-opt
```

Или локально из исходников:

```bash
git clone https://github.com/milka-bulka/global_meth_package.git
cd global_meth_package
pip install .
```


## Структура проекта

```bash
global_meth_package/
│
├── branch_and_bound.py       # Метод ветвей и границ
├── grid_search.py            # Сеточный поиск
├── monte_carlo.py            # Метод Монте-Карло
├── simulated_annealing.py    # Имитация отжига
├── genetic_algorithm.py      # Генетический алгоритм
├── utils.py                  # Тестовые функции
├── __init__.py               # Объединение методов в единый API
│
tests/
├── test_branch_and_bound.py
├── test_grid_search.py
├── test_monte_carlo.py
├── test_simulated_annealing.py
├── test_genetic_algorithm.py
│
pyproject.toml                # Настройки проекта
README.md                     # Документация
```


## Использование

Пример использования метода Монте-Карло:

```python
from global_meth_package.monte_carlo import monte_carlo
from global_meth_package.utils import rastrigin

bounds = [(-5.12, 5.12)] * 3  # 3 переменные
result = monte_carlo(rastrigin, bounds)
print("Minimum found at:", result[0])
print("Function value:", result[1])
```


## Тестирование

Тесты написаны с использованием `pytest`.

Запуск всех тестов:

```bash
pytest tests/
```


## Реализованные методы

| Метод                  | Модуль                  | Аргументы по умолчанию                        |
|------------------------|-------------------------|-----------------------------------------------|
| Ветвей и границ        | `branch_and_bound()`    | `max_iter=500, eps=1e-5, L=10.0`              |
| Сеточный поиск         | `grid_search()`         | `grid_size=30`                                |
| Монте-Карло            | `monte_carlo()`         | `max_iter=10000, seed=None`                   |
| Имитация отжига        | `simulated_annealing()` | `max_iter=10000, T_start=1000, alpha=0.995`   |
| Генетический алгоритм  | `genetic_algorithm()`   | `population_size=30, generations=100`         |


## Поддерживаемые функции

```python
from global_meth_package.utils import rastrigin, rosenbrock, booth
```

- `rastrigin(x)` — функция Растригина
- `booth(x)` — функция Бута
- `rosenbrock(x)` — функция Розенброка

## Лицензия

MIT License

## Автор

**milka_bulka**  
GitHub: [milka-bulka](https://github.com/milka-bulka)

## Публикация на PyPI

Сборка и публикация:

```bash
python -m build
twine upload dist/*
```

(не забудьте настроить `.pypirc` для удобства)


## Обратная связь

Если вы нашли ошибку или хотите предложить улучшение — создайте issue или pull request.
