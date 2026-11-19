#!/bin/sh
set -e
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
     -v app_pw="$APP_DB_PASSWORD" -v db="$POSTGRES_DB" <<'EOSQL'
CREATE ROLE breach_app LOGIN PASSWORD :'app_pw';
GRANT CONNECT ON DATABASE :"db" TO breach_app;
GRANT SELECT ON leaked_hashes TO breach_app;
EOSQL
