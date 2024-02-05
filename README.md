# Kubernetes deployments and stateful sets scaler via slack bot slash command

Kubernetes cluster with multiple namespaces. These namespaces should be stopped at specific time every working day and started manually by user request.

## requirements

Namespace should be stopped by `cronjob` at specific time if it has `scheduler=enabled` label. All namespaces should have the same scheduled shutdown time (for now it's hardcoded in template and can be found in `src/templates/cronjob.py`).

cronjob is created automatically and should be active when:
* we create a new namespace without label
* we label a namespace with `scheduler=enabled`

cronjob should be paused when:
* namespace has been created with `scheduler=disabled`
* namespace has been relabeled with `scheduler=disabled`

## slack slash commands

Commands should send default payload to scaler api; that means it will scale all deployments and stateful sets to 0 replicas as stop/start commands.

### prolongate

Namespace can be prolongated: user can modify (add hours) shutdown time by invoking command /<slash-command> prolongate <namespace> for <hours>. Example:

```yaml
/devenv prolongate dev1 for 1h
```

### start

Namespace can be started manually by user request by invoking command /<slash-command> start <namespace>. Example:

```yaml
/devenv start dev1
```

### stop

Namespace can be stopped manually by user request by invoking command /<slash-command> stop <namespace>. Example:

```yaml
/devenv stop dev1
```

### status

We can track actual status of specific deployment (based on kubernetes deployment status) via /<slash-command> status <namespace>. Example:

```yaml
/devenv status dev1
```

### help

Slash command should have help command which will return actual help message for all commands via /<slash-command> help. Example:

```yaml
/devenv help
```

TODO

## scaler


## cacher


## proxy
