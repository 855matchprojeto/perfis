"""empty message

Revision ID: 70464fb29418
Revises: d8a0df8e1216
Create Date: 2021-11-03 00:11:19.179037

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '70464fb29418'
down_revision = 'd8a0df8e1216'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tb_usuario',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('guid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('email_verificado', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('guid'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tb_usuario')
    # ### end Alembic commands ###
