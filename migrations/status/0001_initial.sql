-- status: initial schema, derived from the requirement (docs/11 §4).
--
-- Expand-phase and additive: every statement is IF NOT EXISTS, so re-applying
-- this file to a database already at this version changes nothing. That is not
-- politeness — it is the property the migration check measures.

CREATE SCHEMA IF NOT EXISTS "svc_status";

CREATE SEQUENCE IF NOT EXISTS "svc_status".record_id AS bigint START 1;

CREATE TABLE IF NOT EXISTS "svc_status".records (
    "id" text PRIMARY KEY,
    "owner" text NOT NULL DEFAULT '',
    "body" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "non_existent" text,
    "system_shall_status_code_currently" text
);

CREATE INDEX IF NOT EXISTS records_owner_idx
    ON "svc_status".records (owner);
