# Visão geral da arquitetura

A arquitetura do back-end será definida em microsserviços. Ao contrário de uma arquitetura convencional monolítica, a aplicação em microsserviços é desmembrada em partes menores e independentes entre si.

Ao fazer o login pelo autenticador, o usuário receberá um token de acesso, com um tempo de expiração bem definido. No token, estarão disponíveis informações como 'username', 'email' e as funções desse usuário no sistema. Ao se comunicar com outros microsserviços, será necessário um header de autenticação, contendo esse token. Cada microsserviço será responsável por descriptografar e validar o token. 

Apesar do microsserviço de autenticação ser responsável pela criação de usuários e suas funções, cada microsserviço implementará seu próprio sistema de permissões, com base nas funções do usuário que fez a requisição. Note que as funções do usuário estarão disponíveis no token de acesso decodificado.

# Descrição

O microsserviço de autenticação é responsável pela implementação do serviço de identificação de usuários. Além disso, são definidos tabelas para o banco de dados, tais como usuário, função e vínculo de usuários com funções. Como supracitado, o autenticador também definirá tabelas de permissões, específicas para esse microsserviço.

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
