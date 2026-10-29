# Salgateria da Jéssica — prévia simplificada

Versão enxuta do sistema: login, busca de produtos, pedido com validação de saldo,
pagamento (dinheiro com troco, Pix, cartão), baixa de estoque e comprovante.
Estilo mínimo, sem dependências além do Django.

## Rodar
```bash
pip install -r requirements.txt
python manage.py makemigrations loja
python manage.py migrate
python manage.py popular_demo
python manage.py runserver
```
Abra http://127.0.0.1:8000/ — usuários `jessica` e `carla`, senha `demo1234`.

## Estrutura
- `config/` configurações e rotas
- `loja/` modelos (Produto, Venda, ItemVenda), views, templates e comando `popular_demo`

Valores em centavos inteiros; a venda e a baixa de estoque acontecem numa única transação.
Fora desta prévia: histórico de movimentos, relatório, CRUD de catálogo e perfis (use o `/admin/`).
