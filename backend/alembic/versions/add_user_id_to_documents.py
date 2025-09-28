"""add user_id to documents

Revision ID: add_user_id_to_documents
Revises: 79e78b83ff1c
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_id_to_documents'
down_revision = '79e78b83ff1c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Сначала добавляем поле user_id как nullable
    op.add_column('documents', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Получаем connection для выполнения SQL
    connection = op.get_bind()
    
    # Получаем первого пользователя (или создаем дефолтного)
    result = connection.execute(sa.text("SELECT id FROM users LIMIT 1"))
    first_user_id = result.fetchone()
    
    if first_user_id:
        # Присваиваем всем существующим документам первого пользователя
        connection.execute(
            sa.text("UPDATE documents SET user_id = :user_id WHERE user_id IS NULL"),
            {"user_id": first_user_id[0]}
        )
    else:
        # Если пользователей нет, создаем дефолтного
        connection.execute(
            sa.text("""
                INSERT INTO users (email, username, hashed_password, is_active, is_verified, balance, created_at, updated_at)
                VALUES ('default@example.com', 'default_user', 'default_password', true, true, 0.0, NOW(), NOW())
            """)
        )
        result = connection.execute(sa.text("SELECT id FROM users WHERE email = 'default@example.com'"))
        default_user_id = result.fetchone()[0]
        
        connection.execute(
            sa.text("UPDATE documents SET user_id = :user_id WHERE user_id IS NULL"),
            {"user_id": default_user_id}
        )
    
    # Теперь делаем поле NOT NULL
    op.alter_column('documents', 'user_id', nullable=False)
    
    # Создаем внешний ключ
    op.create_foreign_key('fk_documents_user_id', 'documents', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Удаляем внешний ключ и поле user_id
    op.drop_constraint('fk_documents_user_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'user_id')
