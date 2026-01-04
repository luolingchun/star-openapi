class Config(dict):
    def from_object(self, obj: object) -> None:
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)
