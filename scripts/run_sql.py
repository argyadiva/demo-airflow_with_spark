import sys
from pathlib import Path

from db import get_engine


SQL_ROOT = (Path(__file__).resolve().parent / 'sql').resolve()


def resolve_sql_path(value):
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if candidate.suffix.lower() != '.sql' or SQL_ROOT not in candidate.parents:
        raise RuntimeError(f'SQL file must be inside {SQL_ROOT}')
    if not candidate.is_file():
        raise RuntimeError(f'SQL file not found: {candidate}')
    return candidate


def main():
    if len(sys.argv) != 2:
        raise RuntimeError('Usage: python scripts/run_sql.py <scripts/sql/model.sql>')

    sql_path = resolve_sql_path(sys.argv[1])
    statement = sql_path.read_text(encoding='utf-8')
    engine = get_engine()
    with engine.begin() as connection:
        connection.exec_driver_sql(statement)

    print(f'Executed {sql_path.relative_to(SQL_ROOT)} successfully.')


if __name__ == '__main__':
    main()
