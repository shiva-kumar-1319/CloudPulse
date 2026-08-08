-- Initialize separate databases for Database-Per-Service architecture
CREATE DATABASE order_db;
CREATE DATABASE inventory_db;

GRANT ALL PRIVILEGES ON DATABASE auth_db TO cloudpulse;
GRANT ALL PRIVILEGES ON DATABASE order_db TO cloudpulse;
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO cloudpulse;
