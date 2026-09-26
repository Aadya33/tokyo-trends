from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Client


# =========================================
# HOME
# =========================================

def home(request):
    return render(request, "home.html")


# =========================================
# MEN
# =========================================

def men(request):

    products = (
        Product.objects
        .filter(category="men")
        .prefetch_related("images")
    )

    return render(
        request,
        "men.html",
        {
            "products": products
        }
    )


# =========================================
# WOMEN
# =========================================

def women(request):

    products = (
        Product.objects
        .filter(category="women")
        .prefetch_related("images")
    )

    return render(
        request,
        "women.html",
        {
            "products": products
        }
    )


# =========================================
# COSMETICS
# =========================================

def cosmetics(request):

    products = (
        Product.objects
        .filter(category="cosmetics")
        .prefetch_related("images")
    )

    return render(
        request,
        "cosmetics.html",
        {
            "products": products
        }
    )


# =========================================
# LOGIN
# =========================================

def login(request):

    if request.method == "POST":

        mobile = request.POST.get(
            "mobile",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()


        # -----------------------------
        # CHECK EMPTY FIELDS
        # -----------------------------

        if not mobile or not email:

            return render(
                request,
                "login.html",
                {
                    "error":
                    "Please enter your mobile number and email address."
                }
            )


        # -----------------------------
        # FIND EXISTING CLIENT
        # -----------------------------

        try:

            client = Client.objects.get(
                mobile=mobile
            )


            # Mobile exists but email doesn't match

            if client.email != email:

                return render(
                    request,
                    "login.html",
                    {
                        "error":
                        "This mobile number is already registered with another email address."
                    }
                )


        # -----------------------------
        # NEW CLIENT
        # -----------------------------

        except Client.DoesNotExist:

            # Check whether email already belongs
            # to another client

            if Client.objects.filter(
                email=email
            ).exists():

                return render(
                    request,
                    "login.html",
                    {
                        "error":
                        "This email address is already registered with another mobile number."
                    }
                )


            # Create new client

            client = Client.objects.create(
                mobile=mobile,
                email=email
            )


        # -----------------------------
        # SAVE CLIENT IN SESSION
        # -----------------------------

        request.session["client_id"] = client.id


        # -----------------------------
        # GO HOME
        # -----------------------------

        return redirect("/")


    # GET REQUEST

    return render(
        request,
        "login.html"
    )


# =========================================
# LOGOUT
# =========================================

def logout(request):

    request.session.flush()

    return redirect("/")


# =========================================
# PRODUCT DETAIL
# =========================================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product.objects.prefetch_related(
            "images",
            "sizes",
            "reviews"
        ),
        id=product_id
    )


    return render(
        request,
        "product_detail.html",
        {
            "product": product
        }
    )