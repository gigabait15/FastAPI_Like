from datetime import datetime, timedelta
from typing import (
    Optional,
    List
)

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Response,
    Depends,
    Query
)
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from database import (
    Gender,
    async_session_maker
)
from users.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token
)
from users.dao import UsersDAO
from users.dependencies import get_current_user
from users.models import User, Grade
from users.schemas import SUserView
from utils.geo import (
    get_geo,
    great_circle_distance
)
from utils.img_watermark import watermark_photo
from utils.send_email import send_email_notification