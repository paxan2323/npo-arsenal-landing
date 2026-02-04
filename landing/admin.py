"""
Django Admin конфигурация для лендинга "Птицелов"
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DocumentCategory, Document, Feature, 
    SpecificationGroup, Specification, 
    GalleryImage, ContactRequest, SiteSettings,
    SoftwarePlatform, SoftwareModule, HardwareInterface, DevelopmentPlan
)


# Кастомизация заголовков админки
admin.site.site_header = 'НПО Арсенал — Управление сайтом'
admin.site.site_title = 'Арсенал Admin'
admin.site.index_title = 'Панель управления'


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'documents_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']
    
    def documents_count(self, obj):
        return obj.documents.count()
    documents_count.short_description = 'Документов'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'file_size_display', 'download_count', 'uploaded_at', 'is_active']
    list_filter = ['category', 'is_active', 'uploaded_at']
    list_editable = ['is_active']
    search_fields = ['title', 'description']
    readonly_fields = ['download_count', 'uploaded_at', 'file_size_display']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Основное', {
            'fields': ('category', 'title', 'description', 'file')
        }),
        ('Статистика', {
            'fields': ('download_count', 'uploaded_at', 'file_size_display'),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
    )
    
    def file_size_display(self, obj):
        return obj.file_size
    file_size_display.short_description = 'Размер файла'


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order']


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
    ordering = ['order']


@admin.register(SpecificationGroup)
class SpecificationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'specs_count']
    list_editable = ['order']
    inlines = [SpecificationInline]
    ordering = ['order']
    
    def specs_count(self, obj):
        return obj.specifications.count()
    specs_count.short_description = 'Характеристик'


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'group', 'order']
    list_filter = ['group']
    list_editable = ['value', 'order']
    ordering = ['group__order', 'order']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px; object-fit: cover;"/>',
                obj.image.url
            )
        return "—"
    image_preview.short_description = 'Превью'


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'company', 'created_at', 'is_processed']
    list_filter = ['is_processed', 'created_at']
    list_editable = ['is_processed']
    search_fields = ['name', 'email', 'phone', 'company', 'message']
    readonly_fields = ['name', 'email', 'phone', 'company', 'message', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Контактные данные', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Сообщение', {
            'fields': ('message', 'created_at')
        }),
        ('Обработка', {
            'fields': ('is_processed', 'notes')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Заявки создаются только через форму на сайте


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('SEO', {
            'fields': ('site_title', 'site_description')
        }),
        ('Главный экран (Hero)', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('О системе', {
            'fields': ('about_text',)
        }),
        ('Контактная информация', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
    )
    
    def has_add_permission(self, request):
        # Разрешаем добавление только если нет записей
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False  # Запрещаем удаление настроек


# ============================================
# Раздел "Программное обеспечение"
# ============================================

@admin.register(SoftwarePlatform)
class SoftwarePlatformAdmin(admin.ModelAdmin):
    """Админка для настроек платформы ПО (singleton)"""
    fieldsets = (
        ('Вводный текст', {
            'fields': ('intro_text',)
        }),
        ('Архитектура платформы', {
            'fields': ('platform_name', 'hardware', 'app_type', 'languages')
        }),
    )
    
    def has_add_permission(self, request):
        return not SoftwarePlatform.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SoftwareModule)
class SoftwareModuleAdmin(admin.ModelAdmin):
    """Админка для функциональных модулей ПО"""
    list_display = ['title', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'icon']
    search_fields = ['title', 'description']
    ordering = ['order']
    
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'icon', 'description')
        }),
        ('Технические детали', {
            'fields': ('tech_details',),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(HardwareInterface)
class HardwareInterfaceAdmin(admin.ModelAdmin):
    """Админка для аппаратных интерфейсов"""
    list_display = ['name', 'value', 'order', 'is_active']
    list_editable = ['value', 'order', 'is_active']
    ordering = ['order']


@admin.register(DevelopmentPlan)
class DevelopmentPlanAdmin(admin.ModelAdmin):
    """Админка для планов развития"""
    list_display = ['title', 'status', 'order', 'is_active']
    list_editable = ['status', 'order', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order']
    
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'description', 'status')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
