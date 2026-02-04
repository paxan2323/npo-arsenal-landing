"""
Management команда для инициализации данных раздела ПО
"""
from django.core.management.base import BaseCommand
from landing.models import (
    SoftwarePlatform, SoftwareModule, 
    HardwareInterface, DevelopmentPlan
)


class Command(BaseCommand):
    help = 'Инициализация данных раздела "Программное обеспечение"'

    def handle(self, *args, **options):
        self.stdout.write('Создание данных для раздела ПО...')
        
        # 1. Платформа (singleton)
        platform, created = SoftwarePlatform.objects.get_or_create(
            pk=1,
            defaults={
                'intro_text': (
                    'Комплекс управляется собственным программным обеспечением, '
                    'разработанным специально для задач автономного обнаружения и '
                    'сопровождения малоразмерных БПЛА в реальном времени.'
                ),
                'platform_name': 'Raspberry Pi 4B / Linux',
                'hardware': 'ARM Cortex-A72, 4 ГБ RAM',
                'app_type': 'PyQt6 GUI + фоновые сервисы',
                'languages': 'Python 3.11, C++ (OpenCV)',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Создана платформа ПО'))
        else:
            self.stdout.write('  Платформа ПО уже существует')
        
        # 2. Функциональные модули
        modules_data = [
            {
                'title': 'Детекция объектов',
                'icon': 'eye',
                'description': (
                    'Нейросетевой детектор на базе YOLOv8 для обнаружения '
                    'БПЛА в видеопотоке с минимальной задержкой.'
                ),
                'tech_details': 'YOLOv8n, ONNX Runtime, 30+ FPS',
                'order': 1,
            },
            {
                'title': 'Трекинг целей',
                'icon': 'crosshair',
                'description': (
                    'Алгоритм сопровождения на основе фильтра Калмана с '
                    'предсказанием траектории движения цели.'
                ),
                'tech_details': 'Kalman Filter, DeepSORT',
                'order': 2,
            },
            {
                'title': 'Управление приводами',
                'icon': 'settings',
                'description': (
                    'PID-регулятор для плавного наведения турели по '
                    'двум осям с компенсацией инерции.'
                ),
                'tech_details': 'PID Control, UART 115200',
                'order': 3,
            },
            {
                'title': 'Видеозахват',
                'icon': 'video',
                'description': (
                    'Параллельный захват с нескольких камер с '
                    'синхронизацией кадров и буферизацией.'
                ),
                'tech_details': 'OpenCV, GStreamer, V4L2',
                'order': 4,
            },
            {
                'title': 'Интерфейс оператора',
                'icon': 'terminal',
                'description': (
                    'Графический интерфейс с отображением видео, '
                    'телеметрии и элементами управления.'
                ),
                'tech_details': 'PyQt6, QML',
                'order': 5,
            },
        ]
        
        for data in modules_data:
            module, created = SoftwareModule.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Модуль: {data["title"]}'))
        
        # 3. Аппаратные интерфейсы
        interfaces_data = [
            {'name': 'Горизонт (Pan)', 'value': 'Stepper NEMA23, UART', 'order': 1},
            {'name': 'Вертикаль (Tilt)', 'value': 'Stepper NEMA17, UART', 'order': 2},
            {'name': 'Камера 1', 'value': 'USB3.0, 1920×1080 @ 30fps', 'order': 3},
            {'name': 'Камера 2', 'value': 'CSI-2, 1640×1232 @ 40fps', 'order': 4},
            {'name': 'Термодатчик', 'value': 'I2C, MLX90614', 'order': 5},
            {'name': 'Питание', 'value': '48V DC → 5V/12V stepdown', 'order': 6},
        ]
        
        for data in interfaces_data:
            iface, created = HardwareInterface.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Интерфейс: {data["name"]}'))
        
        # 4. Планы развития
        plans_data = [
            {
                'title': 'Базовая детекция и трекинг',
                'description': 'Реализован детектор YOLOv8 и алгоритм сопровождения.',
                'status': 'completed',
                'order': 1,
            },
            {
                'title': 'Интеграция с приводами',
                'description': 'Управление шаговыми двигателями через UART.',
                'status': 'completed',
                'order': 2,
            },
            {
                'title': 'Многокамерный режим',
                'description': 'Одновременный захват и обработка нескольких источников.',
                'status': 'in_progress',
                'order': 3,
            },
            {
                'title': 'Автономное патрулирование',
                'description': 'Сканирование сектора при отсутствии целей.',
                'status': 'planned',
                'order': 4,
            },
            {
                'title': 'Интеграция с РЭБ',
                'description': 'Протокол взаимодействия с системами подавления.',
                'status': 'planned',
                'order': 5,
            },
        ]
        
        for data in plans_data:
            plan, created = DevelopmentPlan.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ План: {data["title"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Раздел ПО успешно инициализирован!'))
