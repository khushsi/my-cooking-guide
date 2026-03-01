"""Persona router — managing individual profiles within a household."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User
from app.models.persona import Persona
from app.routers.auth import get_current_user
from app.schemas.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaTemplatesResponse,
    PersonaTemplate,
    GENERIC_PERSONAS,
)

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
    query = select(Persona).where(Persona.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    data: PersonaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new personal profile under the current user's household."""
    new_persona = Persona(
        user_id=current_user.id,
        name=data.name,
        is_primary=data.is_primary,
        template_name=data.template_name,
        diet_type=data.diet_type,
        allergies=data.allergies,
        medical_conditions=data.medical_conditions,
        disliked_ingredients=data.disliked_ingredients,
        loved_ingredients=data.loved_ingredients,
        spice_tolerance=data.spice_tolerance,
        target_calories=data.target_calories,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
    )
    db.add(new_persona)
    await db.commit()
    await db.refresh(new_persona)
    return new_persona


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: uuid.UUID,
    data: PersonaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing personal profile (Progressive Profiling)."""
    query = select(Persona).where(
        Persona.id == persona_id, Persona.user_id == current_user.id
    )
    result = await db.execute(query)
    persona = result.scalar_one_or_none()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(persona, key, value)

    await db.commit()
    await db.refresh(persona)
    return persona


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a personal profile."""
    query = select(Persona).where(
        Persona.id == persona_id, Persona.user_id == current_user.id
    )
    result = await db.execute(query)
    persona = result.scalar_one_or_none()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    await db.delete(persona)
    await db.commit()
    return None
