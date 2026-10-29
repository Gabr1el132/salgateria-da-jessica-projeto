from django.conf import settings
from django.db import models


def reais(centavos):
    """750 -> 'R$ 7,50'"""
    inteiro, resto = divmod(int(centavos), 100)
    return f"R$ {inteiro:,}".replace(",", ".") + f",{resto:02d}"


class Produto(models.Model):
    nome = models.CharField(max_length=80)
    categoria = models.CharField(max_length=40)
    preco_centavos = models.PositiveIntegerField()
    saldo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["categoria", "nome"]

    def __str__(self):
        return self.nome

    @property
    def preco(self):
        return reais(self.preco_centavos)


class Venda(models.Model):
    FORMAS = [("dinheiro", "Dinheiro"), ("pix", "Pix"), ("cartao", "Cartão")]

    atendente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    criada_em = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=10, choices=FORMAS)
    total_centavos = models.PositiveIntegerField()
    recebido_centavos = models.PositiveIntegerField(default=0)

    @property
    def total(self):
        return reais(self.total_centavos)

    @property
    def troco(self):
        return reais(max(self.recebido_centavos - self.total_centavos, 0))


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name="itens", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario_centavos = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return reais(self.quantidade * self.preco_unitario_centavos)

    @property
    def preco(self):
        return reais(self.preco_unitario_centavos)
