from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from products.views import (
    home,
    men,
    women,
    cosmetics,
    login,
    logout,
    product_detail
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),
    path("men/", men, name="men"),
    path("women/", women, name="women"),
    path("cosmetics/", cosmetics, name="cosmetics"),

    path(
        "product/<int:product_id>/",
        product_detail,
        name="product_detail",
    ),

    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )