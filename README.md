# Main idea

Let's imagine that we have a bunch of kubernetes namespaces as environments and we desire to shut them down, like scale replicas to 0 at night time, start/stop environment per user request (for instance, /command start dev1) and have a possibility to prolongate individual environment for some period (/command prolongate dev1 for 2h) and get notifications to slack channel before [x,x,x] mins about shutdown (for this task we use dynamodb). Moreower, we use `ValidatingWebhookConfiguration` to dynamically mark created namespace as schedulable for shut down (can be disabled by re-labeling namespace) or any existing namespace can be labeled (kubectl label namespace dev scheduler={enabled,disabled})

## prolongate and notifications

In this particular example, we will have kubernetes cronjob in each dev namespace with default schedule settings created by app-scaler and we will have another independent cronjob that will reset all cronjobs schedule to default schedule at 9:00 morning time (we have to get back default shut down schedule if any environment is prolongated)

## status command

We took `app-web` as a default deployment label for service and based on status of it's replicas we decide - is our environment up or down
(this behaviour is just an example, can be purged or replaced by more intellectual approach)

## app-slash-command && app-scaler

FastAPI as a http server for Slack slash command. Simply speaking, this is a web server which recieves
Slack payload from slack slash command and forwards that to app-scaler. They have similar project structure.


```shell
├── src/
│   ├── common
│   ├── controllers
│   ├── handlers
│   ├── models
│   ├── routes
│   ├── services
│   ├── config.py
│   └── app.py
├── kubernetes
│   └── ...
└── Dockerfile
```

* common - local utils
* controllers - HTTP endpoints controllers
* hadlers - error handlers/validators
* models - pydantic models for requests and responses
* routes - application routes
* services - layer with endpoint logic/processing
* config.py - config for the project
* app.py - entrypoint for the app

All commands described in `models/slack_model.py`. For instance, currentry we support these commands:

```python
class ActionEnums(str, Enum):
    STOP = "stop"
    START = "start"
    STATUS = "status"
    PROLONGATE = "prolongate"
    HELP = "help"
```