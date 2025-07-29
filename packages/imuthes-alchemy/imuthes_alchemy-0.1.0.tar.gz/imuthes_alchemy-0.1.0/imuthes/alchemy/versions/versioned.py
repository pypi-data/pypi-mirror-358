import getpass
from collections import defaultdict
from datetime import datetime
from typing import Optional

# from kion.util import MarkdownTable, logger
from sqlalchemy import String, DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, MappedAsDataclass
from sqlalchemy.sql import expression

from imuthes.alchemy.exceptions import RecordNotFoundError

import sys

def db_user(context):
    return get_current_user(context.engine)


# noinspection PyPep8Naming
class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


class Versioned:

    # noinspection PyMethodParameters
    @declared_attr
    def __versioned__(cls):
        return {}

    _created__: Mapped[datetime] = mapped_column(
        server_default=utcnow(),
        sort_order=sys.maxsize,
    )
    _updated__: Mapped[Optional[datetime]] = mapped_column(
        onupdate=utcnow(),
        sort_order=sys.maxsize,
    )
    _user__: Mapped[str] = mapped_column(
        String(255),
        default=db_user,
        onupdate=db_user,
        sort_order=sys.maxsize,
    )

    # @classmethod
    # def cli_versions(cls, session, name: str):
    #     # noinspection PyUnresolvedReferences
    #     record = cls.get__(session, name)
    #     if record is None:
    #         raise RecordNotFoundError(cls, name)
    #     columns = ['O', 'T', '_date_', '_user_']
    #     data = []
    #     version_count = 0
    #     for i in record.versions:
    #         version_count += 1
    #         rows = (defaultdict(str), defaultdict(str))
    #         for k, v in i.changeset.items():
    #             if k.endswith('_'):
    #                 if k == '_created_':
    #                     rows[1]['_date_'] = str(v[1])
    #                     continue
    #                 if k == '_updated_':
    #                     if v[0] is None:
    #                         rows[0]['_date_'] = str(i.previous.changeset['_created_'][1])
    #                     else:
    #                         rows[0]['_date_'] = str(v[0])
    #                     rows[1]['_date_'] = str(v[1])
    #                     continue
    #                 if k == '_user_':
    #                     for n in range(2):
    #                         rows[n]['_user_'] = '_None_' if v[n] is None else str(v[n])
    #                     continue
    #             if k.endswith('_id'):
    #                 if k[:-3] not in columns:
    #                     columns.insert(-2, k[:-3])
    #                 for n in range(2):
    #                     # noinspection PyUnresolvedReferences
    #                     rows[n][k[:-3]] = '_None_' if v[n] is None else str(session.get__(cls.get_class_by_tablename__(k[:-3]), v[n]).name)
    #                 continue
    #             if k.strip('_') not in columns:
    #                 columns.insert(-2, k.strip('_'))
    #             for n in range(2):
    #                 rows[n][k.strip('_')] = '_None_' if v[n] is None else str(v[n])
    #         if i.operation_type == 0:   # insert
    #             rows[1]['O'], rows[1]['T'] = 'I', i.transaction_id
    #             data.append(rows[1])
    #         elif i.operation_type == 1:   # update
    #             rows[0]['O'], rows[0]['T'] = 'U', i.transaction_id
    #             data.append(rows[0])
    #             data.append(rows[1])
    #         else:    # delete
    #             rows[0]['O'], rows[0]['T'] = 'D', i.transaction_id
    #             data.append(rows[0])
    #     mt = MarkdownTable(*columns)
    #     for row in data:
    #         mt.append(row)
    #     print(mt.render())
    #     if version_count == 1:
    #         logger.info(f"Found one version")
    #     else:
    #         logger.info(f"Found {version_count} versions")


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, "mssql")
def ms_utcnow(element, compiler, **kw):
    return "GETUTCDATE()"


@compiles(utcnow, "mysql")
def my_utcnow(element, compiler, **kw):
    return "UTC_TIMESTAMP(6)"


@compiles(utcnow, "mariadb")
def maria_utcnow(element, compiler, **kw):
    return "UTC_TIMESTAMP(6)"


@compiles(utcnow, "sqlite")
def sqlite_utcnow(element, compiler, **kw):
    return "strftime('%Y-%m-%d %H:%M:%S')"


def get_current_user(engine):
    return engine.url.username or getpass.getuser() or "** not applicable **"
