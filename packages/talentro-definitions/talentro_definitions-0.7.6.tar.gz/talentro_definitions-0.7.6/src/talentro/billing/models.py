import enum
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Enum as SqlEnum, PrimaryKeyConstraint, Identity, Integer

from sqlalchemy import Column
from sqlmodel import SQLModel, Field

from ..general.models import BillingModel, BillingOrganizationModel


class CurrencyEnum(str, enum.Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    YPJ = "YPJ"


class BillingEvent(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, Identity(), nullable=False)
    )


    organization: uuid.UUID = Field(index=True)
    event_time: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sku: int = Field(foreign_key="sku.id")

    __table_args__ = (
        PrimaryKeyConstraint("id", "event_time"),
    )


class SKU(SQLModel, table=True):
    id: int = Field(nullable=False, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    amount: float
    currency: CurrencyEnum = Field(sa_column=Column(SqlEnum(CurrencyEnum)))
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )


class BillingProfile(BillingOrganizationModel, table=True):
    stripe_customer_id: str = Field(nullable=False)
