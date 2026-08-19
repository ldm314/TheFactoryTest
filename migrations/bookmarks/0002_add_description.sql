-- bookmarks: schema version 0002, derived as the diff between what
-- the ledger says is deployed and what the requirements now imply (docs/11 §5).
--
-- Expand-phase only. Additive by construction, so its failure mode is the
-- migration not completing rather than the old code breaking — which is what
-- lets the expand phase precede the new code in production.

ALTER TABLE "svc_bookmarks".records ADD COLUMN IF NOT EXISTS "description" text;
