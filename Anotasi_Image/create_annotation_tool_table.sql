-- Create AnnotationTool table
CREATE TABLE IF NOT EXISTS master_annotationtool (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default annotation tools
INSERT INTO master_annotationtool (name, description, is_active) VALUES 
('Polygon Tool', 'Tool for creating polygon annotations', TRUE),
('Bounding Box Tool', 'Tool for creating bounding box annotations', TRUE),
('Point Tool', 'Tool for creating point annotations', TRUE)
ON CONFLICT (name) DO NOTHING;