
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Chemin de la base de données
DATABASE_URL = "sqlite:///./juice_database.db"

# Création du moteur SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Création des sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base des modèles
Base = declarative_base()


# Fonction pour obtenir une session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Création des tables
def create_database():
    Base.metadata.create_all(bind=engine)
