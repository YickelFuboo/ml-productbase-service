from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config.settings import settings
from app.domains.product_mgmt.models.products import ProductRecord, VersionRecord
from app.domains.arch_mgmt.models import architecture
from app.domains.arch_mgmt.models import decision
from app.domains.arch_mgmt.models import interfaces
from app.domains.arch_mgmt.models import build
from app.domains.arch_mgmt.models import deployment
from app.domains.scene_mgmt.models import scene
from app.domains.kb_mgmt.models import knowledge_base
from app.infrastructure.database.models_base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def get_sync_database_url() -> str:
    """从应用配置生成同步数据库 URL（Alembic 使用同步驱动）"""
    db_type = settings.database_type.lower()
    if db_type in ("postgresql", "postgres"):
        return (
            f"postgresql+psycopg2://{settings.postgresql_user}:{settings.postgresql_password}"
            f"@{settings.postgresql_host}:{settings.postgresql_port}/{settings.db_name}"
        )
    if db_type == "mysql":
        return (
            f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
            f"@{settings.mysql_host}:{settings.mysql_port}/{settings.db_name}"
        )
    return "sqlite:///./koalawiki.db"


def run_migrations_offline() -> None:
    """离线模式：仅生成 SQL，不连接数据库"""
    url = get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连接数据库执行迁移"""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_sync_database_url()
    connectable = create_engine(
        configuration["sqlalchemy.url"],
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
