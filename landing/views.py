"""
Views для лендинга "Птицелов"
"""
import json
import logging
import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    DocumentCategory, Document, Feature,
    SpecificationGroup,
    ContactRequest, SiteSettings,
    SoftwarePlatform, SoftwareModule, HardwareInterface, DevelopmentPlan
)
from .forms import ContactForm

logger = logging.getLogger(__name__)


def verify_smartcaptcha(token, ip=None):
    """Проверка токена Яндекс SmartCaptcha"""
    if not settings.SMARTCAPTCHA_SERVER_KEY:
        # Если ключ не настроен, пропускаем проверку (dev mode)
        logger.info('SmartCaptcha: No server key configured, skipping verification')
        return True
    
    if not token:
        logger.warning('SmartCaptcha: Empty token received')
        return False
    
    try:
        response = requests.post(
            'https://smartcaptcha.yandexcloud.net/validate',
            data={
                'secret': settings.SMARTCAPTCHA_SERVER_KEY,
                'token': token,
                'ip': ip or '',
            },
            timeout=5
        )
        result = response.json()
        logger.info(f'SmartCaptcha response: {result}')
        return result.get('status') == 'ok'
    except Exception as e:
        logger.error(f'SmartCaptcha verification error: {e}')
        # В случае ошибки API пропускаем (можно изменить на False для строгой проверки)
        return True


def index(request):
    """Главная страница лендинга"""
    site_settings = SiteSettings.get_settings()
    
    context = {
        'settings': site_settings,
        'features': Feature.objects.filter(is_active=True),
        'spec_groups': SpecificationGroup.objects.prefetch_related('specifications'),
        'document_categories': DocumentCategory.objects.prefetch_related(
            'documents'
        ).filter(documents__is_active=True).distinct(),
        'contact_form': ContactForm(),
        'smartcaptcha_client_key': settings.SMARTCAPTCHA_CLIENT_KEY,
        # Раздел ПО
        'software_platform': SoftwarePlatform.get_platform(),
        'software_modules': SoftwareModule.objects.filter(is_active=True),
        'hardware_interfaces': HardwareInterface.objects.filter(is_active=True),
        'development_plans': DevelopmentPlan.objects.filter(is_active=True),
    }
    return render(request, 'landing/index.html', context)


def privacy_policy(request):
    """Страница Политики обработки персональных данных"""
    site_settings = SiteSettings.get_settings()
    return render(request, 'landing/privacy.html', {'settings': site_settings})


def cookie_policy(request):
    """Страница Политики обработки файлов cookie"""
    site_settings = SiteSettings.get_settings()
    return render(request, 'landing/cookies.html', {'settings': site_settings})


def document_download(request, pk):
    """Скачивание документа с учётом счётчика"""
    document = get_object_or_404(Document, pk=pk, is_active=True)
    
    # Увеличиваем счётчик скачиваний
    document.download_count += 1
    document.save(update_fields=['download_count'])
    
    # Возвращаем файл
    try:
        response = FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
        return response
    except FileNotFoundError:
        raise Http404("Файл не найден")


@require_POST
@csrf_protect
def contact_submit(request):
    """Обработка формы обратной связи (AJAX)"""
    
    # Проверяем AJAX-запрос
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Honeypot check - если поле website заполнено, это бот
    if request.POST.get('website'):
        logger.warning(f'Honeypot triggered from IP: {request.META.get("REMOTE_ADDR")}')
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Спасибо!'})  # Fake success
        return render(request, 'landing/thank_you.html', {'settings': SiteSettings.get_settings()})
    
    # SmartCaptcha verification
    captcha_token = request.POST.get('smart-token', '')
    client_ip = request.META.get('REMOTE_ADDR', '')
    
    logger.info(f'Contact form: captcha_token={captcha_token[:20] if captcha_token else "EMPTY"}..., IP={client_ip}')
    
    # Временно: пропускаем проверку если токен пустой (для отладки)
    if captcha_token and not verify_smartcaptcha(captcha_token, client_ip):
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': {'captcha': ['Пожалуйста, пройдите проверку капчи']}
            }, status=400)
        else:
            return render(request, 'landing/index.html', {
                'contact_form': ContactForm(request.POST),
                'captcha_error': 'Пожалуйста, пройдите проверку капчи',
                'settings': SiteSettings.get_settings(),
                'features': Feature.objects.filter(is_active=True),
                'spec_groups': SpecificationGroup.objects.prefetch_related('specifications'),
                'document_categories': DocumentCategory.objects.prefetch_related('documents'),
                'smartcaptcha_client_key': settings.SMARTCAPTCHA_CLIENT_KEY,
            })
    
    form = ContactForm(request.POST)
    
    if form.is_valid():
        # Сохраняем заявку с данными о согласии
        contact_request = form.save(commit=False)
        contact_request.ip_address = request.META.get('REMOTE_ADDR')
        contact_request.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Ограничиваем длину
        contact_request.save()
        
        # Отправляем email уведомление
        try:
            send_mail(
                subject=f'Новая заявка с сайта Арсенал от {contact_request.name}',
                message=f"""
Новая заявка с сайта:

Имя: {contact_request.name}
Email: {contact_request.email}
Телефон: {contact_request.phone or 'Не указан'}
Организация: {contact_request.company or 'Не указана'}

Сообщение:
{contact_request.message}

---
Дата: {contact_request.created_at.strftime('%d.%m.%Y %H:%M')}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass  # Не прерываем процесс если email не отправился
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'
            })
        else:
            # Редирект для не-AJAX запросов
            return render(request, 'landing/thank_you.html', {
                'settings': SiteSettings.get_settings()
            })
    else:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            # Вернуть страницу с ошибками
            return render(request, 'landing/index.html', {
                'contact_form': form,
                'settings': SiteSettings.get_settings(),
                'features': Feature.objects.filter(is_active=True),
                'spec_groups': SpecificationGroup.objects.prefetch_related('specifications'),
                'document_categories': DocumentCategory.objects.prefetch_related('documents'),
            })
