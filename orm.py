class Column:
    """Represents a column in a database table."""

    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    def __repr__(self):
        return self.__str__()


class StringColumn(Column):
    def __init__(self, name, max_length=100):
        super().__init__(name, f"varchar({max_length})")


class IntegerColumn(Column):
    def __init__(self, name):
        super().__init__(name, "bigint")


class ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        if name == "Model":  # keep the Model class unchanged
            return type.__new__(mcs, name, bases, attrs)
        mappings = {k: v for k, v in attrs.items() if isinstance(v, Column)}
        for k in mappings:  # Delete attributes from the attrs to avoid run time error
            attrs.pop(k)
        attrs["__mappings__"] = mappings  # mapping between attributes and column types
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

    def __str__(self):
        kv = [f"{k}={repr(v)}" for k, v in self.items()]
        return f"<{self.__class__.__name__} ({', '.join(kv)})>"

    def __repr__(self):
        return self.__str__()

    def save(self):
        cols, params, args = [], [], []
        for k, v in self.__mappings__.items():
            cols.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))

        sql = f"INSERT INTO {self.__table__} ({', '.join(cols)}) VALUES ({','.join(params)}))"
        print(f"SQL: {sql}", f"ARGS: {args}")  # Using args to  avoid SQL injection

    def find(self, key=None):
        pass

    def update(self):
        pass

    def delete(self):
        pass


class User(Model):
    __table__ = "MyUser"
    id = IntegerColumn("id")
    name = StringColumn("username")
    email = StringColumn("email")
    password = StringColumn("password")


if __name__ == "__main__":
    u = User(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
    print(u)
    u['id'] = 45678
    u.save()

    c = StringColumn('name')
    print(c)
