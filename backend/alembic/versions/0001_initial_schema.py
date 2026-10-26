"""initial schema

Baseline: the tables the app created with Base.metadata.create_all before Alembic.
Databases that already have these tables are stamped at this revision, not re-created
(see app/migrate.py).

Revision ID: 0001
Revises: 
Create Date: 2026-10-25 21:23:35.464191
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('Firms',
    sa.Column('cognito_sub', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('risk_tolerance', sa.String(), nullable=True),
    sa.Column('industry', sa.String(), nullable=True),
    sa.Column('years_active', sa.Integer(), nullable=True),
    sa.Column('num_investments', sa.Integer(), nullable=True),
    sa.Column('board_seat', sa.Boolean(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('investment_size', sa.Integer(), nullable=True),
    sa.Column('investment_stage', sa.String(), nullable=True),
    sa.Column('follow_on_rate', sa.Boolean(), nullable=True),
    sa.Column('rate_of_return', sa.String(), nullable=True),
    sa.Column('success_rate', sa.String(), nullable=True),
    sa.Column('reserved_capital', sa.String(), nullable=True),
    sa.Column('meeting_frequency', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('cognito_sub'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Investors',
    sa.Column('cognito_sub', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('risk_tolerance', sa.String(), nullable=True),
    sa.Column('industry', sa.String(), nullable=True),
    sa.Column('years_active', sa.Integer(), nullable=True),
    sa.Column('num_investments', sa.Integer(), nullable=True),
    sa.Column('board_seat', sa.Boolean(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('investment_size', sa.Integer(), nullable=True),
    sa.Column('investment_stage', sa.String(), nullable=True),
    sa.Column('follow_on_rate', sa.Boolean(), nullable=True),
    sa.Column('rate_of_return', sa.String(), nullable=True),
    sa.Column('success_rate', sa.String(), nullable=True),
    sa.Column('reserved_capital', sa.String(), nullable=True),
    sa.Column('meeting_frequency', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('cognito_sub'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )


def downgrade() -> None:
    op.drop_table('Investors')
    op.drop_table('Firms')
