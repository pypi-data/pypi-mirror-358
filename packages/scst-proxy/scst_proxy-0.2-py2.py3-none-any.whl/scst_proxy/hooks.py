from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook
from django.utils.translation import gettext_lazy as _
from . import urls

class ProxyRegMenuItem(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(
            self,
            'Прокси-сервер альянса',  # Текст в меню
            'fas fa-server',  # Иконка Font Awesome (например, fa-rocket)
            'scst_proxy:main',  # Имя URL из urls.py
            navactive=['scst_proxy:'],  # Подсветка меню при активности
        )


@hooks.register('menu_item_hook')  # Регистрация хука
def register_menu():
  return ProxyRegMenuItem()

@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "scst_proxy", r"^scst_proxy/")

# class SettingsMenuItem(MenuItemHook):
#     def __init__(self):
#         super().__init__(
#             'Настройки плагина',
#             'fas fa-cog',
#             'scst_proxy:settings',
#             navactive=['scst_proxy:settings'],
#         )

# @hooks.register('menu_item_hook')
# def register_menu():
#     return SettingsMenuItem()