import os

import psycopg

Error = psycopg.Error

DSN = os.getenv('DATABASE_URL',
                'postgresql://postgres:postgres@localhost:5432/log_analyser')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS failed_logins (
    id       BIGSERIAL PRIMARY KEY,
    month    TEXT NOT NULL,
    day      INT  NOT NULL,
    hour     INT  NOT NULL,
    username TEXT NOT NULL,
    ip       TEXT NOT NULL,
    attempts INT  NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_failed_ip ON failed_logins (ip);
CREATE TABLE IF NOT EXISTS ip_country (
    ip      TEXT PRIMARY KEY,
    country TEXT NOT NULL
);
'''


def connect():
    return psycopg.connect(DSN)       # `with connect() as conn` commits and closes


def init(conn):
    conn.execute(SCHEMA)


def save_events(conn, events):
    """Rebuilt from the logs on every run, so truncate first (no duplicates)."""
    with conn.cursor() as cur:
        cur.execute('TRUNCATE failed_logins')
        cur.executemany(
            'INSERT INTO failed_logins (month, day, hour, username, ip, attempts) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            [(e['month'], e['day'], e['hour'], e['user'], e['ip'], e['count'])
             for e in events])


def save_geo(conn, geo):
    with conn.cursor() as cur:
        cur.executemany(
            'INSERT INTO ip_country (ip, country) VALUES (%s, %s) '
            'ON CONFLICT (ip) DO UPDATE SET country = EXCLUDED.country',
            list(geo.items()))


def country_counts(conn):
    rows = conn.execute(
        "SELECT COALESCE(c.country, 'unknown'), SUM(f.attempts) "
        'FROM failed_logins f LEFT JOIN ip_country c USING (ip) '
        'GROUP BY 1 ORDER BY 2 DESC').fetchall()
    return {c: int(n) for c, n in rows}


def day_counts(conn):
    rows = conn.execute('SELECT month, day, SUM(attempts) FROM failed_logins '
                        'GROUP BY month, day').fetchall()
    return {(m, d): int(n) for m, d, n in rows}


def hour_counts(conn):
    rows = conn.execute('SELECT hour, SUM(attempts) FROM failed_logins '
                        'GROUP BY hour').fetchall()
    return {h: int(n) for h, n in rows}


def user_counts(conn):
    rows = conn.execute('SELECT username, SUM(attempts) FROM failed_logins '
                        'GROUP BY username ORDER BY 2 DESC').fetchall()
    return {u: int(n) for u, n in rows}


def unique_ips(conn):
    return conn.execute('SELECT COUNT(DISTINCT ip) FROM failed_logins').fetchone()[0]