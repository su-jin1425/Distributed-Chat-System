import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.schemas.room import RoomCreate, RoomUpdate, AddMemberRequest
from app.models.chat_room import ChatRoom, RoomType
from app.models.room_member import RoomMember, MemberRole


class RoomService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.room_repo = RoomRepository(session)
        self.user_repo = UserRepository(session)

    async def get_room(self, room_id: uuid.UUID) -> ChatRoom:
        room = await self.room_repo.get_by_id(room_id)
        if not room or room.is_archived:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )
        return room

    async def create_room(self, user_id: uuid.UUID, room_in: RoomCreate) -> ChatRoom:
        room = await self.room_repo.create(
            name=room_in.name,
            room_type=room_in.room_type,
            description=room_in.description,
            created_by=user_id,
        )
        
        # Add creator as owner
        await self.room_repo.add_member(
            room_id=room.id, user_id=user_id, role=MemberRole.OWNER
        )
        
        return room

    async def update_room(
        self, user_id: uuid.UUID, room_id: uuid.UUID, room_in: RoomUpdate
    ) -> ChatRoom:
        room = await self.get_room(room_id)
        
        member = await self.room_repo.get_member(room_id, user_id)
        if not member or member.role not in [MemberRole.OWNER, MemberRole.MODERATOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update room",
            )
            
        update_data = room_in.model_dump(exclude_unset=True)
        return await self.room_repo.update(room, **update_data)

    async def get_user_rooms(self, user_id: uuid.UUID) -> list[ChatRoom]:
        return await self.room_repo.get_user_rooms(user_id)

    async def add_member(
        self, current_user_id: uuid.UUID, room_id: uuid.UUID, req: AddMemberRequest
    ) -> RoomMember:
        room = await self.get_room(room_id)
        
        if room.room_type == RoomType.DIRECT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add members to direct messages",
            )
            
        # Check permissions
        current_member = await self.room_repo.get_member(room_id, current_user_id)
        if not current_member or current_member.role == MemberRole.MEMBER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to add members",
            )
            
        # Verify user exists
        target_user = await self.user_repo.get_by_id(req.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
            
        # Check if already member
        existing_member = await self.room_repo.get_member(room_id, req.user_id)
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member",
            )
            
        return await self.room_repo.add_member(
            room_id=room_id, user_id=req.user_id, role=req.role
        )

    async def get_members(self, room_id: uuid.UUID) -> list[RoomMember]:
        await self.get_room(room_id)  # Validate exists
        return await self.room_repo.get_members(room_id)

    async def remove_member(
        self, current_user_id: uuid.UUID, room_id: uuid.UUID, target_user_id: uuid.UUID
    ) -> None:
        await self.get_room(room_id)
        
        # Determine if self-leaving or kicking
        if current_user_id != target_user_id:
            current_member = await self.room_repo.get_member(room_id, current_user_id)
            if not current_member or current_member.role == MemberRole.MEMBER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to remove members",
                )
                
            target_member = await self.room_repo.get_member(room_id, target_user_id)
            if target_member and target_member.role == MemberRole.OWNER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot remove room owner",
                )
                
        await self.room_repo.remove_member(room_id, target_user_id)
