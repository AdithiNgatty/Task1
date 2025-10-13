from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from backend.models import BioIn, BioOut
from backend.auth import get_current_user
from backend.database import db

router = APIRouter()



# -------------------- Helper: normalize user id --------------------
def _user_query_id(user: dict):
    # Prefer using the actual Mongo _id if available, otherwise fall back to username
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if "_id" in user:
        return {"_id": user["_id"]}
    return {"username": user.get("username")}

# -------------------- Routes --------------------
@router.get("/me", response_model=BioOut)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Return public profile fields (username, email, bio)."""
    # Fetch latest from DB to ensure freshness
    query = _user_query_id(current_user)
    user = await db.users.find_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return BioOut(username=user.get("username"), email=user.get("email"), bio=user.get("bio"))

@router.post("/me/bio", response_model=BioOut, status_code=status.HTTP_201_CREATED)
async def create_bio(bio_in: BioIn, current_user: dict = Depends(get_current_user)):
    """Create or set the bio for the authenticated user. If a bio already exists it will be overwritten.
    Use POST when creating a bio for the first time; PUT is provided below for edits.
    """
    query = _user_query_id(current_user)
    update = {"$set": {"bio": bio_in.bio}}
    result = await db.users.update_one(query, update)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    user = await db.users.find_one(query)
    return BioOut(username=user.get("username"), email=user.get("email"), bio=user.get("bio"))

@router.put("/me/bio", response_model=BioOut)
async def update_bio(bio_in: BioIn, current_user: dict = Depends(get_current_user)):
    """Edit the existing bio. This will overwrite whatever bio exists currently."""
    query = _user_query_id(current_user)
    result = await db.users.update_one(query, {"$set": {"bio": bio_in.bio}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    user = await db.users.find_one(query)
    return BioOut(username=user.get("username"), email=user.get("email"), bio=user.get("bio"))

@router.delete("/me/bio", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bio(current_user: dict = Depends(get_current_user)):
    """Delete the bio field from the user's profile."""
    query = _user_query_id(current_user)
    result = await db.users.update_one(query, {"$unset": {"bio": ""}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Return no content
    return None

