from .components import CrudComponent, JsonType, KongEntity


class Sni(KongEntity):
    pass


class Snis(CrudComponent[Sni]):
    """Kong SNI API component"""

    async def apply_json(self, data: JsonType, clear: bool = True) -> list:
        """Apply a JSON data objects for snis - never clear them"""
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            entry = entry.copy()
            name = entry.pop("name")
            if await self.has(name):
                sni = await self.update(name, **entry)
            else:
                sni = await self.create(name=name, **entry)
            result.append(sni.data)
        return result
