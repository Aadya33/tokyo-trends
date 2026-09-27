from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


# =========================================================
# PRODUCT
# =========================================================

class Product(models.Model):

    CATEGORY_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("cosmetics", "Cosmetics"),
    ]

    name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def discount_percentage(self):

        if self.sale_price and self.sale_price < self.price:

            discount = (
                (self.price - self.sale_price)
                / self.price
            ) * 100

            return round(discount)

        return 0

    def current_price(self):

        if self.sale_price and self.sale_price < self.price:
            return self.sale_price

        return self.price

    def __str__(self):
        return self.name


# =========================================================
# PRODUCT IMAGES
# =========================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    position = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} - Image {self.position}"


# =========================================================
# PRODUCT SIZES
# =========================================================

class ProductSize(models.Model):

    SIZE_CHOICES = [
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("2XL", "2XL"),
        ("3XL", "3XL"),
        ("4XL", "4XL"),
        ("5XL", "5XL"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sizes"
    )

    size = models.CharField(
        max_length=4,
        choices=SIZE_CHOICES
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["id"]
        unique_together = ["product", "size"]

    def __str__(self):
        return f"{self.product.name} - {self.size}"


# =========================================================
# CLIENT
# =========================================================

class Client(models.Model):

    mobile = models.CharField(
        max_length=15,
        unique=True
    )

    email = models.EmailField(
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.mobile} - {self.email}"


# =========================================================
# REVIEW
# =========================================================

class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True
    )

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    review_image = models.ImageField(
        upload_to="reviews/",
        null=True,
        blank=True
    )

    verified_purchase = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("upi", "UPI"),
        ("card", "Credit/Debit Card"),
        ("netbanking", "Net Banking"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    STATUS_CHOICES = [
        ("placed", "Order Placed"),
        ("confirmed", "Confirmed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    # -----------------------------------------------------
    # Order identification
    # -----------------------------------------------------

    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    tracking_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    # -----------------------------------------------------
    # Customer details
    # -----------------------------------------------------

    full_name = models.CharField(
        max_length=150
    )

    mobile = models.CharField(
        max_length=15
    )

    email = models.EmailField()

    # -----------------------------------------------------
    # Shipping address
    # -----------------------------------------------------

    address = models.TextField()

    area = models.CharField(
        max_length=150
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )

    # -----------------------------------------------------
    # Payment
    # -----------------------------------------------------

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    # -----------------------------------------------------
    # Order status
    # -----------------------------------------------------

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="placed"
    )

    # -----------------------------------------------------
    # Pricing
    # -----------------------------------------------------

    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # -----------------------------------------------------
    # Dates
    # -----------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    def save(self, *args, **kwargs):

        if not self.order_number:

            self.order_number = (
                "TT-"
                + uuid.uuid4().hex[:10].upper()
            )

        if not self.tracking_number:

            self.tracking_number = (
                "TTTRK"
                + uuid.uuid4().hex[:10].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items"
    )

    product_name = models.CharField(
        max_length=200
    )

    size = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    image_url = models.CharField(
        max_length=500,
        blank=True,
        default=""
    )

    def __str__(self):
        return (
            f"{self.product_name} "
            f"x {self.quantity}"
        )