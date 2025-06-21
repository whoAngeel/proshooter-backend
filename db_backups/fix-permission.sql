-- fix-permissions.sql
-- Este script asegura que el usuario admin sea propietario de todos los objetos

DO $$
DECLARE
    r RECORD;
BEGIN
    -- Cambiar propietario de todas las tablas
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' OWNER TO admin';
    END LOOP;

    -- Cambiar propietario de todas las secuencias
    FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'
    LOOP
        EXECUTE 'ALTER SEQUENCE public.' || quote_ident(r.sequence_name) || ' OWNER TO admin';
    END LOOP;

    -- Cambiar propietario de todos los tipos personalizados
    FOR r IN SELECT typname FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE n.nspname = 'public' AND t.typtype = 'e'
    LOOP
        EXECUTE 'ALTER TYPE public.' || quote_ident(r.typname) || ' OWNER TO admin';
    END LOOP;
END $$;
