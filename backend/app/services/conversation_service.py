from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.message import Message
from app.models.session import Session


class ConversationService:
    """
    Central service responsible for conversation history and message persistence.
    """

    # -----------------------------
    # READ: Get conversation history
    # -----------------------------
    @staticmethod
    async def get_messages_for_session(
        db: AsyncSession,
        session_id: int,
        limit: int = 10,
    ) -> list[dict]:
        """
        Fetch last N messages for a session,
        ordered oldest → newest, formatted for LLM usage.
        """

        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )

        messages = result.scalars().all()
        messages.reverse()

        return [
            {
                "role": msg.sender,
                "content": msg.content,
            }
            for msg in messages
        ]

    # -----------------------------
    # WRITE: Persist a new message
    # -----------------------------
    @staticmethod
    async def add_message(
        db: AsyncSession,
        session_id: int,
        role: str,
        content: str,
    ) -> dict:
        """
        Persist a message in a session with validation.
        """

        # 1️⃣ Validate session exists
        session_result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise ValueError("Session does not exist")

        # 2️⃣ Validate role
        if role not in {"user", "assistant", "system"}:
            raise ValueError("Invalid role")

        # 3️⃣ Validate content
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        # 4️⃣ Create message
        message = Message(
            session_id=session_id,
            sender=role,
            content=content,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        # 5️⃣ Return clean structure
        return {
            "id": message.id,
            "session_id": message.session_id,
            "role": message.sender,
            "content": message.content,
        }
