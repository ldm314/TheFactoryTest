-- tags: schema version 0002, derived as the diff between what
-- the ledger says is deployed and what the requirements now imply (docs/11 §5).
--
-- Expand-phase only. Additive by construction, so its failure mode is the
-- migration not completing rather than the old code breaking — which is what
-- lets the expand phase precede the new code in production.

ALTER TABLE "svc_tags".records ADD COLUMN IF NOT EXISTS "label_existing_label_using_case_sensitive_exact_character_comparison" text;
ALTER TABLE "svc_tags".records ADD COLUMN IF NOT EXISTS "system_shall_respond_with_http_conflict" text;
ALTER TABLE "svc_tags".records ADD COLUMN IF NOT EXISTS "shall_create_tag" text;
