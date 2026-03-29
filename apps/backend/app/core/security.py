import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_email(email: str) -> str:
    normalized = email.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.nextauth_secret, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.nextauth_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_consent_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EncryptionService:
    def __init__(self, key: Optional[str] = None):
        raw_key = key or settings.encryption_key
        if not raw_key:
            self._fernet = None
            return
        self._fernet = Fernet(raw_key.encode() if isinstance(raw_key, str) else raw_key)

    def encrypt(self, value: str) -> str:
        if not self._fernet:
            return value
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        if not self._fernet:
            return value
        return self._fernet.decrypt(value.encode()).decode()

    def encrypt_dict_field(self, data: dict, fields: list[str]) -> dict:
        result = dict(data)
        for field in fields:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result

    def decrypt_dict_field(self, data: dict, fields: list[str]) -> dict:
        result = dict(data)
        for field in fields:
            if field in result and result[field]:
                try:
                    result[field] = self.decrypt(str(result[field]))
                except Exception:
                    pass
        return result


encryption_service = EncryptionService()


def get_mas_disclaimer() -> str:
    return (
        "This analysis is for informational purposes only. "
        "It is not financial advice and does not constitute a recommendation "
        "to purchase, cancel, or modify any insurance product. "
        "Actual policy terms, benefits, and payouts are subject to the full "
        "policy documents and insurer discretion. "
        "Consult a licensed financial adviser for personalised advice. "
        "This service is not regulated by the Monetary Authority of Singapore "
        "as a financial advisory service."
    )
