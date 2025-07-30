import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy import Uuid
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class IntegerIDMixin:
    """Integer ID Mixin"""

    if TYPE_CHECKING:
        id: int
    else:
        id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)


class UUIDIDMixin:
    """UUID ID Mixin"""

    if TYPE_CHECKING:
        id: uuid.UUID
    else:
        id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class CreatedAtMixin:
    """Created At Mixin"""

    if TYPE_CHECKING:
        created_at: datetime
    else:
        created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class UpdatedAtMixin:
    """Updated At Mixin"""

    if TYPE_CHECKING:
        updated_at: datetime
    else:
        updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
