"""Persona router — managing individual profiles within a household."""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaTemplatesResponse,
    PersonaTemplate,
    GENERIC_PERSONAS,
)
from app.services.persona_service import PersonaService

router = APIRouter(prefix="/api/personas", tags=["personas"])


@router.get("/templates", response_model=PersonaTemplatesResponse)
async def get_persona_templates():
    """Get the available generic persona templates for new users."""
    templates = [
        PersonaTemplate(**data) for data in GENERIC_PERSONAS.values()
    ]
    return PersonaTemplatesResponse(templates=templates)


@router.get("", response_model=list[PersonaResponse])
async def get_personas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all personas for the current user."""
    persona_service = PersonaService(db)
    return await persona_service.get_all_personas(current_user.id)


@router.post("", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    data: PersonaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new personal profile under the current user's household."""
    persona_service = PersonaService(db)
    return await persona_service.create_persona(current_user.id, data)


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: uuid.UUID,
    data: PersonaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing personal profile (Progressive Profiling)."""
    persona_service = PersonaService(db)
    return await persona_service.update_persona(current_user.id, persona_id, data)


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a personal profile."""
    persona_service = PersonaService(db)
    await persona_service.delete_persona(current_user.id, persona_id)
    return None
