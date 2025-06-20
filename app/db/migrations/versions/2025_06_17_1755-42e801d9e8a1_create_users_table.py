"""create users table

Revision ID: 42e801d9e8a1
Revises:
Create Date: 2025-06-17 17:55:17.342332

"""
from typing import Sequence, Union

import fastapi_utils.guid_type
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '42e801d9e8a1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', fastapi_utils.guid_type.GUID(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=150), nullable=False),
    sa.Column('avatar_url', sa.String(length=200), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('pending_password_hash', sa.String(), nullable=True),
    sa.Column('password_change_token', sa.String(), nullable=True),
    sa.Column('password_change_token_expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('create_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email')),
    sa.UniqueConstraint('id', name=op.f('uq_users_id')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
