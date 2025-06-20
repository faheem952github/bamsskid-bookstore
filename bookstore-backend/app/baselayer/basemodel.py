import datetime

from sqlalchemy import (Column, Integer, DateTime, Boolean, event)

from config.database import Base


def utc_now():
    """Return the current UTC datetime as a timezone-aware object."""
    return datetime.datetime.now(datetime.timezone.utc)


class BaseModel(Base):
    """A base model that includes common fields and soft delete functionality."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Timestamp for when the record was soft-deleted

    @staticmethod
    def on_update(mapper, connection, target):
        """Automatically update the 'updated_at' field when a record is updated."""
        target.updated_at = utc_now()

    def soft_delete(self):
        """Mark the record as deleted and set the deleted_at timestamp."""
        self.is_deleted = True
        self.deleted_at = utc_now()
        self.updated_at = utc_now()


# Attach event listeners to update 'updated_at' field on update
event.listen(BaseModel, "before_update", BaseModel.on_update)
