# backend/database/repositories/base.py

"""
Base repository class with common database operations.
All specific repositories inherit from this.
"""

from typing import List, Optional, TypeVar, Generic, Type, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from backend.database import get_supabase_client
from backend.utils import get_logger, DatabaseError

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class BaseRepository(Generic[T]):
    """
    Base repository providing CRUD operations for Supabase tables.

    Type parameter T should be a Pydantic model representing the entity.
    """

    def __init__(self, table_name: str, model_class: Type[T]):
        """
        Initialize repository.

        Args:
            table_name: Name of the Supabase table
            model_class: Pydantic model class for the entity
        """
        self.table_name = table_name
        self.model_class = model_class
        self.client = get_supabase_client()

    def create(self, entity: T) -> T:
        """
        Insert a new entity.

        Args:
            entity: Pydantic model instance to insert

        Returns:
            Created entity with any generated fields (id, created_at, etc.)

        Raises:
            DatabaseError: If insertion fails
        """
        try:
            data = entity.model_dump(mode="json", exclude_unset=True)
            result = self.client.table(self.table_name).insert(data).execute()

            if not result.data:
                raise DatabaseError(f"Failed to create {self.model_class.__name__}")

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to create entity",
                table=self.table_name,
                error=str(e),
            )
            raise DatabaseError(f"Failed to create entity: {e}")

    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            entity_id: UUID of the entity

        Returns:
            Entity if found, None otherwise
        """
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("id", str(entity_id))
                .execute()
            )

            if not result.data:
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to get entity by ID",
                table=self.table_name,
                id=str(entity_id),
                error=str(e),
            )
            raise DatabaseError(f"Failed to get entity: {e}")

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Get all entities with optional pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        try:
            query = self.client.table(self.table_name).select("*")

            if limit:
                query = query.limit(limit)

            if offset:
                query = query.offset(offset)

            result = query.execute()
            return [self.model_class(**item) for item in result.data]
        except Exception as e:
            logger.error("Failed to get all entities", table=self.table_name, error=str(e))
            raise DatabaseError(f"Failed to get entities: {e}")

    def update(self, entity_id: UUID, updates: Dict[str, Any]) -> Optional[T]:
        """
        Update entity by ID.

        Args:
            entity_id: UUID of the entity
            updates: Dictionary of fields to update

        Returns:
            Updated entity if successful, None if not found
        """
        try:
            result = (
                self.client.table(self.table_name)
                .update(updates)
                .eq("id", str(entity_id))
                .execute()
            )

            if not result.data:
                return None

            return self.model_class(**result.data[0])
        except Exception as e:
            logger.error(
                "Failed to update entity",
                table=self.table_name,
                id=str(entity_id),
                error=str(e),
            )
            raise DatabaseError(f"Failed to update entity: {e}")

    def delete(self, entity_id: UUID) -> bool:
        """
        Delete entity by ID.

        Args:
            entity_id: UUID of the entity

        Returns:
            True if deleted, False if not found
        """
        try:
            result = (
                self.client.table(self.table_name)
                .delete()
                .eq("id", str(entity_id))
                .execute()
            )

            return len(result.data) > 0
        except Exception as e:
            logger.error(
                "Failed to delete entity",
                table=self.table_name,
                id=str(entity_id),
                error=str(e),
            )
            raise DatabaseError(f"Failed to delete entity: {e}")

    def count(self) -> int:
        """
        Get total count of entities in table.

        Returns:
            Number of entities
        """
        try:
            result = (
                self.client.table(self.table_name)
                .select("id", count="exact")
                .execute()
            )
            return result.count if result.count else 0
        except Exception as e:
            logger.error("Failed to count entities", table=self.table_name, error=str(e))
            raise DatabaseError(f"Failed to count entities: {e}")
