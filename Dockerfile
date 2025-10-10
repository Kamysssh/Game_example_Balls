# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости для pygame и X11
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    python3-setuptools \
    python3-dev \
    python3-numpy \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы игры
COPY game.py logic.py gui.py ./

# Устанавливаем переменные окружения для X11
ENV DISPLAY=:0
ENV SDL_VIDEODRIVER=x11

# Делаем gui.py исполняемым
RUN chmod +x gui.py

# Запускаем игру
CMD ["python", "gui.py"]

