from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from loja.models import Produto

# (nome, categoria, unidade, preço em centavos, saldo)
PRODUTOS = [
    ("Coxinha de frango", "fritos", "unidade", 750, 42),
    ("Coxinha de frango com catupiry", "fritos", "unidade", 850, 18),
    ("Mini coxinha (pacote com 25)", "pacotes", "pacote", 3200, 0),
    ("Pastel de carne", "fritos", "unidade", 800, 30),
    ("Pastel de queijo", "fritos", "unidade", 800, 25),
    ("Kibe", "fritos", "unidade", 750, 30),
    ("Risole de presunto", "fritos", "unidade", 750, 20),
    ("Enroladinho de salsicha", "assados", "unidade", 650, 35),
    ("Esfiha de carne", "assados", "unidade", 800, 20),
    ("Pão de queijo", "assados", "unidade", 500, 50),
    ("Refrigerante lata", "bebidas", "unidade", 600, 24),
    ("Suco de laranja", "bebidas", "unidade", 700, 15),
    ("Água mineral", "bebidas", "unidade", 400, 30),
    ("Salgados assados (pacote com 50)", "pacotes", "pacote", 6500, 6),
]


class Command(BaseCommand):
    help = "Cria usuários e produtos de demonstração"

    def handle(self, *args, **opts):
        U = get_user_model()
        if not U.objects.filter(username="jessica").exists():
            U.objects.create_superuser("jessica", password="demo1234", first_name="Jéssica")
        if not U.objects.filter(username="carla").exists():
            U.objects.create_user("carla", password="demo1234", first_name="Carla")
        for nome, cat, unidade, preco, saldo in PRODUTOS:
            Produto.objects.get_or_create(nome=nome, defaults={
                "categoria": cat, "unidade": unidade, "preco_centavos": preco, "saldo": saldo})
        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados. Senha: demo1234"))
