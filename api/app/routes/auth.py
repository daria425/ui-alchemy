from fastapi import APIRouter, HTTPException, Depends, Request
from app.utils.auth_utils import get_token_data
from app.db.database_service_provider import DatabaseServiceProvider
from app.db.database_services import UserDatabaseService

def get_user_collection()->UserDatabaseService:
    return DatabaseServiceProvider.get_user_db_service()

router=APIRouter(prefix="/ui-alchemy/api/auth")

@router.post("/login")
def login(request: Request,user_collection:UserDatabaseService=Depends(get_user_collection)):
    """
    Login route to verify the token and return user data
    """
    id_token=request.headers.get("Authorization")
    if not id_token:
        raise HTTPException(status_code=401, detail="Token not provided")
    id_token = id_token.split('Bearer ')[-1]
    user_data=get_token_data(id_token)
    logged_in_user=user_collection.login_user(user_data)
    return logged_in_user

