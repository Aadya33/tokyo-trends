from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from products.views import (
    home,
    men,
    women,
    cosmetics,
    faq,
    login,
    logout,
    product_detail,
    cart,
    shipping,
    create_order,
    track_order,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),

    path("men/", men, name="men"),

    path("women/", women, name="women"),

    path("cosmetics/", cosmetics, name="cosmetics"),

    path("faq/", faq, name="faq"),

    path(
        "product/<int:product_id>/",
        product_detail,
        name="product_detail",
    ),

    path("login/", login, name="login"),

    path("logout/", logout, name="logout"),

    path("cart/", cart, name="cart"),

    path("shipping/", shipping, name="shipping"),

    path(
        "create-order/",
        create_order,
        name="create_order",
    ),

    path(
        "track-order/",
        track_order,
        name="track_order",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )