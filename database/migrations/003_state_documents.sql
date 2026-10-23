-- ETHIO-CYBERGUARD: durable API state (incidents, SOAR actions, audit log).
-- The API creates this table automatically; this file is for manual/DBA setups.
CREATE TABLE IF NOT EXISTS state_documents (
    name        VARCHAR(64)  PRIMARY KEY,
    data        TEXT         NOT NULL,
    version     INTEGER      NOT NULL DEFAULT 1,
    updated_at  TIMESTAMPTZ  NOT NULL
);
