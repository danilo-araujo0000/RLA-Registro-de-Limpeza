import logging
from functools import wraps
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Obtem o IP real do cliente, considerando proxies.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_device_id(request):
    """
    Obtem o identificador do dispositivo enviado pelo aplicativo.
    """
    device_id = request.headers.get('X-Device-Id')
    if not device_id:
        device_id = request.META.get('HTTP_X_DEVICE_ID')
    if device_id:
        return device_id.strip()

    device_id = request.COOKIES.get('device_id')
    if device_id:
        return device_id.strip()

    return None


def ip_whitelist_required():
    """
    Decorator que verifica se o acesso esta autorizado por IP ou ID do dispositivo.

    Uso:
        @ip_whitelist_required()
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from .models import IPPermitido, DispositivoPermitido

            client_ip = get_client_ip(request)
            device_id = get_client_device_id(request)

            logger.info(
                f'Acesso recebido - IP: {client_ip} - Device ID: {device_id or "N/A"} - '
                f'URL: {request.path} - Metodo: {request.method}'
            )

            ip_permitido = IPPermitido.objects.filter(
                ip_address=client_ip,
                ativo=True
            ).exists()

            if ip_permitido:
                logger.info(f'Acesso PERMITIDO - IP: {client_ip} - URL: {request.path}')
                return view_func(request, *args, **kwargs)

            if device_id:
                device_permitido = DispositivoPermitido.objects.filter(
                    identificador=device_id,
                    ativo=True
                ).exists()

                if device_permitido:
                    logger.info(f'Acesso PERMITIDO - Device ID: {device_id} - URL: {request.path}')
                    return view_func(request, *args, **kwargs)

                logger.warning(
                    f'Acesso NEGADO - Device ID: {device_id} nao autorizado - IP: {client_ip} - URL: {request.path}'
                )
                return redirect('https://amevotuporanga.com.br/')

            logger.warning(
                f'Acesso NEGADO - IP: {client_ip} nao autorizado - Device ID: {device_id or "N/A"} - '
                f'URL: {request.path}'
            )
            return redirect('https://amevotuporanga.com.br/')

        return _wrapped_view

    return decorator
