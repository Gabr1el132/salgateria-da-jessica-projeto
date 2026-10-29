from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from loja.models import Produto

PRODUTOS = [
    ("Coxinha de frango", "Salgados fritos", 700, 40),
    ("Coxinha de catupiry", "Salgados fritos", 800, 30),
    ("Pastel de carne", "Salgados fritos", 900, 25),
    ("Pastel de queijo", "Salgados fritos", 900, 25),
    ("Risole de presunto", "Salgados fritos", 750, 20),
    ("Kibe", "Salgados fritos", 750, 30),
    ("Enroladinho de salsicha", "Salgados assados", 650, 35),
    ("Esfiha de carne", "Salgados assados", 800, 20),
    ("Pão de queijo", "Salgados assados", 500, 50),
    ("Refrigerante lata", "Bebidas", 600, 24),
    ("Suco de laranja", "Bebidas", 700, 15),
    ("Água mineral", "Bebidas", 400, 30),
    ("Brigadeiro", "Doces", 350, 40),
    ("Pudim fatia", "Doces", 900, 10),
]


class Command(BaseCommand):
    help = "Cria usuários e produtos de demonstração"

    def handle(self, *args, **opts):
        U = get_user_model()
        if not U.objects.filter(username="jessica").exists():
            U.objects.create_superuser("jessica", password="demo1234", first_name="Jéssica")
        if not U.objects.filter(username="carla").exists():
            U.objects.create_user("carla", password="demo1234", first_name="Carla")
        for nome, cat, preco, saldo in PRODUTOS:
            Produto.objects.get_or_create(
                nome=nome, defaults={"categoria": cat, "preco_centavos": preco, "saldo": saldo})
        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados. Senha: demo1234"))
