# Salgateria da Jéssica — prévia

Prévia enxuta do sistema, com o fluxo de telas do protótipo:
**Login → Produtos (busca e pedido) → Pagamento → Registro → Comprovante**,
além de listas de Vendas e Estoque.

## Rodar (Windows: use `py` no lugar de `python`)
```bash
python -m pip install -r requirements.txt
python manage.py makemigrations loja
python manage.py migrate
python manage.py popular_demo
python manage.py runserver
```
Abra http://127.0.0.1:8000/ — usuários `carla` (atendente) e `jessica` (proprietária), senha `demo1234`.

Se você já tinha rodado uma versão anterior da prévia, apague `db.sqlite3` e `loja/migrations/0001_initial.py` antes de rodar os comandos acima.

## Estrutura
- `config/` configurações e rotas
- `loja/models.py` Produto, Venda, ItemVenda (valores em centavos inteiros)
- `loja/views.py` fluxo de venda; o pedido fica na sessão, e a venda, o pagamento e a baixa de estoque são gravados numa única transação
- `loja/templates/loja/` telas; `loja/static/loja/` CSS e JS próprios (sem dependência externa)
- `loja/management/commands/popular_demo.py` usuários e 14 produtos de demonstração

Fora da prévia: reposição/ajuste de estoque, histórico de movimentos, relatório, cancelamento e CRUD de catálogo (use `/admin/` com a Jéssica).
