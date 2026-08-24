# Royal Tunbridge Wells Greenspace

## Repo structure

- `pre-processing/` — Python preprocessing scripts. Includes the OS Built-Up Areas 2022 shapefile.
- `model/` — react-three-fiber viewer, Vite planned. Not yet committed/tracked.

## Working conventions

- `git push` always requires explicit user confirmation, in every permission mode (enforced via `.claude/settings.json`: `permissions.ask` on `git push*`, and `disableBypassPermissionsMode` so bypass mode can't be used to skip it).
- This repo is developed both from this web session and from a devcontainer/Codespace running the `claude` CLI directly. The two do not share conversation history — treat them as separate sessions working on the same repo.
