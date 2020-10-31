class Field:
    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"


class StringField(Field):
    def __init__(self, name):
        super().__init__(name, "varchar(100)")


class IntegerField(Field):
    def __init__(self, name):
        super().__init__(name, "bigint")


class ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        if name == "Model":
            return type.__new__(mcs, name, bases, attrs)
        mappings = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        for k in mappings:
            attrs.pop(k)
        attrs["__mappings__"] = mappings  # mapping between attributes and columns
        attrs["__table__"] = attrs.get("__table__", None) or name  # the name of the class is the name of the table
        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'Model' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def save(self):
        fields, params, args = [], [], []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))

        sql = f"INSERT INTO {self.__table__} ({', '.join(fields)}) VALUES ({','.join(params)}))"
        print(f"SQL: {sql}", f"ARGS: {args}")  # Using args to  avoid SQL injection


class User(Model):
    __table__ = "MyUser"
    id = IntegerField("id")
    name = StringField("username")
    email = StringField("email")
    password = StringField("password")


if __name__ == "__main__":
    u = User(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
    u['id'] = 45678
    u.save()
