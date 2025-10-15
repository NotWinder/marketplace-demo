# products/management/commands/populate_data.py
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = "Populate database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating categories...")
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

        Product.objects.get_or_create(
            name="Classic Denim Jeans",
            defaults={
                "description": "Comfortable straight-fit jeans in classic blue",
                "price": 59.99,
                "stock": 100,
                "category": clothing,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Cotton T-Shirt Pack",
            defaults={
                "description": "Set of 3 premium cotton t-shirts in assorted colors",
                "price": 34.99,
                "stock": 150,
                "category": clothing,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Winter Wool Coat",
            defaults={
                "description": "Elegant wool coat perfect for cold weather",
                "price": 189.99,
                "stock": 30,
                "category": clothing,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Running Sneakers",
            defaults={
                "description": "Lightweight athletic shoes with cushioned sole",
                "price": 89.99,
                "stock": 75,
                "category": clothing,
                "seller": user,
            },
        )

        Product.objects.get_or_create(
            name="The Art of Programming",
            defaults={
                "description": "Comprehensive guide to software development best practices",
                "price": 45.99,
                "stock": 60,
                "category": books,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Mystery at Midnight",
            defaults={
                "description": "Thrilling detective novel with unexpected twists",
                "price": 14.99,
                "stock": 200,
                "category": books,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Cooking Masterclass",
            defaults={
                "description": "Professional chef techniques for home cooks",
                "price": 32.99,
                "stock": 45,
                "category": books,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="World Atlas 2025",
            defaults={
                "description": "Updated atlas with detailed maps and geographical data",
                "price": 49.99,
                "stock": 25,
                "category": books,
                "seller": user,
            },
        )

        Product.objects.get_or_create(
            name="Cordless Drill Set",
            defaults={
                "description": "20V cordless drill with 50-piece accessory kit",
                "price": 129.99,
                "stock": 40,
                "category": home,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Garden Hose 100ft",
            defaults={
                "description": "Flexible, kink-resistant garden hose with spray nozzle",
                "price": 39.99,
                "stock": 80,
                "category": home,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="LED Desk Lamp",
            defaults={
                "description": "Adjustable LED lamp with touch controls and USB port",
                "price": 44.99,
                "stock": 90,
                "category": home,
                "seller": user,
            },
        )
        Product.objects.get_or_create(
            name="Ceramic Plant Pots Set",
            defaults={
                "description": "Set of 5 decorative ceramic pots with drainage holes",
                "price": 29.99,
                "stock": 120,
                "category": home,
                "seller": user,
            },
        )

        self.stdout.write(self.style.SUCCESS("✓ Sample products created"))
        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
