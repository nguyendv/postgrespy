db.py: a dead simple python ORM

## CHANGE LOGS
#### Version v0.4
BREAKING CHANGES:
- If you don't explicitly call `get_pool()`, some functions may not work.

#### Version v0.3
- Implement `get_pool()` function. Now you'll need to `get_pool()` to access a pool.

#### Version v0.2
- No longer use DATABASE_URL. Database parameters (host, port, user, password, etc.) must be provided in environment variables.
