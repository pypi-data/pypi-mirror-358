"""Create keywords association table

Revision ID: 002
Revises: 001
Create Date: 2025-01-18

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "memory_keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("memory_key", sa.String(255), nullable=False),
        sa.Column("keyword", sa.String(100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.current_timestamp()
        ),
        sa.ForeignKeyConstraint(
            ["memory_key"],
            ["memories.key"],
            name="fk_memory_keywords_memory_key",
            ondelete="CASCADE",
        ),
    )

    # Indexes for efficient lookups
    op.create_index("idx_memory_keywords_memory_key", "memory_keywords", ["memory_key"])
    op.create_index("idx_memory_keywords_keyword", "memory_keywords", ["keyword"])
    op.create_index(
        "idx_memory_keywords_key_keyword", "memory_keywords", ["memory_key", "keyword"]
    )


def downgrade() -> None:
    op.drop_index("idx_memory_keywords_key_keyword", "memory_keywords")
    op.drop_index("idx_memory_keywords_keyword", "memory_keywords")
    op.drop_index("idx_memory_keywords_memory_key", "memory_keywords")
    op.drop_table("memory_keywords")
