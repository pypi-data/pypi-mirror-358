from enum import IntEnum, auto
from importlib.metadata import entry_points, EntryPoint

class SystemCommand(IntEnum):
    START = auto()
    PAUSE = auto()
    STOP = auto()
    TERMINATE = auto()
    TERMINATE_ALL = auto()


class Registry:
    def __init__(self, group: str):
        self._plugins = dict()
        self.group = group
        self._load_entry_point_plugins()

    def _load_entry_point_plugins(self):
        points = entry_points(group=self.group)

        for point in points:
            self._plugins[point.name] = point

    @property
    def available_items(self):
        return self._plugins

    @property
    def names(self):
        return self._plugins.keys()

    def load_by_name(self, name: str):
        plugin = self._plugins.get(name, None)
        if plugin is None:
            raise NameError(f"cannot find {name} plugin in {self.group} group")
        else:
            if isinstance(plugin, EntryPoint):
                return plugin.load()
            else:
                return plugin

    def __getitem__(self, name):
        return self.load_by_name(name)

    def register(self, name, item):
        self._plugins[name] = item

    def __call__(self, label):
        def adder(func):
            self.register(label, func)
            return func
        return adder


TopicName = str
OperatorID = str
SubscriptionID = str
SYSTEM_COMMAND_TOPIC: TopicName = "SYS-CMD"
DEFAULT_TOPIC: TopicName = SYSTEM_COMMAND_TOPIC
# OPERATOR_CATALOG = entry_points(group="operators")
# MESSAGE_STREAM_CATALOG = entry_points(group="message_streams")
OPERATOR_CATALOG = Registry("operators")
MESSAGE_STREAM_CATALOG = Registry(group="message_streams")
