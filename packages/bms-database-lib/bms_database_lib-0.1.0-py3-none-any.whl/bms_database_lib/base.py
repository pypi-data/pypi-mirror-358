from decimal import Decimal
from typing import Annotated

from sqlalchemy import MetaData
from sqlalchemy import Numeric
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import registry

constraint_naming_conventions = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

num_10_2 = Annotated[Decimal, 10]


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=constraint_naming_conventions)
    registry = registry(
        type_annotation_map={
            num_10_2: Numeric(10, 2),
        }
    )

    def __repr__(self) -> str:
        columns = ", ".join([f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")])
        return f"<{self.__class__.__name__}({columns})>"

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "".join([("_" + i.lower() if i.isupper() else i) for i in cls.__name__]).strip("_")
