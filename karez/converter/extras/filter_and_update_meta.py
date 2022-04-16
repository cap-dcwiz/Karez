from ...config import OptionalConfigEntity
from ..base import ConverterBase


class Converter(ConverterBase):
    def __init__(self, *args, **kwargs):
        super(Converter, self).__init__(*args, **kwargs)
        self._filters = None

    @classmethod
    def role_description(cls):
        return "Filter and/or change the category of the data."

    @classmethod
    def config_entities(cls):
        yield from super(Converter, cls).config_entities()
        yield OptionalConfigEntity("key", None, "meta item name")
        yield OptionalConfigEntity("default", None, "Default value if key is not in meta info")
        yield OptionalConfigEntity("filter", None, "Category or list of categories that should be passed to next roles")
        yield OptionalConfigEntity("rename", {}, "Maps of old category names to new category names")

    @property
    def filters(self):
        if self.config.filter is None:
            return None
        if not self._filters:
            self._filters = self.config.filter
            if isinstance(self._filters, str):
                if "," in self._filters:
                    self._filters = set(self._filters.split(","))
                else:
                    self._filters = {self._filters}
        return self._filters

    def convert(self, payload):
        value = self.get_meta(payload, self.config.key, self.config.default)
        if self.filters and value not in self.filters:
            return
        if value in self.config.rename:
            self.update_meta(payload, category=self.config.rename[value])
        yield payload
