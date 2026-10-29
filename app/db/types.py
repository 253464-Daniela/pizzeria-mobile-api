from sqlalchemy.types import UserDefinedType


class CIText(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "citext"