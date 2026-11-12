-- Curso 4 Laboratorio 2: atomic JSONB updates for pre-existing progress rows.
-- Apply in the Supabase project ACTUALLY used by laboratoriodeacustica.
-- SQL Editor > New query. Non-destructive: never truncates progress.
--
-- This function is NOT currently included in the original database schema.
-- Deployment is separate from merging GitHub code. The app also supports
-- isolated verified Stage 6 recovery checkpoints if this RPC is unavailable.

create or replace function public.patch_c4l2_progress(
    p_class_id text,
    p_user_key text,
    p_changes jsonb
)
returns boolean
language plpgsql
security invoker
set search_path = public
as $$
declare
    v_affected integer;
begin
    if p_class_id is null or length(trim(p_class_id)) = 0
       or p_user_key is null or length(trim(p_user_key)) = 0 then
        raise exception 'class_id/user_key required';
    end if;
    if p_changes is null or jsonb_typeof(p_changes) <> 'object' then
        raise exception 'p_changes must be a JSON object';
    end if;
    update public.user_progress
       set state_json = coalesce(state_json, '{}'::jsonb) || p_changes,
           updated_at = now()
     where class_id = p_class_id
       and user_key = p_user_key;
    get diagnostics v_affected = row_count;
    return v_affected = 1;
end;
$$;

-- Never expose a service-key-only progress function to public clients.
revoke all on function public.patch_c4l2_progress(text,text,jsonb)
    from public, anon, authenticated;
grant execute on function public.patch_c4l2_progress(text,text,jsonb)
    to service_role;

-- Refresh the PostgREST function signature cache.
notify pgrst, 'reload schema';

-- Safe non-mutating check:
-- select proname, pg_get_function_identity_arguments(oid)
-- from pg_proc where proname='patch_c4l2_progress';
