from django.conf import settings
from django.db import models

CATEGORIAS = [("fritos", "Fritos"), ("assados", "Assados"), ("bebidas", "Bebidas"), ("pacotes", "Pacotes")]


class Produto(models.Model):
    nome = models.CharField(max_length=80)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    unidade = models.CharField(max_length=20, default="unidade")
    preco_centavos = models.PositiveIntegerField()
    saldo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["categoria", "nome"]

    def __str__(self):
        return self.nome


class Venda(models.Model):
    FORMAS = [("dinheiro", "Dinheiro"), ("pix", "Pix"), ("cartao", "Cartão")]

    atendente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    criada_em = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=10, choices=FORMAS)
    total_centavos = models.PositiveIntegerField()
    recebido_centavos = models.PositiveIntegerField(default=0)

    @property
    def codigo(self):
        return f"V-{self.id:06d}"

    @property
    def troco_centavos(self):
        return max(self.recebido_centavos - self.total_centavos, 0)


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name="itens", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario_centavos = models.PositiveIntegerField()

    @property
    def subtotal_centavos(self):
        return self.quantidade * self.preco_unitario_centavos
