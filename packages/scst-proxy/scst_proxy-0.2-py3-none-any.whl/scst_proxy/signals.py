# permission_tracker/signals.py

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from scst_proxy.models import PluginSettings
from scst_proxy.tasks import send_permission_removed_notification_task,send_permission_added_notification_task
import logging
import requests
import os

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.user_permissions.through)
def user_permissions_changed(sender, instance, action, pk_set, **kwargs):
    """
    Обработчик сигнала m2m_changed для отслеживания добавления и удаления разрешений пользователя.
    """
    if action == "post_add":
        # Разрешения добавлены пользователю
        for perm_id in pk_set:
            try:
                permission = Permission.objects.get(pk=perm_id)
                send_permission_change_notification(instance, permission, 'added')
                logger.info(f"Permission '{permission.codename}' added to user '{instance.username}'.")
            except Permission.DoesNotExist:
                logger.error(f"Permission with id {perm_id} does not exist.")
    elif action == "post_remove":
        # Разрешения удалены у пользователя
        for perm_id in pk_set:
            try:
                permission = Permission.objects.get(pk=perm_id)
                send_permission_change_notification(instance, permission, 'removed')
                logger.info(f"Permission '{permission.codename}' removed from user '{instance.username}'.")
            except Permission.DoesNotExist:
                logger.error(f"Permission with id {perm_id} does not exist.")

def send_permission_change_notification(user, permission, action):
    data = {
            'user': user, 
            'permission': permission
            }
    if action == "removed":
        send_permission_removed_notification_task.delay(data)