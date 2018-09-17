from datetime import datetime
import json
import os

from google.cloud import bigquery
from flask import make_response
import psycopg2
from psycopg2.pool import SimpleConnectionPool


schemas = [('standard', 'events')]
BIGQUERY = os.environ.get('BIGQUERY') is not None
POSTGRES = os.environ.get('POSTGRES') is not None


if POSTGRES:
    pool = SimpleConnectionPool(1, 1,
                                user=os.environ.get('PG_USER'),
                                password=os.environ.get('PG_PASS', ''),
                                host=os.environ.get('PG_HOST'),
                                port=os.environ.get('PG_PORT', 5432),
                                database=os.environ.get('PG_DB'))

    # TODO verify schemas
    # pool.getconn()
    # pool.putconn()

if BIGQUERY:
    client = bigquery.Client()
    # Only executed during warm-up, for performance matters less
    for schema in schemas:
        assert len(schema) == 2
        dataset_ref = client.dataset(schema[0])
        dataset = client.get_dataset(dataset_ref)
        assert dataset is not None, '{} dataset does not exist'.format(schema[0])
        assert client.get_table(dataset_ref.table(schema[1])), '{}.{} table does not exist'.format(*schema)
        # TODO verify schema
        # TODO create tables if missing


def insert_rows(schema, rows_to_insert):
    if POSTGRES:
        conn = pool.getconn()
        cur = conn.cursor()
        columns = rows_to_insert[0]
        cur.execute("""insert into {}.{}({}) values {}""".format(
            schema[0],
            schema[1],
            ','.join(columns),
            ','.join(str(tuple([r[k] for k in columns])) for r in rows_to_insert)))
        conn.commit()
        pool.putconn(conn)

    if BIGQUERY:
        table = client.dataset(schema[0]).table(schema[1])
        errors = client.insert_rows_json(table, rows_to_insert)
        assert errors == []


def run(request):
    """
    Accepts <chord endpoint>/<dataset_id>/<table_id>
    `created` can be overridden with property
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS, POST',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Max-Age': 86400,
    }

    if request.method == 'OPTIONS':
        resp = make_response('', 200)
        resp.headers = headers
        return resp

    elif request.method == 'POST':
        path_parts = tuple([p for p in request.path.split('/') if p])
        if len(path_parts) != 2:
            return make_response('Incorrect path {}'.format(request.path), 404)
        elif path_parts not in schemas:
            return ('Not in whitelisted schemas {}'.format(request.path), 404)

        created = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f %Z')

        if isinstance(request.get_json(), dict):
            events = [request.get_json()]
        elif isinstance(request.get_json(), list):
            events = request.get_json()
        else:
            return 'Malformed body', 405

        rows_to_insert = []
        for event in events:
            rows_to_insert.append({
                'type': '.'.join(path_parts),
                'created': event.get('created') or created,
                'properties': json.dumps(event),
            })

        insert_rows(path_parts, rows_to_insert)

        resp = make_response('', 204)
        resp.headers = headers
        return resp

    return '<a href="https://github.com/ehfeng/chord">Chord</a>', 200
