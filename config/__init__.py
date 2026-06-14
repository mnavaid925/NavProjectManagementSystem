import pymysql

pymysql.install_as_MySQLdb()

# XAMPP ships MariaDB 10.4.x, but Django 5.1 hard-gates MySQL backend at
# MariaDB >= 10.5. The features this schema uses (JSONField, utf8mb4, indexes)
# are all fully supported on 10.4, so we relax the version floor to match the
# bundled server. This is an environment/deployment override, not a schema change.
from django.db.backends.mysql import features as _mysql_features  # noqa: E402
from django.utils.functional import cached_property  # noqa: E402


def _relaxed_minimum_database_version(self):
    if self.connection.mysql_is_mariadb:
        return (10, 4)
    return (5, 7)


_mysql_features.DatabaseFeatures.minimum_database_version = cached_property(
    _relaxed_minimum_database_version
)
_mysql_features.DatabaseFeatures.minimum_database_version.__set_name__(
    _mysql_features.DatabaseFeatures, 'minimum_database_version'
)


# MariaDB only learned `INSERT ... RETURNING` in 10.5. On the bundled 10.4
# server Django 5.1 still emits RETURNING (it assumes >= 10.5), which fails with
# a SQL syntax error. Disable the RETURNING-based features so Django falls back
# to last_insert_id() on this older server.
def _can_return_columns_from_insert(self):
    if self.connection.mysql_is_mariadb:
        return self.connection.mysql_version >= (10, 5, 0)
    return True


def _can_return_rows_from_bulk_insert(self):
    return self.can_return_columns_from_insert


for _name, _func in (
    ('can_return_columns_from_insert', _can_return_columns_from_insert),
    ('can_return_rows_from_bulk_insert', _can_return_rows_from_bulk_insert),
):
    _prop = cached_property(_func)
    _prop.__set_name__(_mysql_features.DatabaseFeatures, _name)
    setattr(_mysql_features.DatabaseFeatures, _name, _prop)
