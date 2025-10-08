-- Script para adicionar colunas de reposição na tabela if_tbl_registro_higiene
-- Execute este script no Oracle Database

ALTER TABLE if_tbl_registro_higiene ADD (
    PAPEL_HIG VARCHAR2(2),
    PAPEL_TOALHA VARCHAR2(2),
    ALCOOL VARCHAR2(2),
    SABONETE VARCHAR2(2)
);

-- Comentários das colunas
COMMENT ON COLUMN if_tbl_registro_higiene.PAPEL_HIG IS 'Reposição de Papel Higiênico (S/N)';
COMMENT ON COLUMN if_tbl_registro_higiene.PAPEL_TOALHA IS 'Reposição de Papel Toalha (S/N)';
COMMENT ON COLUMN if_tbl_registro_higiene.ALCOOL IS 'Reposição de Álcool (S/N)';
COMMENT ON COLUMN if_tbl_registro_higiene.SABONETE IS 'Reposição de Sabonete (S/N)';
