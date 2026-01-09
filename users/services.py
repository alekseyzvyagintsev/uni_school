#########################################################################################
import stripe
from uni_school.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

def create_stripe_session(price):
    """ Создаёт цену продукта в Stripe. """
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")


#########################################################################################
