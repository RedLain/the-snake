"""Модуль игры "Змейка".

Реализация классической игры "Змейка" с использованием библиотеки Pygame.
Содержит классы игровых объектов (GameObject, Snake, Apple),
функции управления и основной игровой цикл.

Игровой процесс:
    - Змейка управляется стрелками клавиатуры
    - Цель - съедать яблоки, увеличивая длину змейки
    - При столкновении с собственным телом игра перезапускается
    - Змейка может проходить сквозь границы игрового поля

Константы:
    SCREEN_WIDTH, SCREEN_HEIGHT: размеры игрового окна
    GRID_SIZE: размер клетки сетки
    SPEED: скорость движения змейки
    BOARD_BACKGROUND_COLOR: цвет фона
    APPLE_COLOR: цвет яблока
    SNAKE_COLOR: цвет змейки
"""

from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов.

    Предоставляет общие атрибуты и методы для игровых объектов:
        - position: координаты объекта на игровом поле
        - body_color: цвет объекта
        - _draw_cell(): рисует отдельную клетку
        - draw(): абстрактный метод отрисовки объекта
    """

    def __init__(self, body_color=None):
        """Инициализирует игровой объект с заданным цветом.

        Args:
            body_color: RGB-кортеж цвета объекта. По умолчанию None.
        """
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def _draw_cell(self, position=None, color=None):
        """Рисует одну клетку на игровом поле (защищенный метод).

        Используется для отрисовки отдельных сегментов змейки или яблока.

        Args:
            position: Координаты клетки (x, y). Если не указаны, используется
                      позиция самого объекта (self.position).
            color:   Цвет клетки в формате RGB. Если не указан, используется
                      цвет самого объекта (self.body_color).
        """
        pos = position if position is not None else self.position
        col = color if color is not None else self.body_color

        rect = pg.Rect(pos, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, col, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Абстрактный метод для отрисовки объекта.

        Должен быть переопределен в дочерних классах.
        """
        raise NotImplementedError(
            'Метод draw() должен быть переопределен'
            f'в классе {self.__class__.__name__}'
        )


class Apple(GameObject):
    """Класс яблока - объекта, который появляется на игровом поле.

    Яблоко занимает одну клетку игрового поля.
    При съедании змейкой появляется в новой случайной позиции.
    """

    def __init__(self, occupied_cells=None):
        """Инициализирует яблоко со случайной позицией.

        Args:
            occupied_cells: Множество занятых клеток (позиций змейки).
        """
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=None):
        """Устанавливает случайную позицию яблока на игровом поле.

        Координаты генерируются в пределах игрового поля
        с учетом размера сетки. Яблоко не появляется в занятых клетках.

        Args:
            occupied_cells: Множество занятых клеток (позиций змейки).
        """
        if occupied_cells is None:
            occupied_cells = set()

        # Генерируем позицию, пока она не будет свободна
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in occupied_cells:
                self.position = new_position
                break

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self._draw_cell()


class Snake(GameObject):
    """Класс змейки - основного игрового объекта.

    Управляет состоянием змейки:
        - positions: список координат сегментов
        - direction: текущее направление движения
        - length: длина змейки
        - next_direction: следующее направление (после нажатия клавиши)

    Методы:
        - move(): обновляет позицию змейки
        - update_direction(): применяет новое направление
        - reset(): сбрасывает змейку в начальное состояние
    """

    def __init__(self):
        """Инициализирует змейку с начальными параметрами."""
        super().__init__(SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки.

        Returns:
            tuple: Координаты головы змейки (x, y).
        """
        return self.positions[0]

    def move(self):
        """Обновляет позицию змейки, двигая её в текущем направлении.

        Шаг движения соответствует размеру клетки GRID_SIZE.
        При выходе за границы поля змейка появляется с противоположной стороны.
        После движения удаляет последний сегмент, если длина не увеличилась.
        """
        head_x, head_y = self.get_head_position()

        direction_x, direction_y = self.direction
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def update_direction(self, new_direction=None):
        """Обновляет текущее направление движения.

        Args:
            new_direction: Новое направление движения.
            Если None - ничего не меняется.
        """
        if new_direction:
            self.direction = new_direction

    def reset(self):
        """Сбрасывает змейку в начальное состояние.

        Длина становится равной 1, позиция - центр экрана,
        направление выбирается случайным образом.
        """
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))  # Используем кортеж
        self.last = None

    def draw(self):
        """Отрисовывает змейку на экране.

        Рисует голову змейки и затирает последний сегмент.
        Тело не перерисовывается целиком для оптимизации.
        """
        # Сначала затираем последний сегмент
        if self.last:
            self._draw_cell(position=self.last, color=BOARD_BACKGROUND_COLOR)

        # Отрисовка головы змейки
        head_position = self.get_head_position()
        self._draw_cell(position=head_position)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой.

    При нажатии стрелок устанавливает новое направление движения.
    Запрещает поворот на противоположное направление.

    Args:
        snake: Объект змейки для управления.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Игрок закрыл окно игры')

        if event.type == pg.KEYDOWN:
            # Словарь для сопоставления клавиш и направлений
            key_to_direction = {
                pg.K_UP: UP,
                pg.K_DOWN: DOWN,
                pg.K_LEFT: LEFT,
                pg.K_RIGHT: RIGHT,
            }

            # Словарь противоположных направлений
            opposite_directions = {
                UP: DOWN,
                DOWN: UP,
                LEFT: RIGHT,
                RIGHT: LEFT,
            }

            new_direction = key_to_direction.get(event.key)

            # Проверяем, что новое направление не противоположно текущему
            opposite = opposite_directions.get(snake.direction)
            if new_direction and new_direction != opposite:
                snake.update_direction(new_direction)


def main():
    """Основная функция игры, содержащая игровой цикл."""
    pg.init()

    snake = Snake()
    apple = Apple(occupied_cells=set(snake.positions))

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.move()

        # Получаем позицию головы один раз
        head_position = snake.get_head_position()

        # Проверка съедения яблока
        if head_position == apple.position:
            snake.length += 1
            # Передаем занятые клетки при генерации новой позиции
            occupied_cells = set(snake.positions)
            apple.randomize_position(occupied_cells)

        # Проверка столкновения с собой
        if head_position in snake.positions[1:]:
            snake.reset()
            # После сброса змейки обновляем позицию яблока
            occupied_cells = set(snake.positions)
            apple.randomize_position(occupied_cells)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
