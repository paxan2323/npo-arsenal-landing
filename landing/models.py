"""
Модели данных для лендинга "Птицелов"
"""
import os
from django.db import models
from django.core.validators import FileExtensionValidator


class DocumentCategory(models.Model):
    """Категории документов: Техническая документация, Сертификаты, Презентации"""
    name = models.CharField('Название категории', max_length=100)
    slug = models.SlugField('URL-идентификатор', unique=True)
    icon = models.CharField('CSS-класс иконки', max_length=50, default='file-text', 
                           help_text='Название иконки Lucide (например: file-text, award, presentation)')
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    
    class Meta:
        verbose_name = 'Категория документов'
        verbose_name_plural = 'Категории документов'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """Документы для скачивания"""
    category = models.ForeignKey(
        DocumentCategory, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name='Категория'
    )
    title = models.CharField('Название документа', max_length=200)
    description = models.TextField('Описание', blank=True)
    file = models.FileField(
        'Файл',
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx'])]
    )
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    download_count = models.PositiveIntegerField('Количество скачиваний', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    @property
    def file_size(self):
        """Возвращает размер файла в человекочитаемом формате"""
        if self.file and os.path.exists(self.file.path):
            size = self.file.size
            for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} ТБ"
        return "—"
    
    @property
    def file_extension(self):
        """Возвращает расширение файла"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().replace('.', '')
        return ''


class Feature(models.Model):
    """Преимущества/особенности системы"""
    title = models.CharField('Заголовок', max_length=100)
    description = models.TextField('Описание')
    icon = models.CharField('CSS-класс иконки', max_length=50, default='check-circle',
                           help_text='Название иконки Lucide')
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Преимущество'
        verbose_name_plural = 'Преимущества'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class SpecificationGroup(models.Model):
    """Группы ТТХ: Механика, Питание, Зрение и т.д."""
    name = models.CharField('Название группы', max_length=100)
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    
    class Meta:
        verbose_name = 'Группа характеристик'
        verbose_name_plural = 'Группы характеристик'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Specification(models.Model):
    """Тактико-технические характеристики"""
    group = models.ForeignKey(
        SpecificationGroup,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name='Группа'
    )
    name = models.CharField('Параметр', max_length=150)
    value = models.CharField('Значение', max_length=100)
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    
    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики (ТТХ)'
        ordering = ['group__order', 'order']
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class GalleryImage(models.Model):
    """Изображения галереи"""
    title = models.CharField('Название', max_length=100)
    image = models.ImageField('Изображение', upload_to='gallery/')
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Изображение галереи'
        verbose_name_plural = 'Галерея'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class ContactRequest(models.Model):
    """Заявки с формы обратной связи"""
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=30, blank=True)
    company = models.CharField('Организация', max_length=200, blank=True)
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_processed = models.BooleanField('Обработано', default=False)
    notes = models.TextField('Заметки менеджера', blank=True)
    
    # Поля для согласия на обработку ПДН (152-ФЗ)
    consent_given = models.BooleanField('Согласие на обработку ПДН', default=False)
    consent_date = models.DateTimeField('Дата согласия', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True, help_text='Браузер пользователя')
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки с сайта'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} — {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class SiteSettings(models.Model):
    """Настройки сайта (синглтон)"""
    site_title = models.CharField('Заголовок сайта', max_length=200, default='Арсенал')
    site_description = models.TextField('Описание для SEO', 
        default='Роботизированная турель контрдроновой защиты')
    hero_title = models.CharField('Заголовок Hero', max_length=200, default='АРСЕНАЛ')
    hero_subtitle = models.TextField('Подзаголовок Hero',
        default='Роботизированная турель ближней контрдроновой защиты')
    about_text = models.TextField('Текст "О системе"', blank=True)
    turret_image = models.ImageField('Изображение турели', upload_to='turret/', blank=True, null=True,
        help_text='Загрузите фотографию турели для отображения в секции "О системе"')
    contact_email = models.EmailField('Email для связи', default='npo.arsenal.info@mail.ru')
    contact_phone = models.CharField('Телефон', max_length=30, default='8-960-283-15-14')
    contact_address = models.TextField('Адрес', 
        default='Санкт-Петербург, п. Стрельна, ул. Фронтовая д.3')
    
    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'
    
    def __str__(self):
        return 'Настройки сайта'
    
    def save(self, *args, **kwargs):
        # Обеспечиваем синглтон — только одна запись
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Получить настройки или создать дефолтные"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# ==================== ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ====================

class SoftwarePlatform(models.Model):
    """Описание платформы и архитектуры ПО (синглтон)"""
    intro_text = models.TextField('Вводный текст', 
        default='Программное обеспечение обеспечивает автоматическое сопровождение воздушных целей и наведение двухосевой турели.')
    platform_name = models.CharField('Платформа', max_length=100, default='Android 12 AOSP')
    hardware = models.CharField('Бортовой вычислитель', max_length=200, 
        default='8-ядерный CPU, GPU Adreno')
    app_type = models.CharField('Тип приложения', max_length=100, default='Монолитное Android-приложение (APK)')
    languages = models.CharField('Языки разработки', max_length=200, default='Scala, Java, C++ (NDK)')
    
    class Meta:
        verbose_name = 'Платформа ПО'
        verbose_name_plural = 'Платформа ПО'
    
    def __str__(self):
        return 'Настройки платформы ПО'
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_platform(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SoftwareModule(models.Model):
    """Функциональные модули ПО"""
    ICON_CHOICES = [
        ('cpu', 'Процессор'),
        ('eye', 'Зрение/Трекинг'),
        ('crosshair', 'Наведение'),
        ('video', 'Видео/Стриминг'),
        ('settings', 'Настройки'),
        ('chip', 'Контроллер'),
        ('wifi', 'Связь'),
        ('terminal', 'Терминал'),
    ]
    
    title = models.CharField('Название модуля', max_length=100)
    icon = models.CharField('Иконка', max_length=50, choices=ICON_CHOICES, default='cpu')
    description = models.TextField('Описание')
    tech_details = models.TextField('Технические детали', blank=True,
        help_text='Например: "~20 fps при 4K-потоке"')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Модуль ПО'
        verbose_name_plural = 'Модули ПО'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class HardwareInterface(models.Model):
    """Аппаратное взаимодействие"""
    name = models.CharField('Название', max_length=100)
    value = models.CharField('Значение/Характеристика', max_length=200)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Аппаратный интерфейс'
        verbose_name_plural = 'Аппаратные интерфейсы'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class DevelopmentPlan(models.Model):
    """Планы развития ПО"""
    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('in_progress', 'В разработке'),
        ('completed', 'Реализовано'),
    ]
    
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='planned')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'План развития'
        verbose_name_plural = 'Планы развития'
        ordering = ['order']
    
    def __str__(self):
        return self.title

