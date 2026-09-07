-- Fase 0B.1 — lock down public.rls_auto_enable()
--
-- Context: public.rls_auto_enable() is SECURITY DEFINER and currently has the
-- default EXECUTE grant to PUBLIC, so anon and authenticated (which inherit
-- from PUBLIC) can invoke it directly through the Data API / RPC. It also
-- backs the `ensure_rls` event trigger. The event trigger keeps working after
-- this migration: event triggers are dispatched by the server on
-- ddl_command_end and do not go through the function-level EXECUTE ACL, and a
-- SECURITY DEFINER function always runs as its owner regardless of caller.
--
-- Effect: only the function owner (postgres) can call it explicitly.
-- Reversible: re-GRANT EXECUTE ... TO public; (not recommended).
--
-- Apply:  supabase db push   (or paste into the SQL editor)
-- Verify: the \df+ output shows "Access privileges" without anon/authenticated;
--         `select public.rls_auto_enable();` as anon -> permission denied;
--         create a throwaway table in public and confirm RLS is still auto-on.

do $$
declare
  fn text;
begin
  for fn in
    select p.oid::regprocedure::text
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname = 'rls_auto_enable'
  loop
    execute format('revoke execute on function %s from public', fn);
    execute format('revoke execute on function %s from anon', fn);
    execute format('revoke execute on function %s from authenticated', fn);
    execute format('grant  execute on function %s to postgres', fn);
    raise notice 'locked down %', fn;
  end loop;
end
$$;

-- Optional belt-and-suspenders: stop the default grant from coming back for
-- any *future* function created in public by the migration/owner role.
-- Leave commented unless the team wants this repo-wide policy.
-- alter default privileges in schema public revoke execute on functions from public;
