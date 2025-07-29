from django.db import models

class PluginSettings(models.Model):
    """Модель для хранения настроек плагина"""
    api_endpoint = models.URLField(
        max_length=255,
        default="http://proxyreg.ekzoman.ru/",
        verbose_name="API Endpoint"
    )
    api_key = models.CharField(
        max_length=255,
        default="YOUR_API_KEY",
        verbose_name="API ключ"
    )

    class Meta:
        verbose_name = "Настройки плагина"
        verbose_name_plural = "Настройки плагина"

    def __str__(self):
        return "ProxyReg"
    
    @classmethod
    def get_settings(cls):
        """Получает или создает настройки по умолчанию"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj