"""empty message

Revision ID: 2052028b50fb
Revises: 23fff556207e
Create Date: 2021-10-23 22:44:18.198628

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2052028b50fb'
down_revision = '23fff556207e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tb_curso',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('nome_referencia', sa.String(), nullable=False),
    sa.Column('nome_exibicao', sa.String(), nullable=False),
    sa.Column('descricao', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome_exibicao'),
    sa.UniqueConstraint('nome_referencia')
    )
    op.create_table('tb_interesse',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('nome_referencia', sa.String(), nullable=False),
    sa.Column('nome_exibicao', sa.String(), nullable=False),
    sa.Column('descricao', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome_exibicao'),
    sa.UniqueConstraint('nome_referencia')
    )
    op.create_table('tb_perfil_email',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('id_perfil', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_tipo_contato',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('nome_referencia', sa.String(), nullable=False),
    sa.Column('nome_exibicao', sa.String(), nullable=False),
    sa.Column('descricao', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome_exibicao'),
    sa.UniqueConstraint('nome_referencia')
    )
    op.create_table('tb_perfil_phone',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('id_perfil', sa.BigInteger(), nullable=False),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('id_tipo_contato', sa.BigInteger(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id_tipo_contato'], ['tb_tipo_contato.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_perfil',
    sa.Column('guid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('guid_usuario', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('bio', sa.String(), nullable=True),
    sa.Column('nome_exibicao', sa.String(), nullable=True),
    sa.Column('id_entidade_email', sa.BigInteger(), nullable=True),
    sa.Column('id_entidade_phone', sa.BigInteger(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id_entidade_email'], ['tb_perfil_email.id'], ),
    sa.ForeignKeyConstraint(['id_entidade_phone'], ['tb_perfil_phone.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('guid'),
    sa.UniqueConstraint('guid_usuario')
    )
    op.create_table('tb_vinculo_perfil_curso',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('id_perfil', sa.BigInteger(), nullable=True),
    sa.Column('id_curso', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['id_curso'], ['tb_curso.id'], ),
    sa.ForeignKeyConstraint(['id_perfil'], ['tb_perfil.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_perfil', 'id_curso')
    )
    op.create_table('tb_vinculo_perfil_interesse',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('id_perfil', sa.BigInteger(), nullable=True),
    sa.Column('id_interesse', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['id_interesse'], ['tb_interesse.id'], ),
    sa.ForeignKeyConstraint(['id_perfil'], ['tb_perfil.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_perfil', 'id_interesse')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tb_vinculo_perfil_interesse')
    op.drop_table('tb_vinculo_perfil_curso')
    op.drop_table('tb_perfil')
    op.drop_table('tb_perfil_phone')
    op.drop_table('tb_tipo_contato')
    op.drop_table('tb_perfil_email')
    op.drop_table('tb_interesse')
    op.drop_table('tb_curso')
    # ### end Alembic commands ###
