# Implementation Plan for Docker Sandbox Hardening

## Goal Description

The user requests to complete the Docker sandbox setup (`dosker kurulumunu tamamla`) and resolve any related errors. This involves:
- Adding security hardening to the `DockerSandbox` implementation (non‑root user, capability dropping, resource limits).
- Ensuring the Docker client is properly initialized and provides clear error messages.
- Updating configuration (`settings`) to expose needed Docker options.
- Adding logging for Docker sandbox operations.
- Updating any related code (e.g., `Executor`) to handle new parameters and failures gracefully.

## User Review Required

> [!IMPORTANT]
> The proposed changes will modify the Docker sandbox implementation and may affect existing unit tests. Please confirm that you want to:
> - Add non‑root execution (`user='1000:1000'`).
> - Drop all capabilities (`cap_drop=['ALL']`).
> - Add optional environment variable support.
> - Update `settings` to include `docker_user`, `docker_capabilities`, and `docker_network_disabled` flags.
>
> If you have specific values for these settings or prefer a different security posture, let me know.

## Proposed Changes

---
### [MODIFY] docker_sandbox.py
- Add imports for `logging` and `docker.errors`.
- Initialize a logger.
- Extend `DockerSandbox.__init__` to accept optional security parameters (user, capabilities, network disabled) from `settings`.
- Update `execute` method to include `user`, `cap_drop`, and optionally `network_disabled` arguments in `containers.run`.
- Add detailed exception handling with logging.
- Return decoded output safely.

---
### [MODIFY] settings.py (or appropriate config file)
- Add new configuration entries:
  ```python
  docker_user: str = '1000:1000'
  docker_capabilities: List[str] = ['ALL']
  docker_network_disabled: bool = True
  ```
- Ensure defaults are loaded from `.env` (e.g., `DOCKER_USER`, `DOCKER_CAP_DROP`).

---
### [MODIFY] executor.py
- Adjust sandbox initialization to pass the new security options.
- Add fallback handling if Docker client fails to start (log and set `self.sandbox = None`).
- Ensure `execute_code` returns a clear error when sandbox is unavailable.

---
### [ADD] tests/unit/test_docker_sandbox_security.py
- Add unit tests verifying that `DockerSandbox.execute` is called with the correct security arguments using `unittest.mock`.
- Ensure existing tests still pass.

## Open Questions

> [!WARNING]
> - Do you want the Docker sandbox to be optional (i.e., disable via `ENABLE_DOCKER=false` in `.env`)?
> - Are there any additional security constraints (e.g., read‑only filesystem, specific memory limits) you would like to enforce?

## Verification Plan

### Automated Tests
- Run existing test suite (`pytest -q`).
- Add new test `test_docker_sandbox_security.py` and ensure it passes.
- Verify that `Executor.execute_code` returns appropriate error messages when Docker is not available.

### Manual Verification
- Manually run the CLI and execute a simple Python snippet (`/execute "print('hello')"`).
- Observe Docker container logs to confirm it runs as non‑root and with dropped capabilities.
- Check that error messages are user‑friendly if Docker daemon is not running.

---
