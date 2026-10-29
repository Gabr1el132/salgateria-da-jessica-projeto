import re
import unicodedata
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import ItemVenda, Produto, Venda, reais


def _sem_acento(texto):
    base = unicodedata.normalize("NFD", texto)
    return "".join(c for c in base if unicodedata.category(c) != "Mn").lower()


def _carrinho(request):
    """Pedido guardado na sessão: {id_produto: quantidade}."""
    return request.session.setdefault("carrinho", {})


def _linhas(request):
    carrinho = _carrinho(request)
    produtos = Produto.objects.filter(id__in=[int(i) for i in carrinho])
    linhas, total = [], 0
    for p in produtos:
        qtd = carrinho[str(p.id)]
        sub = qtd * p.preco_centavos
        total += sub
        linhas.append({"produto": p, "qtd": qtd, "subtotal": reais(sub)})
    return linhas, total


@require_POST
def sair(request):
    logout(request)
    return redirect("entrar")


@login_required
def pedido(request):
    busca = request.GET.get("q", "").strip()
    produtos = Produto.objects.filter(ativo=True)
    if busca:
        termo = _sem_acento(busca)
        produtos = [p for p in produtos if termo in _sem_acento(p.nome) or termo in _sem_acento(p.categoria)]
    linhas, total = _linhas(request)
    return render(request, "loja/pedido.html", {
        "produtos": produtos, "busca": busca, "linhas": linhas, "total": reais(total),
    })


@login_required
@require_POST
def adicionar(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    try:
        qtd = max(int(request.POST.get("qtd", 1)), 1)
    except ValueError:
        qtd = 1
    carrinho = _carrinho(request)
    novo = carrinho.get(str(produto.id), 0) + qtd
    if novo > produto.saldo:
        messages.error(request, f"Saldo insuficiente de {produto.nome}: restam {produto.saldo}.")
    else:
        carrinho[str(produto.id)] = novo
        request.session.modified = True
    return redirect("pedido")


@login_required
@require_POST
def remover(request, produto_id):
    _carrinho(request).pop(str(produto_id), None)
    request.session.modified = True
    return redirect("pedido")


def _centavos(texto):
    try:
        return int((Decimal(texto.replace(",", ".")) * 100).to_integral_value())
    except (InvalidOperation, AttributeError):
        return None


@login_required
def pagamento(request):
    linhas, total = _linhas(request)
    if not linhas:
        messages.error(request, "O pedido está vazio.")
        return redirect("pedido")

    erro = None
    if request.method == "POST":
        forma = request.POST.get("forma")
        recebido = total
        if forma == "dinheiro":
            recebido = _centavos(request.POST.get("recebido", ""))
            if recebido is None or recebido < total:
                erro = "O valor recebido deve ser maior ou igual ao total."
        elif forma not in ("pix", "cartao"):
            erro = "Escolha a forma de pagamento."

        if not erro:
            try:
                with transaction.atomic():
                    venda = Venda.objects.create(
                        atendente=request.user, forma_pagamento=forma,
                        total_centavos=total, recebido_centavos=recebido,
                    )
                    for l in linhas:
                        p = Produto.objects.select_for_update().get(id=l["produto"].id)
                        if p.saldo < l["qtd"]:
                            raise ValueError(f"Saldo insuficiente de {p.nome}.")
                        ItemVenda.objects.create(
                            venda=venda, produto=p, quantidade=l["qtd"],
                            preco_unitario_centavos=p.preco_centavos,
                        )
                        Produto.objects.filter(id=p.id).update(saldo=F("saldo") - l["qtd"])
            except ValueError as e:
                messages.error(request, str(e))
                return redirect("pedido")
            request.session["carrinho"] = {}
            return redirect("comprovante", venda_id=venda.id)

    return render(request, "loja/pagamento.html", {
        "linhas": linhas, "total": reais(total), "erro": erro,
    })


@login_required
def comprovante(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    return render(request, "loja/comprovante.html", {"venda": venda})


@login_required
def vendas(request):
    lista = Venda.objects.select_related("atendente").order_by("-criada_em")[:50]
    return render(request, "loja/vendas.html", {"vendas": lista})


@login_required
def estoque(request):
    return render(request, "loja/estoque.html", {"produtos": Produto.objects.all()})
