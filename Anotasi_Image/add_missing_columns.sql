-- Add missing columns to tables
ALTER TABLE master_segmentationtype ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE master_annotationtool ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Update existing records to have is_active = true
UPDATE master_segmentationtype SET is_active = TRUE WHERE is_active IS NULL;
UPDATE master_annotationtool SET is_active = TRUE WHERE is_active IS NULL;