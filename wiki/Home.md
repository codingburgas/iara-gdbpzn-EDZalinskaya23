# Fire Safety Management System (ГДПБЗН)

A learning web application that supports the daily operations of a fire and rescue
service: registering incidents, managing staff and vehicles, assigning teams,
distributing tasks and resources, and coordinating over live chat.

The interface is in Bulgarian; the code and documentation are in English.

## Quick links

- **[[Getting Started]]** — install and run the project locally.
- **[[Architecture]]** — how the application is put together.
- **[[Roles and Access]]** — who can do what.
- **[[Data Model]]** — the database tables and relationships.

## What it does

- **Public reporting** — a citizen submits an incident signal without logging in.
- **Dispatching** — the control room registers incidents (with a GPS point on a map)
  and assigns the nearest available team.
- **Coordination** — tasks, resource requests and per-incident chat keep the team in sync.
- **Operations channel** — a shared staff / control-room chat, separate from any incident.
- **Administration** — manage staff, roles and the vehicle fleet.

## Technology

Python 3 · Flask · SQLite · Jinja2 · vanilla JavaScript · Leaflet + OpenStreetMap.

## Demo accounts

All demo accounts use the password `1234`.

| Username | Role | Notes |
|----------|------|-------|
| `admin` | Administrator | Manage staff, vehicles and roles. |
| `dispatcher` | Dispatcher | Register incidents, assign teams, tasks, resources. |
| `<surname>` | Firefighter | Log in with the surname in lowercase Latin (e.g. `ivanov`). |

## Diagrams

The `docs/diagrams/` folder contains draw.io diagrams: architecture, incident flow,
roles and access, and the database ER diagram.
