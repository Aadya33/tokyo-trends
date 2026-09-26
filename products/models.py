from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("cosmetics", "Cosmetics"),
    ]

    name = models.CharField(max_length=200)

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