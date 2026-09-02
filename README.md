# Factory Test 4

Built by The Factory. Product area `PA-0107`.

Code in this repository is generated from a requirement graph, not written by hand. Every change arrives as a pull request from a `work-item/...` branch carrying the identifiers of the work item that produced it, and a release arrives as a one-line change to `flags.json`.

See `RUNNING.md` for how to start it.

## Scaffold

`python-fastapi-postgres@1` — FastAPI + uvicorn, PostgreSQL per service (default greenfield).

- one module per component, named for the resource it serves
- a FastAPI APIRouter named `router` and handler methods on Handler
- JSON in and JSON out; the plumbing is provided and not to be changed
- records go through store.put/get/list; store.py is provided
- each service owns one database schema and touches no other (D-30)
- the schema arrives as numbered files in migrations/<service>/
