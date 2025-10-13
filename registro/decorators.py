import logging
from functools import wraps
from django.shortcuts import redirect, render

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_device_id(request):

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


def relatorio_auth_required(view_func):
    """
    Decorator que verifica autenticação de usuários de relatório.

    Uso:
        @relatorio_auth_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('relatorio_user_id')

        if not user_id:
            return redirect('login_relatorio_view')

        from .models import UserRelatorio

        try:
            user = UserRelatorio.objects.get(id=user_id, ativo=True)
            request.relatorio_user = user
            return view_func(request, *args, **kwargs)
        except UserRelatorio.DoesNotExist:
            request.session.flush()
            return redirect('login_relatorio_view')

    return _wrapped_view


def relatorio_edit_blocked(view_func):
    """
    Decorator que bloqueia acesso se o usuário tiver edit=True.
    Deve ser usado após @relatorio_auth_required.

    Uso:
        @relatorio_auth_required
        @relatorio_edit_blocked
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request, 'relatorio_user') and request.relatorio_user.edit:
            return render(request, 'erro_permissao.html', {
                'mensagem': 'Você não tem permissão para acessar esta página.'
            })
        return view_func(request, *args, **kwargs)

    return _wrapped_view