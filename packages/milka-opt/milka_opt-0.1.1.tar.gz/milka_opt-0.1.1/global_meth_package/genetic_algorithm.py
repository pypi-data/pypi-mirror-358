import numpy as np

def optimize(f, bounds, population_size=30, generations=100, mutation_rate=0.1, seed=42, **kwargs):
    # f — минимизируемая функция
    # bounds — границы для каждой переменной
    # population_size — количество особей
    # generations — число поколений (итераций)
    # mutation_rate — вероятность мутации
    # seed — для генератора случайных чисел
    # **kwargs — дополнительные параметры

    rng = np.random.default_rng(seed)

    # Создание случайной особи
    def create_indiv(bounds):
        indiv = []
        for (low, high) in bounds:
            value =  rng.uniform(low, high)
            indiv.append(value)
        return indiv

    # Оценка приспособленности
    def fitness(individ):
        return f(individ)

    # Скрещивание
    def crossover(parent1, parent2):
        # Создаются дети как смесь родителей
        child = []
        for i in range(len(parent1)):
            # Коэффициент альфа для каждой координаты
            alpha = rng.random()
            # Создание новой особи на основе линейной комбинации двух родителей
            value = alpha * parent1[i] + (1 - alpha) * parent2[i]
            child.append(value)
        return child

    # Мутация
    def mutate(individ, bounds, mutation_rate):
        for i in range(len(individ)):
            # Генерация случайного числа от 0 до 1
            # Если число меньше вероятности мутации, то ген мутирует
            if (rng.random() < mutation_rate):
                # Границы допустимого значения для гена
                low, high = bounds[i]
                # К текущему значению добавляется случайное число от -1 до 1
                individ[i] += rng.uniform(-1, 1)
                # Обрезаем полученное значение, если оно вышло за границы
                individ[i] = np.clip(individ[i], low, high)
        return individ

    # Селекция (отбор) лучших решений
    def select(population, scores, k=3):
        # Случайный выбор k особей из популяции
        selected = rng.choice(len(population), k, replace=False)
        # Поиск наилучшей особи из выбранных по оценке приспособленности
        best = min(selected, key=lambda i: scores[i])
        return population[best]

    # Инициализация популяции
    population = []
    for _ in range(population_size):
        population.append(create_indiv(bounds))

    # Оценка начальной популяции
    scores = []
    for ind in population:
        scores.append(fitness(ind))

    best_index = np.argmin(scores)
    best_solution = population[best_index]
    best_score = scores[best_index]

    # Основной цикл
    for gen in range(generations):
        new_population = []
        for _ in range(population_size):
            # Отбор родителей
            parent1 = select(population, scores)
            parent2 = select(population, scores)
            # Скрещивание
            child = crossover(parent1, parent2)
            # Мутация, добавление случайного шума для поддержания разнообразия
            child = mutate(child, bounds, mutation_rate)
            new_population.append(child)

        # Оценка новой популяции
        scores = []
        for ind in new_population:
            scores.append(fitness(ind))
        population = new_population

        # Обновление лучшего решения
        gen_best_index = np.argmin(scores)
        if scores[gen_best_index] < best_score:
            best_solution = population[gen_best_index]
            best_score = scores[gen_best_index]

    return best_solution, best_score
