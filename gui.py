#!/usr/bin/env python3
"""
Точка входа для игры про шарики.
Запускает графический интерфейс игры.
"""

from game import main

if __name__ == '__main__':
    print("Запуск игры про шарики...")
    print("Управление:")
    print("  ЛКМ - всосать шарик")
    print("  ПКМ - выплюнуть шарик")
    print("  SPACE - пауза")
    print("  ESC - выход")
    print("")
    main()
