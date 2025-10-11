# products/management/commands/populate_data.py
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = "Populate database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating categories...")

        # Create categories
        electronics = Category.objects.get_or_create(
            name="Electronics",
            defaults={"description": "Electronic devices and gadgets"},
        )[0]

        clothing = Category.objects.get_or_create(
            name="Clothing", defaults={"description": "Fashion and apparel"}
        )[0]

        books = Category.objects.get_or_create(
            name="Books", defaults={"description": "Books and magazines"}
        )[0]

        home = Category.objects.get_or_create(
            name="Home & Garden",
            defaults={"description": "Home improvement and garden supplies"},
        )[0]

        self.stdout.write(self.style.SUCCESS("✓ Categories created"))

        # Optional: Create a test user if needed
        user, created = User.objects.get_or_create(
            username="seller1",
            defaults={
                "email": "seller1@example.com",
                "first_name": "Test",
                "last_name": "Seller",
            },
        )
        if created:
            user.set_password("TestPass123!")
            user.save()
            self.stdout.write(
                self.style.SUCCESS("✓ Test user created (seller1/TestPass123!)")
            )

        # Optional: Create sample products
        Product.objects.get_or_create(
            name="iPhone 15 Pro",
            defaults={
                "description": "Latest iPhone with A17 chip",
                "price": 999.99,
                "stock": 50,
                "category": electronics,
                "seller": user,
            },
        )

        Product.objects.get_or_create(
            name="MacBook Pro",
            defaults={
                "description": "Powerful laptop for professionals",
                "price": 2499.99,
                "stock": 20,
                "category": electronics,
                "seller": user,
            },
        )

        self.stdout.write(self.style.SUCCESS("✓ Sample products created"))
        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
