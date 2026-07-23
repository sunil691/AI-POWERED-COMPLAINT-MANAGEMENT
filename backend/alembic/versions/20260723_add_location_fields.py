"""Add customer_location, manufacturing_site, and likely_root_cause columns."""

from alembic import op
import sqlalchemy as sa


revision = "20260723_add_location_fields"
down_revision = "20260722_add_complaint_details"
branch_labels = None
depends_on = None


def upgrade() -> None:
	"""Add new fields to complaints table."""
	op.add_column("complaints", sa.Column("customer_location", sa.String(length=255), nullable=True))
	op.add_column("complaints", sa.Column("manufacturing_site", sa.String(length=255), nullable=True))
	op.add_column("complaints", sa.Column("likely_root_cause", sa.Text(), nullable=True))


def downgrade() -> None:
	"""Remove added columns."""
	op.drop_column("complaints", "likely_root_cause")
	op.drop_column("complaints", "manufacturing_site")
	op.drop_column("complaints", "customer_location")
