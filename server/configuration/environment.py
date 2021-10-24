import re
import pathlib
from pydantic import BaseSettings, EmailStr, Field


class Environment(BaseSettings):

    # Configurações do banco de dados

    DB_ECHO: bool = True
    DB_POOL_SIZE: int = 80
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    DATABASE_URL: str

    # Configurações do servidor

    ENVIRONMENT: str = 'DEV'
    HOST: str = 'localhost'
    PORT: int = 8080

    ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS: int = 1800
    MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS: int = 600

    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ALGORITHM: str

    CURSOR_TOKEN_SECRET_KEY: str
    CURSOR_TOKEN_ALGORITHM: str

    @staticmethod
    def get_db_conn_async(database_url: str):
        return re.sub(r'\bpostgres://\b', "postgresql+asyncpg://", database_url, count=1)

    @staticmethod
    def get_db_conn_default(database_url: str):
        return re.sub(r'\bpostgres://\b', "postgresql://", database_url, count=1)

    class Config:
        env_file = '.env/PERFIS.env'
        env_file_encoding = 'utf-8'


class IntegrationTestEnvironment(BaseSettings):

    TEST_DB_HOST = "localhost"
    TEST_DB_USER: str = "postgres"
    TEST_DB_PASS: str = '1234'
    TEST_DB_NAME: str = 'postgres'
    TEST_DB_PORT: str = '5432'

    @staticmethod
    def get_db_conn_default(db_host: str, db_user: str, db_pass: str,
                            db_name: str, db_port: str):
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    @staticmethod
    def get_db_conn_async(db_host: str, db_user: str, db_pass: str,
                          db_name: str, db_port: str):
        return f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    class Config:
        env_file = '.env/PERFIS_TEST.env'
        env_file_encoding = 'utf-8'


class MigrationEnvironment(BaseSettings):

    MIGRATION_DB_HOST = "localhost"
    MIGRATION_DB_USER: str = "postgres"
    MIGRATION_DB_PASS: str = '1234'
    MIGRATION_DB_NAME: str = 'postgres'
    MIGRATION_DB_PORT: str = '5432'

    @staticmethod
    def get_db_conn_default(db_host: str, db_user: str, db_pass: str,
                            db_name: str, db_port: str):
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    @staticmethod
    def get_db_conn_async(db_host: str, db_user: str, db_pass: str,
                          db_name: str, db_port: str):
        return f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    class Config:
        env_file = '.env/PERFIS_MIGRATION.env'
        env_file_encoding = 'utf-8'


class AuthEnvironment(BaseSettings):
    """
        Classe criada para separar a dependência de autenticação das demais
        Sem ela, teriamos que ter várias variáveis de ambiente nos testes sem necessidade
    """

    AUTHENTICATOR_DNS: str

    class Config:
        env_file = '.env/PERFIS_AUTH.env'
        env_file_encoding = 'utf-8'

