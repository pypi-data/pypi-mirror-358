# reference: https://github.com/NilCoalescing/djangochannelsrestframework/blob/master/djangochannelsrestframework/scope_utils.py
import asyncio
from typing import Any, Callable, Dict

from channels.db import database_sync_to_async
from django.http import HttpRequest


def ensure_async(method: Callable):
    """
    Ensure method is async if not wrap it in database_sync_to_async.
    """
    if asyncio.iscoroutinefunction(method):
        return method
    return database_sync_to_async(method)


def request_from_scope(scope: Dict[str, Any]) -> HttpRequest:
    from django.contrib.auth.models import AnonymousUser

    request = HttpRequest()
    request.path = scope.get('path')
    request.session = scope.get('session')
    request.user = scope.get('user', AnonymousUser)

    request.META['HTTP_CONTENT_TYPE'] = 'application/json'
    request.META['HTTP_ACCEPT'] = 'application/json'

    for header_name, value in scope.get('headers', []):
        request.META[header_name.decode('utf-8')] = value.decode('utf-8')

    if scope.get('cookies'):
        request.COOKIES = scope.get('cookies')
    return request
