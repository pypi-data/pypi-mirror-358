from django.apps import AppConfig


class ScStProxySettings(AppConfig):
    name = 'scst_proxy'
    label = 'scst_proxy'
    default_pesmissions = ('scst_proxy.can_use_proxy')
    

    def ready(self):
        # Импортируем хуки при загрузке приложения
        from . import hooks  # noqa
        import scst_proxy.signals