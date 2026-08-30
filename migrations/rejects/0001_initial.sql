-- rejects: initial schema, derived from the requirement (docs/11 §4).
--
-- Expand-phase and additive: every statement is IF NOT EXISTS, so re-applying
-- this file to a database already at this version changes nothing. That is not
-- politeness — it is the property the migration check measures.

CREATE SCHEMA IF NOT EXISTS "svc_rejects";

CREATE SEQUENCE IF NOT EXISTS "svc_rejects".record_id AS bigint START 1;

CREATE TABLE IF NOT EXISTS "svc_rejects".records (
    "id" text PRIMARY KEY,
    "owner" text NOT NULL DEFAULT '',
    "body" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "same_label_already_exists_system_identifier_generation_process_may_not_guarantee_attempted_submission_receives_unique_currently_convergence_budget_cycle_exhausted_after_cycle" text
);

CREATE INDEX IF NOT EXISTS records_owner_idx
    ON "svc_rejects".records (owner);
