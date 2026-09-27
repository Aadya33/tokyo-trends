import json
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import (
    Product,
    Client,
    Order,
    OrderItem,
)


# =========================================================
# HOME
# =========================================================

def home(request):
    products = (
        Product.objects
        .prefetch_related("images")
        .order_by("-created_at")[:8]
    )

    return render(
        request,
        "home.html",
        {
            "products": products,
        },
    )


# =========================================================
# MEN
# =========================================================

def men(request):
    products = (
        Product.objects
        .filter(category="men")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    return render(
        request,
        "men.html",
        {
            "products": products,
        },
    )


# =========================================================
# WOMEN
# =========================================================

def women(request):
    products = (
        Product.objects
        .filter(category="women")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    return render(
        request,
        "women.html",
        {
            "products": products,
        },
    )


# =========================================================
# COSMETICS
# =========================================================

def cosmetics(request):
    products = (
        Product.objects
        .filter(category="cosmetics")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    return render(
        request,
        "cosmetics.html",
        {
            "products": products,
        },
    )


# =========================================================
# FAQ
# =========================================================

def faq(request):
    return render(
        request,
        "faq.html",
    )


# =========================================================
# LOGIN
# =========================================================

def login(request):

    if request.method == "POST":

        mobile = request.POST.get(
            "mobile",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        # Check empty fields
        if not mobile or not email:
            return render(
                request,
                "login.html",
                {
                    "error": (
                        "Please enter your mobile number "
                        "and email address."
                    ),
                },
            )

        # Check existing mobile
        try:

            client = Client.objects.get(
                mobile=mobile
            )

            # Mobile exists but email does not match
            if client.email != email:
                return render(
                    request,
                    "login.html",
                    {
                        "error": (
                            "This mobile number is already "
                            "registered with another email address."
                        ),
                    },
                )

        except Client.DoesNotExist:

            # Email already belongs to another client
            if Client.objects.filter(
                email=email
            ).exists():

                return render(
                    request,
                    "login.html",
                    {
                        "error": (
                            "This email address is already "
                            "registered with another mobile number."
                        ),
                    },
                )

            # Create new client
            client = Client.objects.create(
                mobile=mobile,
                email=email,
            )

        # Save client in session
        request.session["client_id"] = client.id

        return redirect("/")

    return render(
        request,
        "login.html",
    )


# =========================================================
# LOGOUT
# =========================================================

def logout(request):

    request.session.flush()

    return redirect("/")


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product.objects.prefetch_related(
            "images",
            "sizes",
            "reviews",
            "reviews__client",
        ),
        id=product_id,
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
        },
    )


# =========================================================
# CART
# =========================================================

def cart(request):

    return render(
        request,
        "cart.html",
    )


# =========================================================
# SHIPPING / CHECKOUT
# =========================================================

def shipping(request):

    return render(
        request,
        "shipping.html",
    )


# =========================================================
# TRACK ORDER
# =========================================================

def track_order(request):

    order = None
    searched = False
    error = ""

    order_number = request.GET.get(
        "order",
        "",
    ).strip().upper()

    mobile = request.GET.get(
        "mobile",
        "",
    ).strip()

    # Search requested
    if order_number or mobile:

        searched = True

        # Both fields are required
        if not order_number or not mobile:

            error = (
                "Please enter both your Order ID "
                "and mobile number."
            )

        else:

            order = (
                Order.objects
                .prefetch_related("items")
                .filter(
                    order_number=order_number,
                    mobile=mobile,
                )
                .first()
            )

            if order is None:

                error = (
                    "We could not find an order with "
                    "that Order ID and mobile number."
                )

    return render(
        request,
        "track_order.html",
        {
            "order": order,
            "searched": searched,
            "error": error,
            "order_number": order_number,
            "mobile": mobile,
        },
    )


# =========================================================
# CREATE ORDER
# =========================================================

@require_POST
def create_order(request):

    # -----------------------------------------------------
    # Read JSON
    # -----------------------------------------------------

    try:

        data = json.loads(
            request.body.decode("utf-8")
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid order data.",
            },
            status=400,
        )

    # -----------------------------------------------------
    # Get shipping and cart data
    # -----------------------------------------------------

    shipping_data = data.get(
        "shipping",
        {},
    )

    cart = data.get(
        "cart",
        [],
    )

    # -----------------------------------------------------
    # Empty cart check
    # -----------------------------------------------------

    if not cart:

        return JsonResponse(
            {
                "success": False,
                "message": "Your cart is empty.",
            },
            status=400,
        )

    # -----------------------------------------------------
    # Required shipping fields
    # -----------------------------------------------------

    required_fields = [
        "fullName",
        "mobile",
        "email",
        "address",
        "area",
        "city",
        "state",
        "pincode",
        "country",
    ]

    for field in required_fields:

        if not str(
            shipping_data.get(
                field,
                "",
            )
        ).strip():

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Please complete all "
                        "shipping details."
                    ),
                },
                status=400,
            )

    # -----------------------------------------------------
    # Mobile validation
    # -----------------------------------------------------

    mobile = str(
        shipping_data["mobile"]
    ).strip()

    if not mobile.isdigit() or len(mobile) != 10:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please enter a valid "
                    "10 digit mobile number."
                ),
            },
            status=400,
        )

    # -----------------------------------------------------
    # PIN code validation
    # -----------------------------------------------------

    pincode = str(
        shipping_data["pincode"]
    ).strip()

    if not pincode.isdigit() or len(pincode) != 6:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please enter a valid "
                    "6 digit PIN code."
                ),
            },
            status=400,
        )

    # -----------------------------------------------------
    # Payment method validation
    # -----------------------------------------------------

    payment_method = str(
        data.get(
            "payment_method",
            "",
        )
    ).strip().lower()

    allowed_payment_methods = {
        "upi",
        "card",
        "netbanking",
    }

    if payment_method not in allowed_payment_methods:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please select a valid "
                    "online payment method."
                ),
            },
            status=400,
        )

    # -----------------------------------------------------
    # Calculate order subtotal on server
    # -----------------------------------------------------

    server_subtotal = Decimal("0")

    clean_items = []

    for item in cart:

        try:

            quantity = int(
                item.get(
                    "quantity",
                    1,
                )
            )

            price = Decimal(
                str(
                    item.get(
                        "price",
                        "0",
                    )
                )
            )

        except (
            ValueError,
            TypeError,
            InvalidOperation,
        ):

            continue

        # Ignore invalid quantities/prices
        if quantity <= 0 or price < 0:
            continue

        # -------------------------------------------------
        # Find actual product from database
        # -------------------------------------------------

        product_id = item.get(
            "productId",
            item.get("id"),
        )

        product = None

        if product_id:

            try:

                product = Product.objects.get(
                    id=int(product_id)
                )

            except (
                Product.DoesNotExist,
                ValueError,
                TypeError,
            ):

                product = None

        # -------------------------------------------------
        # Use database price if product exists
        # -------------------------------------------------

        if product:

            actual_price = Decimal(
                str(
                    product.current_price()
                )
            )

            product_name = product.name

        else:

            actual_price = price

            product_name = str(
                item.get(
                    "name",
                    "Tokyo Trends Product",
                )
            )

        # -------------------------------------------------
        # Add to subtotal
        # -------------------------------------------------

        server_subtotal += (
            actual_price * quantity
        )

        # -------------------------------------------------
        # Store cleaned item
        # -------------------------------------------------

        clean_items.append(
            {
                "product": product,
                "product_name": product_name,
                "size": str(
                    item.get(
                        "size",
                        "",
                    )
                ),
                "price": actual_price,
                "quantity": quantity,
                "image_url": str(
                    item.get(
                        "image",
                        "",
                    )
                ),
            }
        )

    # -----------------------------------------------------
    # No valid products
    # -----------------------------------------------------

    if not clean_items:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "No valid products were found "
                    "in your cart."
                ),
            },
            status=400,
        )

    # -----------------------------------------------------
    # Shipping calculation
    #
    # ₹2,000 or more = FREE
    # Below ₹2,000 = ₹99
    # -----------------------------------------------------

    if server_subtotal >= Decimal("2000"):

        server_shipping = Decimal("0")

    else:

        server_shipping = Decimal("99")

    # -----------------------------------------------------
    # Coupon
    #
    # TOKYO100
    # ₹1,000 off
    # Minimum subtotal ₹8,000
    # -----------------------------------------------------

    coupon_code = str(
        data.get(
            "coupon_code",
            "",
        )
    ).strip().upper()

    if (
        coupon_code == "TOKYO100"
        and server_subtotal >= Decimal("8000")
    ):

        server_discount = Decimal("1000")

    else:

        server_discount = Decimal("0")

    # -----------------------------------------------------
    # Final total
    # -----------------------------------------------------

    server_total = (
        server_subtotal
        + server_shipping
        - server_discount
    )

    # -----------------------------------------------------
    # Create order
    # -----------------------------------------------------

    order = Order.objects.create(

        full_name=str(
            shipping_data["fullName"]
        ).strip(),

        mobile=mobile,

        email=str(
            shipping_data["email"]
        ).strip().lower(),

        address=str(
            shipping_data["address"]
        ).strip(),

        area=str(
            shipping_data["area"]
        ).strip(),

        city=str(
            shipping_data["city"]
        ).strip(),

        state=str(
            shipping_data["state"]
        ).strip(),

        pincode=pincode,

        country=str(
            shipping_data["country"]
        ).strip() or "India",

        payment_method=payment_method,

        payment_status="pending",

        status="placed",

        coupon_code=(
            "TOKYO100"
            if server_discount > 0
            else ""
        ),

        subtotal=server_subtotal,

        shipping_fee=server_shipping,

        discount=server_discount,

        total=server_total,
    )

    # -----------------------------------------------------
    # Create order items
    # -----------------------------------------------------

    for item in clean_items:

        OrderItem.objects.create(

            order=order,

            product=item["product"],

            product_name=item["product_name"],

            size=item["size"],

            price=item["price"],

            quantity=item["quantity"],

            image_url=item["image_url"],
        )

    # -----------------------------------------------------
    # Send response to frontend
    # -----------------------------------------------------

    return JsonResponse(
        {
            "success": True,
            "order_number": order.order_number,
            "tracking_number": order.tracking_number,
        }
    )