# Factory Test 4

Built by The Factory. Product area `PA-0107`.

Code in this repository is generated from a requirement graph, not written by hand. Every change arrives as a pull request from a `work-item/...` branch carrying the identifiers of the work item that produced it, and a release arrives as a one-line change to `flags.json`.

See `RUNNING.md` for how to start it.

## Scaffold

`python-http-postgres@1` — Python 3.12 stdlib HTTP, PostgreSQL per service.

- one module per component, named for the resource it serves
- a BaseHTTPRequestHandler subclass and a serve(port) function
- JSON in and JSON out; the plumbing is provided and not to be changed
- records go through store.put/get/list; store.py is provided
- each service owns one database schema and touches no other (D-30)
- the schema arrives as numbered files in migrations/<service>/
