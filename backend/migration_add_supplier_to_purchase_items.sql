-- Migration: Add supplier information to purchase_items
-- This allows each item in a purchase to have its own supplier

ALTER TABLE purchase_items 
ADD COLUMN supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
ADD COLUMN supplier_name VARCHAR(200);

-- Create index for performance
CREATE INDEX idx_purchase_items_supplier ON purchase_items(supplier_id);

-- Update existing records with supplier from their product
UPDATE purchase_items pi
SET 
    supplier_id = p.supplier_id,
    supplier_name = s.name
FROM products p
LEFT JOIN suppliers s ON p.supplier_id = s.id
WHERE pi.product_id = p.id;

COMMENT ON COLUMN purchase_items.supplier_id IS 'Reference to the supplier for this specific item';
COMMENT ON COLUMN purchase_items.supplier_name IS 'Cached supplier name for this item at time of purchase';
