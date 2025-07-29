# from sqlalchemy import Enum
# from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import configure_mappers


def get_engine(url="sqlite+pysqlite:///:memory:", timeout: int = 0, schema: str = ""):
    configure_mappers()
    connect_args = {}
    if timeout:
        if "pymysql" in url:  # pragma: no cover
            connect_args.update(dict(read_timeout=timeout, write_timeout=timeout))
        elif "sqlite" in url:
            connect_args.update(dict(timeout=float(timeout)))
        elif "pyodbc" in url:  # pragma: no cover
            connect_args.update(dict(timeout=timeout))
        elif "psycopg" in url:  # pragma: no cover
            connect_args.update(dict(connect_timeout=timeout))
    engine = create_engine(url, connect_args=connect_args)
    # if engine.driver == "postgresql":  # pragma: no cover
    #     Base.metadata = MetaData(schema=schema)
    #     Base.type_annotation_map = {Enum: Enum(Enum, inherit_schema=True)}
    return engine
