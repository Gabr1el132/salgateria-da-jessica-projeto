from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("entrar/", auth_views.LoginView.as_view(template_name="loja/entrar.html"), name="entrar"),
    path("sair/", views.sair, name="sair"),
    path("", views.pedido, name="pedido"),
    path("adicionar/<int:produto_id>/", views.adicionar, name="adicionar"),
    path("remover/<int:produto_id>/", views.remover, name="remover"),
    path("pagamento/", views.pagamento, name="pagamento"),
    path("venda/<int:venda_id>/comprovante/", views.comprovante, name="comprovante"),
    path("vendas/", views.vendas, name="vendas"),
    path("estoque/", views.estoque, name="estoque"),
]
