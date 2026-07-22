"""Create initial complaints, chat_messages, and uploaded_documents tables."""

from alembic import op
import sqlalchemy as sa


revision = "00000000_create_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the base tables the application models describe."""
    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("complaint_number", sa.String(length=64), nullable=False, unique=True),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("dosage_strength", sa.String(length=100), nullable=True),
        sa.Column("dosage_unit", sa.String(length=50), nullable=True),
        sa.Column("batch_number", sa.String(length=100), nullable=True),
        sa.Column("originating_site", sa.String(length=255), nullable=True),
        sa.Column("impacted_material", sa.String(length=255), nullable=True),
        sa.Column("complaint_category", sa.String(length=100), nullable=True),
        sa.Column("complaint_description", sa.Text(), nullable=True),
        sa.Column("structured_summary", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=50), nullable=True),
        sa.Column("risk_assessment", sa.Text(), nullable=True),
        sa.Column("suggested_next_action", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_complaints_status", "complaints", ["status"])
    op.create_index("ix_complaints_complaint_number", "complaints", ["complaint_number"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "complaint_id",
            sa.Integer(),
            sa.ForeignKey("complaints.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_chat_messages_complaint_id", "chat_messages", ["complaint_id"])

    op.create_table(
        "uploaded_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "complaint_id",
            sa.Integer(),
            sa.ForeignKey("complaints.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_uploaded_documents_complaint_id", "uploaded_documents", ["complaint_id"])


def downgrade() -> None:
    """Drop all base tables."""
    op.drop_table("uploaded_documents")
    op.drop_table("chat_messages")
    op.drop_index("ix_complaints_complaint_number", table_name="complaints")
    op.drop_index("ix_complaints_status", table_name="complaints")
    op.drop_table("complaints")
