# FinanceFlow

Sistema web de **controle financeiro pessoal** construído com Streamlit, SQLAlchemy,
Pandas e Plotly. Interface responsiva (desktop e celular), autenticação com bcrypt e
arquitetura em camadas pronta para crescer.

---

## Stack

| Camada | Tecnologia |
| --- | --- |
| Interface | Streamlit |
| ORM | SQLAlchemy 2.0 |
| Banco (dev) | SQLite |
| Banco (produção) | PostgreSQL |
| Dados / cálculos | Pandas |
| Gráficos | Plotly |
| Senhas | bcrypt |
| Configuração | python-dotenv |

---

## Como executar

Pré-requisito: **Python 3.13** ([python.org/downloads](https://www.python.org/downloads/) —
marque a opção *Add python.exe to PATH* durante a instalação).

> Evite o Python 3.15 por enquanto: o `pyarrow`, usado internamente pelo Streamlit,
> ainda não publica pacote compilado para essa versão e a instalação falha pedindo
> o Microsoft C++ Build Tools.

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

No Linux/macOS, troque a ativação por `source .venv/bin/activate`.

A aplicação abre em `http://localhost:8501`. Na primeira execução o banco
`financeflow.db` (SQLite) é criado automaticamente — basta usar a aba
**Criar conta** para começar.

---

## Trocando SQLite por PostgreSQL

Copie `.env.example` para `.env` e defina apenas a variável de conexão:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/financeflow
```

Nenhuma outra linha de código precisa mudar: a engine é criada a partir dessa
variável em `config/database.py`.

---

## Estrutura do projeto

```text
.
├── app.py                        # Ponto de entrada: tema, sessão e roteamento
├── config/
│   ├── database.py               # Engine, sessão e criação do schema
│   └── settings.py               # Constantes, categorias, moedas e .env
├── models/
│   ├── usuario.py                # Entidade Usuario
│   └── movimentacao.py           # Entidade Movimentacao
├── repositories/                 # Acesso a dados (somente SQL/ORM)
│   ├── usuario_repository.py
│   └── movimentacao_repository.py
├── services/                     # Regras de negócio
│   ├── auth_service.py           # Cadastro, login, logout, perfil
│   ├── movimentacao_service.py   # CRUD, filtros e exportação (Pandas)
│   └── dashboard_service.py      # Indicadores, séries e insights (Pandas)
├── pages/                        # Telas (apenas apresentação)
│   ├── login.py
│   ├── dashboard.py
│   ├── movimentacoes.py
│   └── configuracoes.py
├── components/                   # Blocos visuais reutilizáveis
│   ├── sidebar.py
│   ├── cards.py
│   ├── tabelas.py
│   ├── graficos.py
│   └── estilos.py                # Paletas + injeção do CSS
├── utils/
│   ├── formatters.py             # Moeda, datas e percentuais em pt-BR
│   └── validations.py            # Validações com mensagens amigáveis
├── assets/
│   ├── logo.svg
│   └── styles.css                # Folha de estilo única (desktop + mobile)
├── .streamlit/config.toml
├── requirements.txt
└── README.md
```

### Fluxo de uma requisição

```text
pages/ (interface)  ->  services/ (regras + Pandas)  ->  repositories/ (ORM)  ->  banco
```

As páginas nunca acessam o banco diretamente e os repositórios nunca calculam
indicadores: todo cálculo é feito com Pandas na camada de serviços.

---

## Funcionalidades

**Dashboard**
- Cards de Saldo Atual, Receitas do mês, Despesas do mês e Economizado
  (com variação percentual sobre o mês anterior).
- Gráfico de linha: receitas, despesas e saldo acumulado dos últimos 6 meses.
- Gráfico de rosca: distribuição das despesas do mês por categoria, com legenda de valores.
- Últimas 5 movimentações e contas a vencer no mês.
- Insights automáticos gerados a partir do DataFrame.

**Movimentações**
- Tela única para receitas e despesas.
- Cadastro, edição e exclusão em diálogos (modais) com confirmação.
- Busca textual e filtros por período, categoria e tipo.

**Configurações**
- Alteração de nome, e-mail, telefone e senha.
- Tema (claro/escuro), idioma e moeda.
- Exportação das movimentações em CSV e informação do banco em uso.

---

## Responsividade

Todas as telas foram pensadas para o celular:

- As colunas do Streamlit recebem `flex-wrap` abaixo de 820px e passam a ocupar
  a largura total, empilhando cards, gráficos e painéis.
- Colunas aninhadas (botões de ação) continuam lado a lado, evitando botões gigantes.
- A tabela de movimentações vira uma lista de cartões: o cabeçalho é ocultado e
  cada valor ganha um rótulo (`DATA`, `VALOR`, `STATUS`…) exibido apenas no mobile.
- A sidebar é recolhida automaticamente pelo próprio Streamlit em telas pequenas.

---

## Decisões de projeto

- **Status do lançamento** é derivado da data (futura = *Pendente*), sem coluna extra no banco.
- **Tema e moeda** foram adicionados ao modelo `Usuario` para que as preferências
  escolhidas em Configurações sobrevivam ao logout.
- **Navegação**: `st.navigation(..., position="hidden")` desativa o menu automático do
  Streamlit, permitindo a sidebar customizada sem duplicar links.
- **Sessões do SQLAlchemy** usam `expire_on_commit=False`, o que permite usar os objetos
  depois que a sessão é fechada sem reabrir conexões.

---

## Próximos passos sugeridos

- Metas de gastos por categoria e alertas de estouro.
- Importação de extratos (CSV/OFX).
- Lançamentos recorrentes e parcelados.
- Testes automatizados com `pytest` sobre a camada de serviços.
