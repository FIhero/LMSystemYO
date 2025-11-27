import stripe
from django.conf import settings

class StripeService:
    @staticmethod
    def create_product(name: str):
        """Создает продукт в Stripe"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe.Product.create(name=name)

    @staticmethod
    def create_price(amount: int, product_id: str):
        """Создает цену в Stripe (amount в рублях)"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe.Price.create(
            unit_amount=amount * 100,
            currency="rub",
            product=product_id,
        )

    @staticmethod
    def create_checkout_session(price_id: str, course_id: int):
        """Создает сессию оплаты"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe.checkout.Session.create(
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"http://localhost:8000/api/payments/success/?course_id={course_id}",
            cancel_url="http://localhost:8000/api/payments/cancel/",
            metadata={"course_id": course_id}
        )

    @staticmethod
    def get_session_status(session_id: str):
        """Проверяет статус сессии оплаты"""
        session = stripe.checkout.Session.retrieve(session_id)
        return session['payment_status']

