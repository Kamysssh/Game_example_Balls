"""
Модуль игровой логики для игры про шарики.
Содержит всю логику без визуального интерфейса.
"""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Ball:
    """Класс для представления шарика."""
    x: float
    y: float
    vx: float  # скорость по x
    vy: float  # скорость по y
    radius: float
    color: Tuple[int, int, int]  # RGB цвет
    id: int = field(default_factory=lambda: random.randint(0, 1000000))
    
    def move(self, dt: float = 1.0):
        """Двигает шарик согласно его скорости."""
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def distance_to(self, other: 'Ball') -> float:
        """Вычисляет расстояние до другого шарика."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def distance_to_point(self, px: float, py: float) -> float:
        """Вычисляет расстояние до точки."""
        return math.sqrt((self.x - px)**2 + (self.y - py)**2)
    
    def is_colliding(self, other: 'Ball') -> bool:
        """Проверяет, касается ли этот шарик другого."""
        return self.distance_to(other) <= (self.radius + other.radius)
    
    def copy(self) -> 'Ball':
        """Создаёт копию шарика."""
        return Ball(
            x=self.x,
            y=self.y,
            vx=self.vx,
            vy=self.vy,
            radius=self.radius,
            color=self.color,
            id=self.id
        )


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Конвертирует RGB в HSV."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    
    if max_c == min_c:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    s = 0 if max_c == 0 else (diff / max_c)
    v = max_c
    
    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Конвертирует HSV в RGB."""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def mix_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Смешивает два цвета через математическое усреднение RGB.
    Использует нормализацию для предотвращения посерения цветов.
    """
    # Математическое усреднение RGB компонентов
    r_avg = (color1[0] + color2[0]) / 2
    g_avg = (color1[1] + color2[1]) / 2
    b_avg = (color1[2] + color2[2]) / 2
    
    # Вычисляем насыщенность результата
    max_component = max(r_avg, g_avg, b_avg)
    min_component = min(r_avg, g_avg, b_avg)
    
    # Если все компоненты примерно равны (серый цвет), нормализуем
    if max_component > 0:
        saturation = (max_component - min_component) / max_component
    else:
        saturation = 0
    
    # Минимальная целевая насыщенность
    MIN_SATURATION = 0.35
    
    if saturation < MIN_SATURATION:
        # Цвет слишком серый - применяем специальную логику
        
        # Проверяем, все ли компоненты примерно равны (допуск ±2)
        if abs(r_avg - g_avg) < 2 and abs(g_avg - b_avg) < 2 and abs(r_avg - b_avg) < 2:
            # Идеально серый - это комплементарные цвета
            # Используем несимметричное взвешивание на основе яркости цветов
            
            # Вычисляем яркость каждого цвета (взвешенная сумма)
            brightness1 = color1[0] * 0.299 + color1[1] * 0.587 + color1[2] * 0.114
            brightness2 = color2[0] * 0.299 + color2[1] * 0.587 + color2[2] * 0.114
            
            total_brightness = brightness1 + brightness2
            
            if total_brightness > 0:
                # Вычисляем веса: более яркий цвет получает больший вес (60-65%)
                weight1 = brightness1 / total_brightness
                weight2 = brightness2 / total_brightness
                
                # Применяем небольшое смещение в сторону более яркого цвета
                # Это делает результат менее симметричным и более насыщенным
                # Используем меньший коэффициент для более сбалансированного результата
                if weight1 > weight2:
                    weight1 = min(0.75, weight1 * 1.15)  # Усиливаем, но ограничиваем
                    weight2 = 1 - weight1
                else:
                    weight2 = min(0.75, weight2 * 1.15)
                    weight1 = 1 - weight2
                    
                # Применяем взвешенное усреднение
                r_final = int(color1[0] * weight1 + color2[0] * weight2)
                g_final = int(color1[1] * weight1 + color2[1] * weight2)
                b_final = int(color1[2] * weight1 + color2[2] * weight2)
            else:
                # Оба цвета чёрные
                r_final = int(r_avg)
                g_final = int(g_avg)
                b_final = int(b_avg)
            
        elif max_component > 0:
            # Не идеально серый, но недостаточно насыщенный
            # Находим средний уровень яркости
            brightness = (r_avg + g_avg + b_avg) / 3
            
            # Усиливаем различия между компонентами относительно среднего
            # Коэффициент усиления зависит от того, насколько серый цвет
            boost_factor = (MIN_SATURATION - saturation) / MIN_SATURATION + 1
            
            # Применяем усиление к отклонениям от среднего
            r_boosted = brightness + (r_avg - brightness) * boost_factor
            g_boosted = brightness + (g_avg - brightness) * boost_factor
            b_boosted = brightness + (b_avg - brightness) * boost_factor
            
            # Масштабируем, чтобы максимальный компонент был близок к 255
            # Это сохраняет яркость цвета
            max_boosted = max(r_boosted, g_boosted, b_boosted)
            if max_boosted > 0:
                scale = min(255 / max_boosted, 1.5)  # Ограничиваем масштабирование
                r_boosted *= scale
                g_boosted *= scale
                b_boosted *= scale
            
            # Ограничиваем диапазон [0, 255]
            r_final = max(0, min(255, int(r_boosted)))
            g_final = max(0, min(255, int(g_boosted)))
            b_final = max(0, min(255, int(b_boosted)))
        else:
            # Чёрный цвет - возвращаем как есть
            r_final = int(r_avg)
            g_final = int(g_avg)
            b_final = int(b_avg)
    else:
        # Цвет достаточно насыщенный - используем прямое усреднение
        r_final = int(r_avg)
        g_final = int(g_avg)
        b_final = int(b_avg)
    
    return (r_final, g_final, b_final)


class GameLogic:
    """Основной класс игровой логики."""
    
    def __init__(self, width: float, height: float):
        """
        Инициализирует игровую логику.
        
        Args:
            width: ширина игрового поля
            height: высота игрового поля
        """
        self.width = width
        self.height = height
        self.balls: List[Ball] = []
        self.inventory: List[Ball] = []
        self.delete_zone = {
            'x': width - 100,
            'y': 0,
            'width': 100,
            'height': 100
        }
        self.next_ball_id = 0
        
    def add_ball(self, x: float, y: float, vx: float, vy: float, 
                 radius: float, color: Tuple[int, int, int]) -> Ball:
        """Добавляет новый шарик на поле."""
        ball = Ball(x, y, vx, vy, radius, color, self.next_ball_id)
        self.next_ball_id += 1
        self.balls.append(ball)
        return ball
    
    def create_random_ball(self) -> Ball:
        """Создаёт случайный шарик."""
        x = random.uniform(50, self.width - 50)
        y = random.uniform(50, self.height - 50)
        vx = random.uniform(-5, 5)
        vy = random.uniform(-5, 5)
        radius = random.uniform(15, 30)
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        return self.add_ball(x, y, vx, vy, radius, color)
    
    def update(self, dt: float = 1.0):
        """
        Обновляет состояние игры.
        
        Args:
            dt: временной шаг
        """
        # Двигаем все шарики
        for ball in self.balls:
            ball.move(dt)
            self._handle_wall_collision(ball)
        
        # Проверяем коллизии и смешиваем цвета
        self._handle_ball_collisions()
    
    def _handle_wall_collision(self, ball: Ball):
        """Обрабатывает столкновение шарика со стенами."""
        # Левая и правая стены
        if ball.x - ball.radius < 0:
            ball.x = ball.radius
            ball.vx = abs(ball.vx)
        elif ball.x + ball.radius > self.width:
            ball.x = self.width - ball.radius
            ball.vx = -abs(ball.vx)
        
        # Верхняя и нижняя стены
        if ball.y - ball.radius < 0:
            ball.y = ball.radius
            ball.vy = abs(ball.vy)
        elif ball.y + ball.radius > self.height:
            ball.y = self.height - ball.radius
            ball.vy = -abs(ball.vy)
    
    def _handle_ball_collisions(self):
        """
        Обрабатывает столкновения шариков друг с другом.
        При столкновении шарики смешивают цвета, но не отталкиваются.
        """
        # Используем множество для отслеживания уже проверенных пар
        merged_pairs = set()
        
        for i, ball1 in enumerate(self.balls):
            for j, ball2 in enumerate(self.balls):
                if i >= j:  # Пропускаем себя и уже проверенные пары
                    continue
                
                pair_id = (ball1.id, ball2.id)
                if pair_id in merged_pairs:
                    continue
                
                if ball1.is_colliding(ball2):
                    # Смешиваем цвета
                    new_color = mix_colors(ball1.color, ball2.color)
                    ball1.color = new_color
                    ball2.color = new_color
                    
                    # Запоминаем, что эта пара уже смешала цвета
                    merged_pairs.add(pair_id)
    
    def suck_ball(self, mouse_x: float, mouse_y: float, suck_radius: float = 50) -> Optional[Ball]:
        """
        Всасывает шарик в инвентарь, если он находится рядом с курсором.
        
        Args:
            mouse_x: координата X мыши
            mouse_y: координата Y мыши
            suck_radius: радиус всасывания
            
        Returns:
            Всосанный шарик или None
        """
        for ball in self.balls[:]:  # Копируем список для безопасного удаления
            if ball.distance_to_point(mouse_x, mouse_y) <= suck_radius:
                self.balls.remove(ball)
                self.inventory.append(ball)
                return ball
        return None
    
    def spit_ball(self, mouse_x: float, mouse_y: float, 
                  direction_x: float = 0, direction_y: float = 0,
                  speed: float = 3.0) -> Optional[Ball]:
        """
        Выплёвывает шарик из инвентаря в указанную позицию.
        
        Args:
            mouse_x: координата X для размещения шарика
            mouse_y: координата Y для размещения шарика
            direction_x: направление скорости по X
            direction_y: направление скорости по Y
            speed: скорость выплёвывания
            
        Returns:
            Выплюнутый шарик или None, если инвентарь пуст
        """
        if not self.inventory:
            return None
        
        ball = self.inventory.pop(0)  # Берём первый шарик из инвентаря
        ball.x = mouse_x
        ball.y = mouse_y
        
        # Нормализуем направление
        magnitude = math.sqrt(direction_x**2 + direction_y**2)
        if magnitude > 0:
            ball.vx = (direction_x / magnitude) * speed
            ball.vy = (direction_y / magnitude) * speed
        else:
            # Случайное направление, если не указано
            angle = random.uniform(0, 2 * math.pi)
            ball.vx = math.cos(angle) * speed
            ball.vy = math.sin(angle) * speed
        
        self.balls.append(ball)
        return ball
    
    def check_delete_zone(self) -> List[Ball]:
        """
        Проверяет, какие шарики находятся в зоне удаления, и удаляет их.
        
        Returns:
            Список удалённых шариков
        """
        deleted = []
        dz = self.delete_zone
        
        for ball in self.balls[:]:
            if (dz['x'] <= ball.x <= dz['x'] + dz['width'] and
                dz['y'] <= ball.y <= dz['y'] + dz['height']):
                self.balls.remove(ball)
                deleted.append(ball)
        
        return deleted
    
    def get_ball_at_position(self, x: float, y: float) -> Optional[Ball]:
        """
        Возвращает шарик в указанной позиции (если есть).
        
        Args:
            x: координата X
            y: координата Y
            
        Returns:
            Шарик или None
        """
        for ball in self.balls:
            if ball.distance_to_point(x, y) <= ball.radius:
                return ball
        return None
    
    def get_balls_in_radius(self, x: float, y: float, radius: float) -> List[Ball]:
        """
        Возвращает все шарики в указанном радиусе от точки.
        
        Args:
            x: координата X центра
            y: координата Y центра
            radius: радиус поиска
            
        Returns:
            Список шариков
        """
        result = []
        for ball in self.balls:
            if ball.distance_to_point(x, y) <= radius:
                result.append(ball)
        return result
    
    def clear_all(self):
        """Очищает все шарики и инвентарь."""
        self.balls.clear()
        self.inventory.clear()
    
    def get_state(self) -> dict:
        """
        Возвращает текущее состояние игры в виде словаря.
        Полезно для сохранения/загрузки или для UI.
        """
        return {
            'width': self.width,
            'height': self.height,
            'balls': [
                {
                    'x': b.x,
                    'y': b.y,
                    'vx': b.vx,
                    'vy': b.vy,
                    'radius': b.radius,
                    'color': b.color,
                    'id': b.id
                }
                for b in self.balls
            ],
            'inventory': [
                {
                    'x': b.x,
                    'y': b.y,
                    'vx': b.vx,
                    'vy': b.vy,
                    'radius': b.radius,
                    'color': b.color,
                    'id': b.id
                }
                for b in self.inventory
            ],
            'delete_zone': self.delete_zone
        }
    
    def set_delete_zone(self, x: float, y: float, width: float, height: float):
        """Устанавливает зону удаления."""
        self.delete_zone = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }


# Вспомогательные функции для тестирования

def create_test_game() -> GameLogic:
    """Создаёт тестовую игру с несколькими шариками."""
    game = GameLogic(800, 600)
    
    # Добавляем несколько шариков разных цветов
    game.add_ball(100, 100, 1, 1, 20, (255, 0, 0))  # Красный
    game.add_ball(200, 150, -1, 0.5, 25, (0, 255, 0))  # Зелёный
    game.add_ball(300, 200, 0.5, -1, 22, (0, 0, 255))  # Синий
    game.add_ball(400, 250, -0.5, -0.5, 18, (255, 255, 0))  # Жёлтый
    game.add_ball(500, 300, 1, -1, 28, (255, 0, 255))  # Пурпурный
    
    return game


if __name__ == '__main__':
    # Демонстрация работы логики
    print("Создание тестовой игры...")
    game = create_test_game()
    
    print(f"Начальное количество шариков: {len(game.balls)}")
    print(f"Размер инвентаря: {len(game.inventory)}")
    
    # Симулируем несколько кадров
    print("\nСимуляция 5 кадров движения...")
    for i in range(5):
        game.update(dt=1.0)
        print(f"Кадр {i+1}: шариков на поле = {len(game.balls)}")
    
    # Всасываем шарик
    print("\nВсасывание шарика рядом с позицией (100, 100)...")
    sucked = game.suck_ball(100, 100, suck_radius=50)
    if sucked:
        print(f"Всосан шарик с цветом {sucked.color}")
        print(f"Шариков на поле: {len(game.balls)}, в инвентаре: {len(game.inventory)}")
    
    # Выплёвываем шарик обратно
    print("\nВыплёвывание шарика на позицию (400, 300)...")
    spat = game.spit_ball(400, 300, direction_x=1, direction_y=0, speed=2.0)
    if spat:
        print(f"Выплюнут шарик с цветом {spat.color}")
        print(f"Шариков на поле: {len(game.balls)}, в инвентаре: {len(game.inventory)}")
    
    # Проверяем зону удаления
    print("\nПроверка зоны удаления...")
    deleted = game.check_delete_zone()
    print(f"Удалено шариков: {len(deleted)}")
    
    print("\nГотово! Логика работает корректно.")
