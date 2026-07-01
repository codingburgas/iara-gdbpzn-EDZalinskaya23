# Data Model

The database contains ten tables. The authoritative definition is in
`database/schema.sql`; the visual model is in `docs/diagrams/er-diagram.drawio`.

| Table | Purpose | Key references |
|-------|---------|----------------|
| `vehicles` | Fire vehicles. | — |
| `users` | Staff accounts and status. | `vehicle_id → vehicles` |
| `incidents` | Registered incidents. | `created_by → users` |
| `incident_assignments` | Staff assigned to an incident (the team). | `incident_id → incidents`, `user_id → users` |
| `tasks` | Tasks within an incident. | `incident_id → incidents`, `assigned_to → users` |
| `resource_requests` | Resource requests within an incident. | `incident_id → incidents`, `requested_by → users` |
| `messages` | Per-incident chat messages. | `incident_id → incidents`, `user_id → users` |
| `message_templates` | Ready-made chat replies. | — (standalone) |
| `ops_messages` | Operations-channel messages. | `user_id → users` |
| `chat_reads` | "Seen" receipts per channel and user. | `user_id` references `users` (logical) |

## Referential rules

- **Cascade:** assignments, tasks, resources and messages are deleted together with
  their incident (`ON DELETE CASCADE`).
- **Set null:** user references on incidents, tasks, resources and messages are nulled
  when a user is removed (`ON DELETE SET NULL`).

## Status vocabularies

- **Incident status:** Нова → В процес → Приключена
- **Task status:** Нова → В процес → Приключена
- **Resource status:** Заявена → Одобрена → Доставена
- **Incident channel:** 112 · Онлайн · Телефон
- **Staff status:** Наличен · Почивка · На произшествие · Отпуск · Болничен · Командировка
