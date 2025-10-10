"""
Графический интерфейс для игры про шарики.
Использует pygame для визуализации и logic.py для игровой логики.
"""

import pygame
import sys
import math
from logic import GameLogic, Ball
from typing import Optional, Tuple

# ============================================================================
# НАСТРОЙКИ ИГРЫ
# ============================================================================

# Размеры окна
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Стартовое количество шариков
INITIAL_BALLS_COUNT = 30

# Цвета
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (200, 200, 200)
COLOR_LIGHT_GRAY = (240, 240, 240)
COLOR_RED = (255, 100, 100)
COLOR_GREEN = (100, 255, 100)
COLOR_BLUE = (100, 150, 255)
COLOR_DARK_RED = (200, 50, 50)

# Параметры всасывания
SUCK_RADIUS = 60
SUCK_ANIMATION_RADIUS = 80

# FPS
FPS = 60


# ============================================================================
# КЛАСС ИГРЫ
# ============================================================================

class BallGame:
    """Основной класс игры с графическим интерфейсом."""
    
    def __init__(self):
        """Инициализирует игру."""
        pygame.init()
        
        # Создаём окно
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Игра про шарики 🎨")
        
        # Часы для контроля FPS
        self.clock = pygame.time.Clock()
        
        # Игровая логика
        self.game_logic = GameLogic(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Настраиваем зону удаления в правом верхнем углу
        self.game_logic.set_delete_zone(
            WINDOW_WIDTH - 120,
            10,
            110,
            110
        )
        
        # Создаём начальные шарики
        for _ in range(INITIAL_BALLS_COUNT):
            self.game_logic.create_random_ball()
        
        # Состояние мыши
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.right_mouse_pressed = False
        
        # Анимация всасывания
        self.suck_animation_active = False
        self.suck_animation_time = 0
        
        # Перетаскивание шариков из инвентаря
        self.dragging_ball = None  # Шарик, который перетаскиваем
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_from_inventory = False
        
        # Шрифты
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # Состояние игры
        self.running = True
        self.paused = False
        
    def handle_events(self):
        """Обрабатывает события pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
                
                # Если перетаскиваем шарик, обновляем его позицию
                if self.dragging_ball:
                    self.dragging_ball.x = self.mouse_x + self.drag_offset_x
                    self.dragging_ball.y = self.mouse_y + self.drag_offset_y
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.mouse_pressed = True
                    # Сначала проверяем, кликнули ли по инвентарю
                    if not self.try_start_drag_from_inventory():
                        # Если нет, то всасываем шарик с поля
                        self.handle_left_click()
                elif event.button == 3:  # Правая кнопка мыши
                    self.right_mouse_pressed = True
                    self.handle_right_click()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
                    # Завершаем перетаскивание
                    if self.dragging_ball:
                        self.finish_dragging()
                elif event.button == 3:
                    self.right_mouse_pressed = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_n:
                    self.game_logic.create_random_ball()
                elif event.key == pygame.K_c:
                    self.game_logic.clear_all()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def handle_left_click(self):
        """Обрабатывает левый клик мыши (всасывание шарика)."""
        sucked = self.game_logic.suck_ball(
            self.mouse_x,
            self.mouse_y,
            SUCK_RADIUS
        )
        
        if sucked:
            # Активируем анимацию всасывания
            self.suck_animation_active = True
            self.suck_animation_time = 0
    
    def try_start_drag_from_inventory(self) -> bool:
        """
        Пытается начать перетаскивание шарика из инвентаря.
        Возвращает True, если перетаскивание началось.
        """
        if len(self.game_logic.inventory) == 0:
            return False
        
        # Координаты инвентаря
        start_x = 20
        start_y = WINDOW_HEIGHT - 200
        spacing = 45
        mini_radius = 15
        
        # Проверяем клик по каждому шарику в инвентаре
        for i, ball in enumerate(self.game_logic.inventory[:5]):
            inv_x = start_x + 20
            inv_y = start_y + i * spacing
            
            # Проверяем, попали ли в шарик
            distance = math.sqrt((self.mouse_x - inv_x)**2 + (self.mouse_y - inv_y)**2)
            if distance <= mini_radius + 5:
                # Начинаем перетаскивание
                self.dragging_ball = self.game_logic.inventory.pop(i)
                self.drag_from_inventory = True
                
                # Устанавливаем позицию шарика на курсор
                self.dragging_ball.x = self.mouse_x
                self.dragging_ball.y = self.mouse_y
                self.drag_offset_x = 0
                self.drag_offset_y = 0
                
                return True
        
        return False
    
    def finish_dragging(self):
        """Завершает перетаскивание шарика."""
        if not self.dragging_ball:
            return
        
        # Проверяем, попал ли шарик в зону удаления
        dz = self.game_logic.delete_zone
        if (dz['x'] <= self.dragging_ball.x <= dz['x'] + dz['width'] and
            dz['y'] <= self.dragging_ball.y <= dz['y'] + dz['height']):
            # Удаляем шарик
            pass  # Просто не добавляем его обратно
        else:
            # Добавляем шарик на поле с небольшой случайной скоростью
            import random
            self.dragging_ball.vx = random.uniform(-1.5, 1.5)
            self.dragging_ball.vy = random.uniform(-1.5, 1.5)
            self.game_logic.balls.append(self.dragging_ball)
        
        # Сбрасываем состояние перетаскивания
        self.dragging_ball = None
        self.drag_from_inventory = False
    
    def handle_right_click(self):
        """Обрабатывает правый клик мыши (выплёвывание шарика)."""
        if len(self.game_logic.inventory) > 0:
            # Вычисляем направление от центра экрана к курсору
            center_x = WINDOW_WIDTH // 2
            center_y = WINDOW_HEIGHT // 2
            
            direction_x = self.mouse_x - center_x
            direction_y = self.mouse_y - center_y
            
            self.game_logic.spit_ball(
                self.mouse_x,
                self.mouse_y,
                direction_x,
                direction_y,
                speed=4.0
            )
    
    def reset_game(self):
        """Сбрасывает игру к начальному состоянию."""
        self.game_logic.clear_all()
        for _ in range(INITIAL_BALLS_COUNT):
            self.game_logic.create_random_ball()
    
    def update(self):
        """Обновляет состояние игры."""
        if not self.paused:
            # Обновляем логику игры
            self.game_logic.update(dt=1.0)
            
            # Проверяем зону удаления
            deleted = self.game_logic.check_delete_zone()
            
            # Обновляем анимацию всасывания
            if self.suck_animation_active:
                self.suck_animation_time += 1
                if self.suck_animation_time > 15:  # 15 кадров анимации
                    self.suck_animation_active = False
    
    def draw(self):
        """Отрисовывает всё на экране."""
        # Фон
        self.screen.fill(COLOR_WHITE)
        
        # Зона удаления
        self.draw_delete_zone()
        
        # Шарики
        self.draw_balls()
        
        # Курсор и радиус всасывания
        self.draw_cursor()
        
        # UI элементы
        self.draw_ui()
        
        # Инвентарь
        self.draw_inventory()
        
        # Обновляем экран
        pygame.display.flip()
    
    def draw_balls(self):
        """Отрисовывает все шарики."""
        for ball in self.game_logic.balls:
            self.draw_3d_ball(ball)
        
        # Рисуем перетаскиваемый шарик поверх всех остальных
        if self.dragging_ball:
            self.draw_3d_ball(self.dragging_ball, is_dragging=True)
    
    def draw_3d_ball(self, ball: Ball, is_dragging: bool = False):
        """Рисует шарик с 3D эффектом."""
        x, y = int(ball.x), int(ball.y)
        radius = int(ball.radius)
        
        # Если шарик перетаскивается, добавляем тень
        if is_dragging:
            shadow_offset = 8
            self.draw_transparent_circle(
                x + shadow_offset,
                y + shadow_offset,
                radius,
                (0, 0, 0),
                alpha=80
            )
        
        # Тёмная тень снизу для объёма
        shadow_color = tuple(max(0, c - 80) for c in ball.color)
        for i in range(3):
            shadow_radius = radius - i
            shadow_y_offset = radius * 0.15 + i * 0.5
            pygame.draw.circle(
                self.screen,
                shadow_color,
                (x, int(y + shadow_y_offset)),
                shadow_radius
            )
        
        # Основной шарик - градиент от тёмного к светлому
        # Рисуем несколько слоёв для создания градиента
        for i in range(radius, 0, -2):
            # Вычисляем цвет для текущего слоя (от тёмного к основному)
            progress = i / radius
            layer_color = tuple(
                int(ball.color[j] * (0.5 + 0.5 * progress))
                for j in range(3)
            )
            pygame.draw.circle(
                self.screen,
                layer_color,
                (x, y),
                i
            )
        
        # Основной цвет
        pygame.draw.circle(
            self.screen,
            ball.color,
            (x, y),
            int(radius * 0.85)
        )
        
        # Большой блик в верхней левой части
        highlight_offset_x = -radius * 0.35
        highlight_offset_y = -radius * 0.35
        highlight_radius = radius * 0.45
        
        # Яркий блик
        highlight_color = tuple(min(255, c + 120) for c in ball.color)
        pygame.draw.circle(
            self.screen,
            highlight_color,
            (int(x + highlight_offset_x), int(y + highlight_offset_y)),
            int(highlight_radius)
        )
        
        # Маленький яркий блик для усиления эффекта
        small_highlight_x = -radius * 0.25
        small_highlight_y = -radius * 0.25
        small_highlight_radius = radius * 0.2
        
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(x + small_highlight_x), int(y + small_highlight_y)),
            int(small_highlight_radius)
        )
        
        # Обводка для чёткости
        outline_color = tuple(max(0, c - 60) for c in ball.color)
        pygame.draw.circle(
            self.screen,
            outline_color,
            (x, y),
            radius,
            2
        )
        
        # Дополнительная светлая обводка для глянца
        gloss_color = tuple(min(255, c + 40) for c in ball.color)
        pygame.draw.arc(
            self.screen,
            gloss_color,
            (x - radius, y - radius, radius * 2, radius * 2),
            math.pi * 0.7,
            math.pi * 1.3,
            2
        )
    
    def draw_cursor(self):
        """Отрисовывает курсор и радиус всасывания."""
        # Если перетаскиваем шарик, не показываем радиус всасывания
        if not self.dragging_ball:
            # Радиус всасывания (полупрозрачный круг)
            if self.mouse_pressed:
                # Более яркий круг при нажатии
                self.draw_transparent_circle(
                    self.mouse_x,
                    self.mouse_y,
                    SUCK_RADIUS,
                    COLOR_BLUE,
                    alpha=100
                )
            else:
                # Слабый круг в обычном состоянии
                self.draw_transparent_circle(
                    self.mouse_x,
                    self.mouse_y,
                    SUCK_RADIUS,
                    COLOR_GRAY,
                    alpha=50
                )
        
        # Анимация всасывания
        if self.suck_animation_active:
            progress = self.suck_animation_time / 15.0
            radius = SUCK_ANIMATION_RADIUS * (1 - progress)
            alpha = int(150 * (1 - progress))
            
            self.draw_transparent_circle(
                self.mouse_x,
                self.mouse_y,
                radius,
                COLOR_GREEN,
                alpha=alpha
            )
        
        # Крестик курсора (или стрелка при перетаскивании)
        if self.dragging_ball:
            # Показываем стрелку вниз при перетаскивании
            arrow_size = 15
            pygame.draw.polygon(
                self.screen,
                COLOR_BLACK,
                [
                    (self.mouse_x, self.mouse_y + arrow_size),
                    (self.mouse_x - arrow_size // 2, self.mouse_y),
                    (self.mouse_x + arrow_size // 2, self.mouse_y)
                ]
            )
            
            # Проверяем, над зоной удаления ли мы
            dz = self.game_logic.delete_zone
            if (dz['x'] <= self.mouse_x <= dz['x'] + dz['width'] and
                dz['y'] <= self.mouse_y <= dz['y'] + dz['height']):
                # Показываем предупреждение
                warning_text = self.font_small.render("Удалить!", True, COLOR_RED)
                self.screen.blit(warning_text, (self.mouse_x + 20, self.mouse_y - 20))
        else:
            # Обычный крестик
            cursor_size = 10
            pygame.draw.line(
                self.screen,
                COLOR_BLACK,
                (self.mouse_x - cursor_size, self.mouse_y),
                (self.mouse_x + cursor_size, self.mouse_y),
                2
            )
            pygame.draw.line(
                self.screen,
                COLOR_BLACK,
                (self.mouse_x, self.mouse_y - cursor_size),
                (self.mouse_x, self.mouse_y + cursor_size),
                2
            )
    
    def draw_transparent_circle(self, x: int, y: int, radius: float, 
                                color: Tuple[int, int, int], alpha: int = 128):
        """Рисует полупрозрачный круг."""
        if radius <= 0:
            return
        
        # Создаём временную поверхность с альфа-каналом
        surface = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(
            surface,
            (*color, alpha),
            (int(radius), int(radius)),
            int(radius)
        )
        
        # Рисуем на основном экране
        self.screen.blit(
            surface,
            (int(x - radius), int(y - radius))
        )
    
    def draw_delete_zone(self):
        """Отрисовывает зону удаления."""
        dz = self.game_logic.delete_zone
        
        # Фон зоны удаления
        pygame.draw.rect(
            self.screen,
            COLOR_RED,
            (dz['x'], dz['y'], dz['width'], dz['height'])
        )
        
        # Рамка
        pygame.draw.rect(
            self.screen,
            COLOR_DARK_RED,
            (dz['x'], dz['y'], dz['width'], dz['height']),
            3
        )
        
        # Иконка корзины (упрощённая)
        center_x = dz['x'] + dz['width'] // 2
        center_y = dz['y'] + dz['height'] // 2
        
        # Корпус корзины
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            (center_x - 25, center_y - 10, 50, 40),
            0
        )
        pygame.draw.rect(
            self.screen,
            COLOR_DARK_RED,
            (center_x - 25, center_y - 10, 50, 40),
            3
        )
        
        # Крышка корзины
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            (center_x - 30, center_y - 20, 60, 8),
            0
        )
        pygame.draw.rect(
            self.screen,
            COLOR_DARK_RED,
            (center_x - 30, center_y - 20, 60, 8),
            3
        )
        
        # Текст
        text = self.font_small.render("DELETE", True, COLOR_WHITE)
        text_rect = text.get_rect(center=(center_x, dz['y'] + dz['height'] - 15))
        self.screen.blit(text, text_rect)
    
    def draw_ui(self):
        """Отрисовывает UI элементы (счётчики, подсказки)."""
        padding = 10
        
        # Счётчик шариков на поле
        balls_text = self.font_medium.render(
            f"Шариков на поле: {len(self.game_logic.balls)}",
            True,
            COLOR_BLACK
        )
        self.screen.blit(balls_text, (padding, padding))
        
        # Счётчик шариков в инвентаре
        inventory_text = self.font_medium.render(
            f"В инвентаре: {len(self.game_logic.inventory)}",
            True,
            COLOR_BLACK
        )
        self.screen.blit(inventory_text, (padding, padding + 35))
        
        # Подсказки управления
        hints = [
            "ЛКМ - всосать шарик с поля",
            "ЛКМ на инвентарь - перетащить",
            "ПКМ - выплюнуть из инвентаря",
            "N - добавить шарик",
            "R - сброс",
            "C - очистить всё",
            "SPACE - пауза",
            "ESC - выход"
        ]
        
        y_offset = WINDOW_HEIGHT - 20 - len(hints) * 22
        for hint in hints:
            hint_text = self.font_small.render(hint, True, COLOR_GRAY)
            self.screen.blit(hint_text, (padding, y_offset))
            y_offset += 22
        
        # Индикатор паузы
        if self.paused:
            pause_text = self.font_large.render("ПАУЗА", True, COLOR_RED)
            pause_rect = pause_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            )
            
            # Фон для текста паузы
            background_rect = pause_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, COLOR_WHITE, background_rect)
            pygame.draw.rect(self.screen, COLOR_RED, background_rect, 3)
            
            self.screen.blit(pause_text, pause_rect)
    
    def draw_inventory(self):
        """Отрисовывает инвентарь в виде миниатюр шариков."""
        if len(self.game_logic.inventory) == 0:
            return
        
        # Позиция инвентаря (слева снизу, над подсказками)
        start_x = 20
        start_y = WINDOW_HEIGHT - 200
        spacing = 45
        mini_radius = 15
        
        # Заголовок
        title = self.font_medium.render("Инвентарь:", True, COLOR_BLACK)
        self.screen.blit(title, (start_x, start_y - 35))
        
        # Подсказка
        hint = self.font_small.render("(перетащи мышью)", True, COLOR_GRAY)
        self.screen.blit(hint, (start_x + 110, start_y - 30))
        
        # Рисуем миниатюры шариков
        for i, ball in enumerate(self.game_logic.inventory[:5]):  # Максимум 5 шариков
            x = start_x + 20
            y = start_y + i * spacing
            
            # Проверяем, наведён ли курсор на этот шарик
            distance = math.sqrt((self.mouse_x - x)**2 + (self.mouse_y - y)**2)
            is_hovered = distance <= mini_radius + 5
            
            # Фон (больше при наведении)
            bg_radius = mini_radius + 5 if is_hovered else mini_radius + 3
            bg_color = COLOR_GRAY if is_hovered else COLOR_LIGHT_GRAY
            pygame.draw.circle(
                self.screen,
                bg_color,
                (x, y),
                bg_radius
            )
            
            # Тень для объёма
            shadow_color = tuple(max(0, c - 100) for c in ball.color)
            pygame.draw.circle(
                self.screen,
                shadow_color,
                (x, y + 2),
                mini_radius - 2
            )
            
            # Шарик
            pygame.draw.circle(
                self.screen,
                ball.color,
                (x, y),
                mini_radius
            )
            
            # Блик
            highlight_color = tuple(min(255, c + 100) for c in ball.color)
            pygame.draw.circle(
                self.screen,
                highlight_color,
                (x - 5, y - 5),
                5
            )
            
            # Яркий блик
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (x - 4, y - 4),
                2
            )
            
            # Обводка
            outline_color = COLOR_BLACK if is_hovered else tuple(max(0, c - 50) for c in ball.color)
            outline_width = 3 if is_hovered else 2
            pygame.draw.circle(
                self.screen,
                outline_color,
                (x, y),
                mini_radius,
                outline_width
            )
            
            # Номер
            num_text = self.font_small.render(f"#{i+1}", True, COLOR_BLACK)
            self.screen.blit(num_text, (x + 25, y - 8))
            
            # Иконка руки при наведении
            if is_hovered:
                hand_text = self.font_small.render("👆", True, COLOR_BLACK)
                self.screen.blit(hand_text, (x + 25, y + 5))
        
        # Если шариков больше 5, показываем количество
        if len(self.game_logic.inventory) > 5:
            more_text = self.font_small.render(
                f"+{len(self.game_logic.inventory) - 5} ещё",
                True,
                COLOR_GRAY
            )
            self.screen.blit(more_text, (start_x + 20, start_y + 5 * spacing + 10))
    
    def run(self):
        """Основной игровой цикл."""
        while self.running:
            # Обработка событий
            self.handle_events()
            
            # Обновление
            self.update()
            
            # Отрисовка
            self.draw()
            
            # Контроль FPS
            self.clock.tick(FPS)
        
        # Завершение
        pygame.quit()
        sys.exit()


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

def main():
    """Запускает игру."""
    game = BallGame()
    game.run()


if __name__ == '__main__':
    main()

