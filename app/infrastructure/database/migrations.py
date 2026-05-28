from alembic import command
from alembic.config import Config
import uuid


alembic_cfg = Config("alembic.ini")

def create_migration():
    command.revision(
        alembic_cfg,
        autogenerate=True,
        message=str(uuid.uuid4()),
    )

def run_migrations():
    create_migration()
    
    command.upgrade(
        alembic_cfg,
        "head",
    )