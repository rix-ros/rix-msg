from field import Field


class Message:
    def __init__(
        self, name: str, package: str, hash: str, fields: list[dict[str, str]]
    ):
        self.name = name
        self.package = package
        self.hash = hash
        self.fields = [
            Field(f["name"], f["type"], None if "package" not in f else f["package"])
            for f in fields
        ]
