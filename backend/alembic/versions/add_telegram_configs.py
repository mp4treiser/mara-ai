"""add telegram_configs table

Revision ID: add_telegram_configs
Revises: add_user_id_to_documents
Create Date: 2024-01-20 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_telegram_configs'
down_revision = 'add_user_id_to_documents'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу telegram_configs
    op.create_table(
        'telegram_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bot_token', sa.Text(), nullable=False),
        sa.Column('chat_id', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Добавляем внешние ключи
    op.create_foreign_key('fk_telegram_configs_agent_id', 'telegram_configs', 'agents', ['agent_id'], ['id'])
    op.create_foreign_key('fk_telegram_configs_user_id', 'telegram_configs', 'users', ['user_id'], ['id'])
    
    # Добавляем индексы
    op.create_index('ix_telegram_configs_agent_id', 'telegram_configs', ['agent_id'])
    op.create_index('ix_telegram_configs_user_id', 'telegram_configs', ['user_id'])
    op.create_index('ix_telegram_configs_is_active', 'telegram_configs', ['is_active'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_telegram_configs_is_active', table_name='telegram_configs')
    op.drop_index('ix_telegram_configs_user_id', table_name='telegram_configs')
    op.drop_index('ix_telegram_configs_agent_id', table_name='telegram_configs')
    
    # Удаляем внешние ключи
    op.drop_constraint('fk_telegram_configs_user_id', 'telegram_configs', type_='foreignkey')
    op.drop_constraint('fk_telegram_configs_agent_id', 'telegram_configs', type_='foreignkey')
    
    # Удаляем таблицу
    op.drop_table('telegram_configs')
