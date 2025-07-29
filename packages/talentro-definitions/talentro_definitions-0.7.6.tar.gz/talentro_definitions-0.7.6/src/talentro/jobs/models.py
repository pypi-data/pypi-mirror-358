import uuid

from sqlalchemy import Column, JSON
from sqlmodel import Field

from ..general.models import JobsOrganizationModel


class Feed(JobsOrganizationModel, table=True):
    name: str = Field(index=True)
    status: str = Field(index=True)


class Job(JobsOrganizationModel, table=True):
    name: str = Field(index=True)
    feed_id: uuid.UUID = Field(foreign_key="feed.id")
    status: str = Field(index=True)
    custom_fields: dict = Field(sa_column=Column(JSON))

