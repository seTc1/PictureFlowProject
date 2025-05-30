import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, scoped_session

SqlAlchemyBase = orm.declarative_base()

Session = None  # Будет инициализирован как scoped_session

def global_init(db_file):
    global Session

    if Session:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(
        conn_str,
        echo=False,
        pool_size=20,
        max_overflow=30,
        pool_timeout=30
    )
    session_factory = orm.sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)

def create_session() -> Session:
    return Session()