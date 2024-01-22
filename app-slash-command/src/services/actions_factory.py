from ..handlers.error_handler import DevenvActionIsNotImplementedError
from .actions import start, stop, status, prolongate, help, support


class ActionFactory:
    actions = {
        "start": start.StartAction,
        "stop": stop.StopAction,
        "status": status.StatusAction,
        "prolongate": prolongate.ProlongateAction,
        "help": help.HelpAction,
        "support": support.SupportAction,
    }

    @classmethod
    def create_action(cls, action):
        if action_class := cls.actions.get(action):
            return action_class()

        raise DevenvActionIsNotImplementedError(action=action)
