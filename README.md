# Universidade Estadual de Campinas
# Instituto da Computação

## Disciplina: MC855-2s2021

#### Professor e Assistente

| Nome                     | Email                   |
| ------------------------ | ------------------------|
| Professora Juliana Borin | jufborin@unicamp.br     |
| Assistente Paulo Kussler | paulo.kussler@gmail.com |


#### Equipe

| Nome               | RA               | Email                  | ID Git                |
| ------------------ | ---------------- | ---------------------- |---------------------- |
| Gustavo Henrique Libraiz Teixeira                   | 198537                 | g198537@dac.unicamp.br                     |   nugnu                    |
| Lucas Henrique Machado Domingues                   | 182557                 | l182557@dac.unicamp.br                    |   lhmdomingues                   ||                    |                  |                        |                       |
| Matheus Vicente Mazon                   | 203609                | m203609@dac.unicamp.br                     |   matheusmazon                    |
| Pietro Pugliesi                   | 185921               | p185921@dac.unicamp.br                     |   pietro1704                   |
| Caio Lucas Silveira de Sousa                  | 165461                | c165461@dac.unicamp.br                     |   caiolucasw                    |
| Thomas Gomes Ferreira                  | 224919                | t224919@dac.unicamp.br                     |   Desnord                   |


## Específico sobre esse repositório: 
Esse repositório faz parte do projetos da plataforma de Match de Projetos desenvolvido no 2s/2021 para a disciplina MC-855 na Unicamp (https://github.com/orgs/855matchprojeto/repositories). Neste repositório se encontra a implementação do microsserviço de perfis dos usuários para o projeto.

# Visão geral da arquitetura

A arquitetura do back-end será definida em microsserviços. Ao contrário de uma arquitetura convencional monolítica, a aplicação em microsserviços é desmembrada em partes menores e independentes entre si.

Ao fazer o login pelo autenticador, o usuário receberá um token de acesso, com um tempo de expiração bem definido. No token, estarão disponíveis informações como 'username', 'email' e as funções desse usuário no sistema. Ao se comunicar com outros microsserviços, será necessário um header de autenticação, contendo esse token. Cada microsserviço será responsável por descriptografar e validar o token. 

Apesar do microsserviço de autenticação ser responsável pela criação de usuários e suas funções, cada microsserviço implementará seu próprio sistema de permissões, com base nas funções do usuário que fez a requisição. Note que as funções do usuário estarão disponíveis no token de acesso decodificado.

# Descrição desse repositório

O microserviço de perfis é responsável pela atualização de perfis de um usuário, alterando campos específicos do perfil ou vinculando novas entidades. Foram implementadas as seguintes features:

- Paginação baseada em cursores e filtros:
    - Filtros com nome normalizado
    - Filtros a partir de cursos
    - FIltros a partir de interesses 
- Entidade de "Curso" e vínculo do perfil com curso
- Entidade de "Interesse" e vínculo do perfil com interesse
- Entidade de "Contato" e vínculo do perfil com contato

Note que é possível fazer o POST de um perfil, mas não é necessário. Há um código no repositório "adapters", que trata mensagens SQS. Ao criar um usuário, o serviço de autenticação manda uma mensagem SQS que é tratada pelo serviço de adapter. O adapter, por sua vez, cria um perfil "zerado" para o usuário criado, de forma automática.

# Aspectos Técnicos

## FAST-API

Os microsserviços serão implementados utilizando o framework web FAST-API. É um framework baseado no módulo de type-hints do python. A partir dos type-hints, o framework realiza a documentação de maneira automática, definindo inputs e outputs de um endpoint. 

O FAST-API implementa a especificação ASGI (Asynchronous Server Gateway Interface), que provê um padrão assíncrono (e também um padrão síncrono) para implementação de aplicativos em python. Nesse projeto, utilizaremos a funcionalidade assíncrona do FAST-API em nosso favor, principalmente ao requisitar o banco de dados.

## SQL-Alchemy

O SQL-Alchemy é uma biblioteca em python, com o objetivo de facilitar a comunicação entre programas e python com um banco de dados relacional. 

Nesse projeto, utilizaremos o ORM (Object Relational Mapper) do SQL-Alchemy, conectando a um banco de dados PostgreSQL. Um ORM é uma ferramenta capaz de traduzir classes do python em tabelas. Além disso, funções em python podem representar queries e statements.

Além disso, o ORM provê uma flexibilidade de tecnologias de banco de dados. A tradução, citada anteriormente, é realizada de maneira similar nos bancos de dados que o SQL-Alchemy implementa. Por exemplo, se houver necessidade de alterar a tecnologia de banco de dados PostgreSQL vigente para outra, como MySQL, não haverá muitos problemas.

## Alembic

O Alembic é uma ferramenta de migração de dados, que funciona a partir da 'engine' disponível no SQL-Alchemy. O Alembic se conecta à um banco de dados e define um versionamento 'alembic_version'. A partir do 'metadata' do banco de dados criado no projeto, o Alembic é capaz de verificar se foram implementadas alterações nas classes que definem os modelos do banco de dados. Caso requisitado pelo programador, o Alembic pode gerar um script de revisão, com as alterações necessárias no banco de dados. Ao executar esse script, o banco de dados é atualizado.

Podemos citar algumas funcionalidades importantes no CLI do Alembic:

- alembic init: Gera os templates necessários para o funcionamento do Alembic. Algumas informações devem ser preenchidas no template, como a conexão com o banco de dados
- alembic revision --autogenerate: Gera o arquivo de revisão explicado anteriormente. Note que a revisão pode não ser perfeita. Sempre verifique os scripts de revisão gerados e os corrige se necessário.
- alembic upgrade head: Atualiza o banco de dados para a última versão definida pelo Alembic.
- alembic upgrade {revision}: Atualiza o banco de dados para a versão definida em 'revision'. Esse campo está disponível nos scripts de revisão gerados, na variável 'revision'.
- alembic downgrade -1: Desfaz a última alteração definida pelo alembic
- alembic downgrade {revision}: Desfaz as últimas alterações definidas pelo alembic, até que se retorna à versão definida por {revision}.

## Estrutura do código

### configuration

Essa pasta é responsável por definir módulos responsáveis por: 

- Conexão com o banco de dados assíncrono
- Variáveis de ambiente
- Exceções customizadas
- Constantes
- Logging

### controllers

Essa pasta é responsável por definir a primeira camada de acesso aos endpoints. Nela são definidos:

- Rotas
- Paths dos endpoitns
- Dependências
- Decorator para tratar exceções com rollback do banco de dados

### services

Define a lógica dos endpoints, abstraindo o acesso ao banco de dados, que é efetuado pelos módulos definidos na pastas repository

### repository

Define os métodos que atuam diretamente com banco de dados

### dependencies

Define as injeções de dependência utilizadas pelos controllers. Pode-se citar:

- Dependências de segurança, como o Form do OAuth2
- Sessão do banco de dados assícrono

### models

Define as classes que representam o banco de dados, suas tabelas e campos

### schemas

Essa classe é necessária para definir inputs e outputs de endpoints, permitindo a documentação automática do FAST-API.
