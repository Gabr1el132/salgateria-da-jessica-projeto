import unicodedata
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import CATEGORIAS, ItemVenda, Produto, Venda

PASSOS = ["Produtos", "Pagamento", "Registro", "Comprovante"]


def _passos(atual):
    return [
        {"n": i + 1, "nome": nome,
         "estado": "done" if i + 1 < atual else "atual" if i + 1 == atual else "futuro"}
        for i, nome in enumerate(PASSOS)
    ]


def _sem_acento(texto):
    base = unicodedata.normalize("NFD", texto)
    return "".join(c for c in base if unicodedata.category(c) != "Mn").lower()


def _carrinho(request):
    """Pedido guardado na sessão: {id_produto: quantidade}."""
    return request.session.setdefault("carrinho", {})


def _mudou(request, produto_id=None):
    """Itens mudaram: o pagamento informado precisa ser refeito."""
    request.session.pop("pagamento", None)
    if produto_id:
        request.session["ultimo"] = produto_id
    request.session.modified = True


def _linhas(request):
    carrinho = _carrinho(request)
    produtos = Produto.objects.in_bulk([int(i) for i in carrinho])
    linhas, total, unidades = [], 0, 0
    for chave, qtd in carrinho.items():
        p = produtos.get(int(chave))
        if not p:
            continue
        sub = qtd * p.preco_centavos
        total += sub
        unidades += qtd
        linhas.append({"produto": p, "qtd": qtd, "preco": p.preco_centavos, "subtotal": sub})
    return linhas, total, unidades


def _voltar(request, padrao="pedido"):
    destino = request.POST.get("voltar", "")
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return redirect(destino)
    return redirect(padrao)


def _centavos(texto):
    texto = (texto or "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        return None
    return int((valor * 100).to_integral_value()) if valor >= 0 else None


@require_POST
def sair(request):
    logout(request)
    return redirect("entrar")


# ---------- Passo 1: produtos e pedido ----------

@login_required
def pedido(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    buscou = bool(q or cat)
    produtos = []
    if buscou:
        qs = Produto.objects.filter(ativo=True)
        if cat and cat != "todas":
            qs = qs.filter(categoria=cat)
        termo = _sem_acento(q)
        produtos = [p for p in qs if termo in _sem_acento(p.nome)]
        carrinho = _carrinho(request)
        for p in produtos:
            p.no_pedido = carrinho.get(str(p.id), 0)
    linhas, total, unidades = _linhas(request)
    return render(request, "loja/pedido.html", {
        "passos": _passos(1), "q": q, "cat": cat or "todas", "buscou": buscou,
        "categorias": [("todas", "Todas")] + CATEGORIAS,
        "cat_nome": dict(CATEGORIAS).get(cat, "Todas"),
        "produtos": produtos, "linhas": linhas, "total": total, "unidades": unidades,
        "ultimo": request.session.get("ultimo"), "voltar": request.get_full_path(),
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
    atual = carrinho.get(str(produto.id), 0)
    if atual + qtd > produto.saldo:
        restante = max(produto.saldo - atual, 0)
        messages.error(request, f"Saldo insuficiente de {produto.nome}: dá para adicionar mais {restante}.")
    else:
        carrinho[str(produto.id)] = atual + qtd
        _mudou(request, produto.id)
        messages.success(
            request, f"{qtd} × {produto.nome} {'adicionada' if qtd == 1 else 'adicionadas'} ao pedido.")
    return _voltar(request)


@login_required
@require_POST
def alterar(request, produto_id):
    carrinho = _carrinho(request)
    chave = str(produto_id)
    delta = 1 if request.POST.get("delta") == "1" else -1
    if chave in carrinho:
        produto = get_object_or_404(Produto, id=produto_id)
        novo = carrinho[chave] + delta
        if novo <= 0:
            del carrinho[chave]
        elif novo > produto.saldo:
            messages.error(request, f"Saldo insuficiente de {produto.nome}: restam {produto.saldo}.")
        else:
            carrinho[chave] = novo
        _mudou(request, produto_id)
    return _voltar(request)


@login_required
@require_POST
def remover(request, produto_id):
    _carrinho(request).pop(str(produto_id), None)
    _mudou(request)
    return _voltar(request)


# ---------- Passo 2: pagamento ----------

@login_required
def pagamento(request):
    linhas, total, unidades = _linhas(request)
    if not linhas:
        messages.error(request, "O pedido está vazio.")
        return redirect("pedido")

    salvo = request.session.get("pagamento", {})
    forma = salvo.get("forma", "dinheiro")
    recebido = salvo.get("recebido", 0) if forma == "dinheiro" else 0
    erro = None

    if request.method == "POST":
        forma = request.POST.get("forma", "")
        recebido = _centavos(request.POST.get("recebido")) or 0
        if forma not in dict(Venda.FORMAS):
            erro = "Escolha a forma de pagamento."
        elif forma == "dinheiro" and recebido < total:
            erro = "Informe um valor recebido maior ou igual ao total."
        else:
            request.session["pagamento"] = {"forma": forma, "recebido": recebido if forma == "dinheiro" else total}
            return redirect("registro")

    return render(request, "loja/pagamento.html", {
        "passos": _passos(2), "linhas": linhas, "total": total, "unidades": unidades,
        "forma": forma, "forma_nome": dict(Venda.FORMAS).get(forma, "Dinheiro"),
        "recebido": recebido, "erro": erro,
        "rapidos": [{"c": v, "exato": v == total} for v in sorted({2000, 5000, 10000, total})],
    })


# ---------- Passo 3: registro ----------

@login_required
def registro(request):
    linhas, total, unidades = _linhas(request)
    pg = request.session.get("pagamento")
    if not linhas:
        return redirect("pedido")
    if not pg:
        return redirect("pagamento")
    forma, recebido = pg["forma"], pg["recebido"]

    if request.method == "POST":
        if forma == "dinheiro" and recebido < total:
            return redirect("pagamento")
        try:
            with transaction.atomic():
                venda = Venda.objects.create(
                    atendente=request.user, forma_pagamento=forma,
                    total_centavos=total, recebido_centavos=recebido)
                for l in linhas:
                    p = Produto.objects.select_for_update().get(id=l["produto"].id)
                    if p.saldo < l["qtd"]:
                        raise ValueError(f"Saldo insuficiente de {p.nome}: restam {p.saldo}.")
                    ItemVenda.objects.create(
                        venda=venda, produto=p, quantidade=l["qtd"],
                        preco_unitario_centavos=p.preco_centavos)
                    Produto.objects.filter(id=p.id).update(saldo=F("saldo") - l["qtd"])
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("pedido")
        for chave in ("carrinho", "pagamento", "ultimo"):
            request.session.pop(chave, None)
        return redirect("comprovante", venda_id=venda.id)

    return render(request, "loja/registro.html", {
        "passos": _passos(3), "linhas": linhas, "total": total,
        "forma": forma, "forma_nome": dict(Venda.FORMAS)[forma],
        "recebido": recebido, "troco": max(recebido - total, 0),
    })


# ---------- Passo 4: comprovante e consultas ----------

@login_required
def comprovante(request, venda_id):
    venda = get_object_or_404(Venda.objects.select_related("atendente"), id=venda_id)
    return render(request, "loja/comprovante.html", {"passos": _passos(5), "venda": venda})


@login_required
def vendas(request):
    lista = Venda.objects.select_related("atendente").order_by("-criada_em")[:50]
    return render(request, "loja/vendas.html", {"vendas": lista})


@login_required
def estoque(request):
    return render(request, "loja/estoque.html", {"produtos": Produto.objects.all()})
