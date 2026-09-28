# POL VPS Deployment Agent Runbook

This directory defines the safe execution contract for an AI agent or operator that deploys POL to the self-hosted VPS.

## Canonical command

From the repository root:

```bash
bash deploy/vps_deploy.sh
```

Optional public verification:

```bash
POL_PUBLIC_BASE_URL=http://85.198.50.29 bash deploy/vps_deploy.sh
```

## What the agent does

1. Acquires a deployment lock so two deployments cannot run concurrently.
2. Fetches the exact authorized deployment branch.
3. Checks out the branch and verifies local HEAD equals the remote HEAD.
4. Validates required non-secret environment keys without printing their values.
5. Validates Docker Compose configuration.
6. Builds all deployment images.
7. Starts PostgreSQL and waits for a healthy state.
8. Runs the forward-only production migration runner.
9. Starts API, worker, web, and Nginx.
10. Verifies local health, readiness, and web routing.
11. Optionally verifies the public base URL.
12. Records a deployment log under `deploy/logs/`.

## Safety contract

The agent MUST NOT automatically:

- run `scripts/bootstrap_env.py --reset`
- run the destructive reset path in `scripts/migration_runner.py`
- use `pol_test`
- remove the `pol_pgdata` volume
- run `docker compose down -v`
- rotate production secrets on every deployment
- expose or echo secret values

A PostgreSQL startup failure is treated as a blocking infrastructure error. The agent should inspect logs and stop rather than deleting data.

## Evidence

A successful run ends with:

```text
[DEPLOY] === PASS ===
[DEPLOY] commit=<sha>
[DEPLOY] log=<path>
```

A failed run prints service state and recent logs and points to the immutable deployment log.

## AI-agent usage

The AI agent should invoke the script rather than reconstructing the deployment procedure from memory. It should report the final commit SHA, service state, migration result, health/readiness result, and log path.

If the SSH session is unreliable, launch the command inside a persistent tmux session:

```bash
tmux new -s pol-deploy
bash deploy/vps_deploy.sh
```

The agent may reconnect with:

```bash
tmux attach -t pol-deploy
```

Do not treat a dropped SSH session as a deployment failure until the tmux job has been inspected.
