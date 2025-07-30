from importlib.metadata import entry_points, EntryPoint


class Registry:
    def __init__(self, group_name: str):
        self._plugins = dict()
        self.group_name = group_name
        self._load_entry_point_plugins()

    def _load_entry_point_plugins(self):
        points = entry_points(group=self.group_name)

        for point in points:
            self._plugins[point.name] = point

    @property
    def available_items(self):
        return self._plugins

    def load_by_name(self, name: str):
        plugin = self._plugins.get(name, None)
        if plugin is None:
            raise NameError(f"cannot find {name} plugin in {self.group_name} group")
        else:
            if isinstance(plugin, EntryPoint):
                return plugin.load()
            else:
                return plugin

    def register(self, name, item):
        self._plugins[name] = item

    def __call__(self, label):
        def adder(func):
            self.register(label, func)
            return func
        return adder


operator_registry = Registry("operators")


@operator_registry("NewOperator")
class NewOperator:
    def __init__(self):
        print("new operator initialized")

if __name__ == "__main__":
    for x in operator_registry.available_items:
        print(x)