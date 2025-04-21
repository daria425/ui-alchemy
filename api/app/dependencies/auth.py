
from fastapi import Header, HTTPException
from app.utils.auth_utils import decode_token
def get_uid(authorization=Header(None)):
    """
    Get the uid from the token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token not provided")
    id_token = authorization.split('Bearer ')[-1]
    decoded_token=decode_token(id_token)
    if decoded_token:
        return decoded_token["uid"]
    else:
        return None