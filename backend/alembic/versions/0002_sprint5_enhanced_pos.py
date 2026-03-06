"""Sprint 5 — Enhanced Retail POS tables + column additions

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- Column additions to existing tables ----

    # customers
    op.add_column('customers', sa.Column('credit_limit', sa.DECIMAL(15, 2), server_default='0'))
    op.add_column('customers', sa.Column('loyalty_points', sa.Integer(), server_default='0'))

    # products
    op.add_column('products', sa.Column('has_variants', sa.Boolean(), server_default='false'))
    op.add_column('products', sa.Column('reorder_point', sa.Integer(), server_default='0'))

    # sales
    op.add_column('sales', sa.Column('tax_rate', sa.DECIMAL(5, 2), server_default='14'))
    op.add_column('sales', sa.Column('tax_amount', sa.DECIMAL(15, 2), server_default='0'))
    op.add_column('sales', sa.Column('is_held', sa.Boolean(), server_default='false'))
    op.add_column('sales', sa.Column('held_name', sa.String(100), nullable=True))
    op.add_column('sales', sa.Column('shift_id', sa.Integer(), nullable=True))

    # sale_items
    op.add_column('sale_items', sa.Column('variant_id', sa.Integer(), nullable=True))
    op.add_column('sale_items', sa.Column('variant_label', sa.String(200), nullable=True))
    op.add_column('sale_items', sa.Column('tax_amount', sa.DECIMAL(15, 2), server_default='0'))

    # ---- New tables ----

    op.create_table(
        'product_variants',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('sku', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('weight', sa.String(50), nullable=True),
        sa.Column('purchase_price', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('sale_price', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('quantity', sa.Integer(), server_default='0'),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
    )

    op.create_table(
        'sale_payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('payment_method', sa.String(30), nullable=False),
        sa.Column('amount', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('reference_no', sa.String(100), nullable=True),
    )

    op.create_table(
        'sale_returns',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('return_no', sa.String(20), unique=True, nullable=False),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=True),
        sa.Column('return_date', sa.Date(), nullable=False),
        sa.Column('subtotal', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('tax_amount', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('total', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('refund_method', sa.String(30), server_default="'cash'"),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default="'pending'"),
        sa.Column('restock', sa.Boolean(), server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'sale_return_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('return_id', sa.Integer(), sa.ForeignKey('sale_returns.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('reason', sa.String(200), nullable=True),
    )

    op.create_table(
        'installments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('installment_no', sa.Integer(), nullable=False),
        sa.Column('amount', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('paid_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), server_default="'pending'"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'shifts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('opening_balance', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('closing_balance', sa.DECIMAL(15, 2), nullable=True),
        sa.Column('expected_balance', sa.DECIMAL(15, 2), nullable=True),
        sa.Column('variance', sa.DECIMAL(15, 2), nullable=True),
        sa.Column('total_sales', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('total_returns', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('total_cash_in', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('total_cash_out', sa.DECIMAL(15, 2), server_default='0'),
        sa.Column('status', sa.String(20), server_default="'open'"),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    op.create_table(
        'cash_drawer_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('amount', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('reason', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'product_batches',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('batch_no', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer(), server_default='0'),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'stocktakes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('reference', sa.String(30), unique=True, nullable=False),
        sa.Column('status', sa.String(20), server_default="'in_progress'"),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'stocktake_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('stocktake_id', sa.Integer(), sa.ForeignKey('stocktakes.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('system_quantity', sa.Integer(), nullable=False),
        sa.Column('counted_quantity', sa.Integer(), nullable=True),
        sa.Column('variance', sa.Integer(), nullable=True),
    )

    op.create_table(
        'einvoices',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), unique=True, nullable=False),
        sa.Column('internal_id', sa.String(50), unique=True, nullable=False),
        sa.Column('eta_uuid', sa.String(100), nullable=True),
        sa.Column('submission_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(30), server_default="'draft'"),
        sa.Column('qr_code_data', sa.Text(), nullable=True),
        sa.Column('raw_response', sa.Text(), nullable=True),
    )

    # FK for sales.shift_id
    op.create_foreign_key('fk_sales_shift_id', 'sales', 'shifts', ['shift_id'], ['id'])
    # FK for sale_items.variant_id
    op.create_foreign_key('fk_sale_items_variant_id', 'sale_items', 'product_variants', ['variant_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_sale_items_variant_id', 'sale_items', type_='foreignkey')
    op.drop_constraint('fk_sales_shift_id', 'sales', type_='foreignkey')

    op.drop_table('einvoices')
    op.drop_table('stocktake_items')
    op.drop_table('stocktakes')
    op.drop_table('product_batches')
    op.drop_table('cash_drawer_logs')
    op.drop_table('shifts')
    op.drop_table('installments')
    op.drop_table('sale_return_items')
    op.drop_table('sale_returns')
    op.drop_table('sale_payments')
    op.drop_table('product_variants')

    op.drop_column('sale_items', 'tax_amount')
    op.drop_column('sale_items', 'variant_label')
    op.drop_column('sale_items', 'variant_id')

    op.drop_column('sales', 'shift_id')
    op.drop_column('sales', 'held_name')
    op.drop_column('sales', 'is_held')
    op.drop_column('sales', 'tax_amount')
    op.drop_column('sales', 'tax_rate')

    op.drop_column('products', 'reorder_point')
    op.drop_column('products', 'has_variants')

    op.drop_column('customers', 'loyalty_points')
    op.drop_column('customers', 'credit_limit')
