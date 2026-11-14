
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import create_database, get_db
from backend.models import User, LoginSession, CalculationHistory
from backend.schemas import UserCreate, UserLogin, UserResponse
from backend.auth import (
    hash_password,
    verify_password,
    create_session_token,
    hash_session_token
)


app = FastAPI(
    title="Juice Concentration API",
    description="API pour le calcul et le suivi du procédé de concentration du jus",
    version="1.0.0"
)

security = HTTPBearer(
    scheme_name="Bearer Authentication",
    auto_error=False
)

SESSION_DURATION_DAYS = 7


# INITIALISATION DE LA BASE DE DONNEES
@app.on_event("startup")
def startup():
    create_database()


# VALIDATION DE LA SESSION
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Token manquant."
        )

    token_hash = hash_session_token(
        credentials.credentials
    )

    session = db.query(LoginSession).filter(
        LoginSession.token_hash == token_hash,
        LoginSession.revoked.is_(False)
    ).first()

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Session invalide."
        )

    if session.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="Session expirée."
        )

    user = db.query(User).filter(
        User.id == session.user_id
    ).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur invalide ou désactivé."
        )

    return user


# PAGE D'ACCUEIL
@app.get("/")
def home():
    return {
        "message": "Bienvenue dans l'API Juice Concentration"
    }


# VERIFICATION API
@app.get("/health")
def health():
    return {"status": "OK"}


# INSCRIPTION
@app.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        (User.username == user_data.username) |
        (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username ou email déjà utilisé."
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# CONNEXION
@app.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        (User.username == user_data.username_or_email) |
        (User.email == user_data.username_or_email)
    ).first()

    if not user or not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Identifiants incorrects."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Ce compte est désactivé."
        )

    token, token_hash = create_session_token()

    expires_at = datetime.utcnow() + timedelta(
        days=SESSION_DURATION_DAYS
    )

    new_session = LoginSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )

    db.add(new_session)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": SESSION_DURATION_DAYS * 24 * 60 * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


# INFORMATIONS DE L'UTILISATEUR CONNECTE
@app.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user


# DECONNEXION
@app.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Token manquant."
        )

    token_hash = hash_session_token(
        credentials.credentials
    )

    session = db.query(LoginSession).filter(
        LoginSession.token_hash == token_hash,
        LoginSession.revoked.is_(False)
    ).first()

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Session invalide."
        )

    session.revoked = True
    db.commit()

    return {
        "message": "Déconnexion réussie."
    }

# HISTORIQUE DES CALCULS

import json
from pydantic import BaseModel


class CalculationHistoryCreate(BaseModel):
    results: dict


@app.post("/calculations")
def save_calculation(
    data: CalculationHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_calculation = CalculationHistory(
        user_id=current_user.id,
        results=json.dumps(data.results)
    )

    db.add(new_calculation)
    db.commit()
    db.refresh(new_calculation)

    return {
        "message": "Calcul enregistré avec succès.",
        "calculation_id": new_calculation.id
    }


@app.get("/calculations")
def get_calculations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    calculations = db.query(CalculationHistory).filter(
        CalculationHistory.user_id == current_user.id
    ).order_by(
        CalculationHistory.created_at.desc()
    ).all()

    return [
        {
            "id": calculation.id,
            "results": json.loads(calculation.results),
            "created_at": calculation.created_at
        }
        for calculation in calculations
    ]
