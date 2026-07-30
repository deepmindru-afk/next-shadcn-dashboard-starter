"""Seed the database with sample data using faker."""

from faker import Faker

from .database import SessionLocal, init_db
from .models import Product, User

fake = Faker()

PRODUCT_CATEGORIES = [
    "Electronics",
    "Furniture",
    "Clothing",
    "Toys",
    "Groceries",
    "Books",
    "Jewelry",
    "Beauty Products",
]

USER_ROLES = ["Developer", "Designer", "Manager", "QA", "DevOps", "Product Owner"]
USER_STATUSES = ["Active", "Inactive", "Invited"]


def seed_products(count: int = 20) -> list[Product]:
    products = []
    for i in range(1, count + 1):
        product = Product(
            name=fake.unique.word().title() + " " + fake.word().title(),
            description=fake.sentence(nb_words=10),
            price=round(fake.random.uniform(5, 500), 2),
            category=fake.random_element(PRODUCT_CATEGORIES),
            photo_url=f"https://api.slingacademy.com/public/sample-products/{i}.png",
        )
        products.append(product)
    fake.unique.clear()
    return products


def seed_users(count: int = 50) -> list[User]:
    users = []
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=fake.unique.email(),
            phone=fake.phone_number(),
            status=fake.random_element(USER_STATUSES),
            role=fake.random_element(USER_ROLES),
        )
        users.append(user)
    fake.unique.clear()
    return users


def seed_database():
    """Main entry point – drops and re-creates data."""
    init_db()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()

        # Seed
        products = seed_products(20)
        users = seed_users(50)

        db.add_all(products)
        db.add_all(users)
        db.commit()

        print(f"✅ Seeded {len(products)} products and {len(users)} users.")
    except Exception as exc:
        db.rollback()
        print(f"❌ Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
