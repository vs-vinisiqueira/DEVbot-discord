# MeuSiteJá Discord Bot

![Python](https://img.shields.io/badge/Python-3.x-blue)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2)
![Trello API](https://img.shields.io/badge/Trello%20API-integration-0079BF)
![OpenAI API](https://img.shields.io/badge/OpenAI%20API-integration-412991)
![Status](https://img.shields.io/badge/status-est%C3%A1gio%20inicial-yellow)

Bot para Discord desenvolvido em Python, com automação de configuração inicial do servidor do projeto MeuSiteJá, integração com Trello para criação de tarefas por comandos e ações simples interpretadas pela OpenAI API.

## Sobre o projeto

O **MeuSiteJá Discord Bot** é um projeto de automação para Discord voltado à organização inicial do ambiente do projeto MeuSiteJá. Ele reúne comandos simples para verificar o status do bot, criar uma estrutura inicial de cargos, categorias e canais, registrar tarefas em uma lista do Trello e interpretar pedidos controlados em linguagem natural com a OpenAI API.

O projeto foi construído com foco em clareza, separação de responsabilidades e uso de variáveis de ambiente para configuração. Por estar em estágio inicial, mantém uma estrutura objetiva e fácil de entender, adequada para demonstrar fundamentos de desenvolvimento backend, automação e integração com APIs externas.

## Funcionalidades atuais

- Verificação de status do bot com o comando `!ping`.
- Configuração inicial do servidor MeuSiteJá com o comando `!setup`.
- Criação de cargos, categorias e canais definidos no projeto, incluindo o canal `#arquivos`.
- Criação de tarefas no Trello com o comando `!tarefa <descrição>`.
- Interpretação de ações simples com o comando `!ia <pedido>`.
- Configuração do token do Discord, prefixo de comandos, credenciais do Trello e chave da OpenAI por variáveis de ambiente.

## Tecnologias utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| Python | Linguagem principal do bot. |
| discord.py | Comunicação com a API do Discord e criação dos comandos. |
| python-dotenv | Carregamento das variáveis de ambiente a partir do arquivo `.env`. |
| aiohttp | Requisições assíncronas para a API do Trello. |
| Trello API | Criação de cards em uma lista do Trello. |
| OpenAI API | Interpretação segura de pedidos em linguagem natural. |

## Estrutura do projeto

```text
DEVbot-discord/
├── devbot/
│   ├── commands/
│   │   ├── general.py
│   │   ├── ai_actions.py
│   │   ├── server_setup.py
│   │   └── tasks.py
│   ├── bot_factory.py
│   ├── config.py
│   ├── constants.py
│   ├── openai_client.py
│   └── trello.py
├── bot.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Como executar o projeto

1. Clone o repositório:

```bash
git clone https://github.com/vs-vinisiqueira/DEVbot-discord.git
cd DEVbot-discord
```

2. Crie um ambiente virtual:

```bash
python -m venv .venv
```

3. Ative o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente em um arquivo `.env`.

6. Execute o bot:

```bash
python bot.py
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto usando o arquivo `.env.example` como referência.

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `DISCORD_TOKEN` | Sim | Token do bot criado no Discord Developer Portal. |
| `COMMAND_PREFIX` | Não | Prefixo usado para executar os comandos. O padrão é `!`. |
| `TRELLO_API_KEY` | Para Trello | Chave de API da conta Trello. |
| `TRELLO_TOKEN` | Para Trello | Token de acesso da conta Trello. |
| `TRELLO_LIST_ID` | Para Trello | ID da lista onde os cards serão criados. |
| `OPENAI_API_KEY` | Para IA | Chave de API usada para interpretar pedidos do comando `!ia`. |

Exemplo:

```env
DISCORD_TOKEN=seu_token_do_discord
COMMAND_PREFIX=!

TRELLO_API_KEY=sua_api_key_do_trello
TRELLO_TOKEN=seu_token_do_trello
TRELLO_LIST_ID=id_da_lista_do_trello

OPENAI_API_KEY=sua_api_key_da_openai
```

## Comandos disponíveis

| Comando | Descrição |
| --- | --- |
| `!ping` | Verifica se o MeuSiteJá está online. |
| `!setup` | Cria cargos, categorias e canais iniciais do servidor MeuSiteJá. Requer permissão de administrador. |
| `!tarefa <descrição>` | Cria uma tarefa no Trello com a descrição informada. |
| `!ia <pedido>` | Interpreta um pedido simples com a OpenAI API e executa somente ações permitidas. |

Exemplos:

```text
!ia enviar no canal arquivos: "Segue o documento do projeto"
!ia fixar a última mensagem
!ia criar canal arquivos
!ia criar tarefa: Ajustar README do projeto
```

## Integração com OpenAI

O comando `!ia` usa a OpenAI API apenas para interpretar o pedido do usuário e retornar uma ação estruturada em JSON. O bot valida essa resposta antes de executar qualquer ação, sem executar texto bruto retornado pela IA.

Ações permitidas:

- `send_message`: envia mensagem em um canal de texto existente.
- `pin_last_message`: fixa a última mensagem válida do canal atual ou de um canal informado.
- `create_text_channel`: cria um canal de texto simples.
- `create_trello_task`: cria uma tarefa usando a integração Trello existente.
- `unknown`: resposta usada quando o pedido não está claro ou não é permitido.

Bloqueios de segurança:

- banir ou expulsar usuários;
- apagar canais;
- apagar mensagens em massa;
- alterar permissões;
- alterar cargos;
- mencionar `@everyone` ou `@here`;
- enviar mensagens ofensivas ou abusivas;
- expor tokens, secrets ou variáveis de ambiente.

Permissões:

- Criar canal e fixar mensagem exigem permissão de administrador.
- Enviar mensagens e criar tarefas por IA exigem administrador ou cargo `Equipe`.
- O bot também precisa ter permissões adequadas no Discord, como enviar mensagens, gerenciar canais ou gerenciar mensagens, conforme a ação.

## Estrutura criada pelo setup

O comando `!setup` cria os cargos `Administrador`, `Equipe`, `Desenvolvedor`, `Suporte`, `Cliente` e `Visitante`, se eles ainda não existirem.

Também cria as categorias e canais de texto usados para organizar o projeto:

- `📌 INFORMAÇÕES`: `#avisos`, `#regras`, `#links-importantes`
- `💻 PROJETO MEUSITEJÁ`: `#planejamento`, `#demandas`, `#tarefas`, `#arquivos`
- `🛠️ SUPORTE`: `#atendimento`, `#dúvidas`, `#suporte-técnico`
- `🤖 BOT`: `#comandos`, `#logs`

## Aprendizados técnicos

- Organização modular de comandos em um bot Discord.
- Uso de variáveis de ambiente para separar configuração e código.
- Criação de integrações assíncronas com APIs externas.
- Estruturação de um cliente simples para comunicação com a API do Trello.
- Aplicação de conceitos de backend e automação em um projeto prático.

## Status do projeto

O MeuSiteJá Discord Bot está funcional em estágio inicial. O foco atual é oferecer automações básicas para o servidor Discord do projeto MeuSiteJá e integração simples com Trello.

## Próximos passos

Possíveis melhorias futuras:

- Melhorar o tratamento de erros em respostas de APIs externas.
- Adicionar mensagens de retorno mais detalhadas para alguns fluxos.
- Tornar a estrutura inicial de cargos e canais mais fácil de personalizar.
- Expandir a documentação conforme o projeto evoluir.

## Segurança

Nunca exponha o token do Discord, a chave de API do Trello ou qualquer credencial sensível em commits, prints, issues ou mensagens públicas. Use o arquivo `.env` localmente e mantenha credenciais reais fora do repositório.

## Autoria

Projeto desenvolvido por [Vinicius Siqueira](https://github.com/vs-vinisiqueira) como parte do portfólio de desenvolvimento backend e automação.
