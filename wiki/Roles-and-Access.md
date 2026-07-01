# Roles and Access

Access is enforced by two decorators in `app/auth_utils.py`:

- `login_required` — the user must be authenticated.
- `role_required(*roles)` — the user must hold one of the listed roles.

## Roles

| Role | Login | Main capabilities |
|------|-------|-------------------|
| **Citizen** | No | Submit an incident report from the public page. |
| **Dispatcher** | Yes | Register incidents, view staff statuses, assign the team, create tasks, approve resource requests, change incident status, chat. |
| **Firefighter** | Yes | View own incidents and tasks, confirm participation, change own status (limited subset), per-incident chat, operations channel. |
| **Administrator** | Yes | Manage staff and vehicles, assign roles. |

## Notes

- Assigning a firefighter to an incident sets their status to "На произшествие";
  closing the incident returns the whole team to "Наличен".
- A firefighter may set only a safe subset of their own status ("Наличен", "Почивка").
- Passwords are stored as hashes; usernames are unique.

The visual version is in `docs/diagrams/roles-access.drawio`.
