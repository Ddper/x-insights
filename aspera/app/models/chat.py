from sqlalchemy import Column, String, VARCHAR, ForeignKey, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Chat(Base):

    title = Column(VARCHAR(30), nullable=True)
    chat_documents = relationship("ChatDocument", back_populates="chat")


class ChatDocument(Base):

    chat_id = Column(
        UUID(as_uuid=True), ForeignKey("chat.id"), index=True
    )
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("document.id"), index=True
    )
    chat = relationship("Chat", back_populates="chat_documents")
    document = relationship("Document", back_populates="chats")
