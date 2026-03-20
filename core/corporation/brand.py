import random

class BrandAgnecy:
    """
    PR Department.
    """
    def generate_ad_copy(self, product_name):
        adjectives = ["Revolutionary", "AI-Powered", "Synergistic", "Hyper-Modern"]
        adj = random.choice(adjectives)
        return f"Introducing {product_name}: The most {adj} solution for your business. Buy now."

brand = BrandAgnecy()
