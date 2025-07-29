from django.apps import AppConfig


class pluginConfig(AppConfig):
    name = 'scst_proxy'
    label = 'scst_proxy'
    
    def ready(self):
        # Импортируем хуки при загрузке приложения
        from . import hooks  # noqa