-- SQL para agregar cliente_id y propio a la tabla campos
-- Ejecutar directamente en la base de datos MySQL

-- Agregar columna cliente_id si no existe
ALTER TABLE campos 
ADD COLUMN IF NOT EXISTS cliente_id INT NULL,
ADD INDEX IF NOT EXISTS idx_campos_cliente_id (cliente_id);

-- Agregar columna propio si no existe
ALTER TABLE campos 
ADD COLUMN IF NOT EXISTS propio TINYINT(1) NULL DEFAULT 1;

-- Nota: Si tu versión de MySQL no soporta IF NOT EXISTS, usar:
-- ALTER TABLE campos ADD COLUMN cliente_id INT NULL;
-- ALTER TABLE campos ADD INDEX idx_campos_cliente_id (cliente_id);
-- ALTER TABLE campos ADD COLUMN propio TINYINT(1) NULL DEFAULT 1;
