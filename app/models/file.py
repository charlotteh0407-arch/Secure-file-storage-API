from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    Owner_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    storage_key = Column(String, unique=True, nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="files")