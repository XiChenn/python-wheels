"""Simple ORM implementation with table Read, Update and Delete"""


class Column:
    """Represents a column in a database table."""

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    def __repr__(self):
        return self.__str__()


class StringColumn(Column):
    def __init__(self, name=None, length=100, primary_key=False, default=None):
        super().__init__(name, f"varchar({length})", primary_key, default)


class IntegerColumn(Column):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, "bigint", primary_key, default)


class ModelMetaclass(type):
    """Meta class to do columns check and filter"""
    def __new__(mcs, name, bases, attrs):
        # Skip base Model class
        if name == "Model":
            return type.__new__(mcs, name, bases, attrs)

        mappings = {}
        pk_columns, non_pk_columns = [], []

        for k, v in attrs.items():
            if isinstance(v, Column):
                # Use the key if the column name is not set
                column_name = v.name or k

                mappings[k] = v
                if v.primary_key:
                    pk_columns.append(column_name)  # support multiple PK cols
                else:
                    non_pk_columns.append(column_name)

        all_columns = pk_columns + non_pk_columns
        parameters = ["?"] * len(all_columns)

        if not pk_columns:
            raise RuntimeError("No primary key found")

        # Make sure getattr() in the subclass will not search meta class attrs
        for k in mappings:
            attrs.pop(k)

        # mapping between attributes and column types
        attrs["__mappings__"] = mappings

        # the name of the class is the name of the table if __table__ is None
        table_name = attrs.get("__table__", None) or name
        attrs["__table__"] = table_name

        attrs["__primary_keys__"] = pk_columns
        attrs["__non_pk_columns__"] = non_pk_columns

        # Construct default SELECT, INSERT, UPDATE and DELETE statements
        all_col_str = ", ".join([f"`{c}`" for c in all_columns])
        non_pk_col_str = ", ".join([f"`{c}`=?" for c in non_pk_columns])
        pk_cols = [f"`{c}`=?" for c in pk_columns]

        attrs["__select__"] = f"SELECT {all_col_str} FROM `{table_name}`"
        attrs["__insert__"] = f"INSERT INTO `{table_name}` " \
                              f"({all_col_str}) VALUES({','.join(parameters)})"
        attrs["__update__"] = f"UPDATE `{table_name}` SET {non_pk_col_str} " \
                              f"WHERE {' AND '.join(pk_cols)}"
        attrs["__remove__"] = f"DELETE FROM {table_name} " \
                              f"WHERE {' AND '.join(pk_cols)}"

        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    """Model class is the base class of all model classes"""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(f"'Model' has no attribute '{key}'") from e

    def __str__(self):
        kv = [f"{k}={repr(v)}" for k, v in self.items()]
        return f"<{self.__class__.__name__} ({', '.join(kv)})>"

    def __repr__(self):
        return self.__str__()

    def save(self):
        """Save object to DB"""
        args = [self.get(k, None) for k in self.__mappings__]
        sql = self.__insert__
        print(f"SQL: {sql}\nARGS: {args}")

    def find(self):
        """Find the object by the primary key."""
        pk_columns = self.__primary_keys__
        pk_col_str = " AND ".join([f"`{c}`=?" for c in pk_columns])
        args = [self.get(k, None) for k, v in self.__mappings__.items() if
                v.name in self.__primary_keys__]  # v.name is the column name
        sql = f"{self.__select__} WHERE {pk_col_str}"
        print(f"SQL: {sql}\nARGS: {args}")

    def update(self):
        sql = self.__update__
        args = [self.get(k, None) for k, v in self.__mappings__.items() if
                v.name in self.__non_pk_columns__]  # v.name is the column name
        args.extend([self.get(k, None) for k, v in self.__mappings__.items() if
                    v.name in self.__primary_keys__])
        print(f"SQL: {sql}\nARGS: {args}")

    def delete(self):
        sql = self.__remove__
        args = [self.get(k, None) for k, v in self.__mappings__.items() if
                v.name in self.__primary_keys__]  # v.name is the column name
        print(f"SQL: {sql}\nARGS: {args}")


class User(Model):
    __table__ = "MyUser"
    id = IntegerColumn("id", primary_key=True)
    name = StringColumn("username", 20, primary_key=True)
    email = StringColumn("email")
    password = StringColumn("password")


if __name__ == "__main__":
    u = User(id=654321, name="Mike", email="test@abc.com", password="my_pass")
    u["id"] = 45678
    u.save()
    u.find()
    u.update()
    u.delete()
