from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.domain.entities.user import UserInDB, UserUpdate, UserCreate
from app.presentation.api.v1.dependencies import get_current_active_user, get_user_use_case
from app.domain.use_cases.user_use_case import UserUseCase

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=UserInDB)
async def read_user(
    user_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    user_use_case: UserUseCase = Depends(get_user_use_case)
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    user = await user_use_case.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    user_use_case: UserUseCase = Depends(get_user_use_case)
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    try:
        user = await user_use_case.update_user(user_id, user_update)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    user_use_case: UserUseCase = Depends(get_user_use_case)
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    try:
        success = await user_use_case.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
