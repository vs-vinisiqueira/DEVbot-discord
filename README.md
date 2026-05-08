# DEVbot Discord

Bot para Discord desenvolvido em Python, com automação de setup de servidores e integração com Trello.

## Sobre o projeto

O DEVbot é um bot para Discord criado para apoiar a organização inicial de servidores e facilitar o registro de tarefas em um quadro do Trello.

O projeto foi estruturado de forma simples, separando configurações, constantes, integração externa e comandos em módulos próprios. A proposta é manter o código legível e fácil de evoluir, sem esconder a lógica principal em abstrações desnecessárias.

## Funcionalidades atuais

- Verificação de status do bot com comando de ping.
- Configuração inicial de servidor com criação de cargos, categorias e canais.
- Criação de tarefas no Trello a partir de comandos no Discord.
- Configuração por variáveis de ambiente.

## Tecnologias utilizadas

- Python
- discord.py
- python-dotenv
- aiohttp
- Trello API

## Estrutura do projeto

```text
DEVbot-discord/
├── devbot/
│   ├── commands/
│   │   ├── general.py
│   │   ├── server_setup.py
│   │   └── tasks.py
│   ├── bot_factory.py
│   ├── config.py
│   ├── constants.py
│   └── trello.py
├── bot.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Como executar o projeto

Clone o repositório:

```bash
git clone https://github.com/vs-vinisiqueira/DEVbot-discord.git
cd DEVbot-discord
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows, ative o ambiente virtual:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o bot:

```bash
python bot.py
```

## Configuração das variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no arquivo `.env.example`.

```env
DISCORD_TOKEN=seu_token_do_discord
COMMAND_PREFIX=!

TRELLO_API_KEY=sua_api_key_do_trello
TRELLO_TOKEN=seu_token_do_trello
TRELLO_LIST_ID=id_da_lista_do_trello
```

Variáveis utilizadas:

- `DISCORD_TOKEN`: token do bot criado no Discord Developer Portal.
- `COMMAND_PREFIX`: prefixo usado para executar comandos no servidor.
- `TRELLO_API_KEY`: chave de API da conta Trello.
- `TRELLO_TOKEN`: token de acesso da conta Trello.
- `TRELLO_LIST_ID`: identificador da lista onde os cards serão criados.

## Comandos disponíveis

| Comando | Descrição |
| --- | --- |
| `!ping` | Verifica se o DEVbot está online. |
| `!setup` | Cria cargos, categorias e canais iniciais no servidor. Requer permissão de administrador. |
| `!tarefa <descrição>` | Cria uma tarefa no Trello com a descrição informada. |

## Aprendizados

Este projeto consolida práticas importantes de desenvolvimento com bots para Discord, como organização modular de comandos, leitura de variáveis de ambiente, uso de intents do Discord e integração assíncrona com APIs externas.

Também reforça cuidados com separação de responsabilidades, mensagens de erro claras e configuração segura por meio de arquivo `.env`.

## Status do projeto

Projeto funcional em estágio inicial, com foco em automação básica de servidor Discord e integração com Trello.
