-- Initialize things locally that aren't relevant in production.
CREATE USER "infini-gram" WITH PASSWORD 'llmz';

GRANT ALL ON schema public TO "infini-gram";