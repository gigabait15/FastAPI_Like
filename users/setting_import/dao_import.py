from sqlalchemy.orm import joinedload
from DAO.base import BaseDAO
from database import async_session_maker
from users.models import User
from sqlalchemy import select, desc