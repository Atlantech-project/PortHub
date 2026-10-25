# ATLANTECH Progress Tracker — online

Same tracker as the local HTML, but progress is stored on Cloudflare so everyone sees the same thing.

- **Anyone with the link** can view (statuses, notes, sprint ticks).
- **Editors** sign in with a personal key and can change statuses, add notes, tick hand-offs and set the current sprint.
- Every change is logged with its time, the editor's name and the current sprint at that moment:
  - **Activity** tab: every change, newest first, filterable by person.
  - Task dialog ("Notes"): the task's full status history.
  - Tasks table: time and editor of the last status change; a **Done late** flag when a task was finished after its planned sprint.
  - Blocked and late tab: how long each item has been in its state, plus a **Finished late** list.
  - Sprints tab: who ticked each hand-off / done-when item and when.
- Open pages refresh every 20 seconds.

## Files

| Path | What it is |
|---|---|
| `public/index.html` | The tracker page (your original page plus view/edit mode) |
| `src/worker.js` | Small API: `GET /api/state` and `GET /api/log` (public), `POST /api/op` (editors only) |
| `wrangler.jsonc` | Cloudflare config (Worker + D1 database) |

Storage is Cloudflare **D1** (free tier is plenty). The tables are created automatically on the first request.

## Deploy (one time)

> On Windows, put this folder on a short path (for example `E:\atlantech-tracker`). Wrangler fails with `ENAMETOOLONG` on very long paths.

```bash
npm install
npx wrangler login
npx wrangler d1 create atlantech-tracker
```

Copy the `database_id` it prints into `wrangler.jsonc` (the one there now is the live AtlanTech database).

Make one key per editor (run once per person):

```bash
node -e "console.log(require('crypto').randomBytes(12).toString('base64url'))"
```

Save the editors as a secret, in the form `Name:key,Name:key` (each key at least 8 characters):

```bash
npx wrangler secret put EDITORS
```

Deploy:

```bash
npx wrangler deploy
```

It prints the link, like `https://atlantech-tracker.<your-subdomain>.workers.dev`. Share it with everyone; send each editor their own key privately.

## Day-to-day

- Add or remove an editor, or change a key: run `npx wrangler secret put EDITORS` again with the full new list. Removed keys stop working immediately.
- Change the page (new tasks, wording): edit `public/index.html`, then `npx wrangler deploy`. Progress in D1 is kept.
- Backup: anyone can click **Export JSON** at any time.
- Custom domain (optional): Cloudflare dashboard → Workers → atlantech-tracker → Settings → Domains & Routes.

## Local test

Create `.dev.vars` with `EDITORS="Tester:local-test-key-123"`, then `npx wrangler dev` and open http://localhost:8787.
