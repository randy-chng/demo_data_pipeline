import os
import subprocess
import mysql.connector
import yaml
import pandas as pd


def get_env():

    with open('db_details.yaml', 'r') as stream:

        db_details = yaml.safe_load(stream)

    if os.name == 'nt':

        db_details['exe_loc'] = '"C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe"'

    else:

        db_details['exe_loc'] = 'mysql'

    return db_details


def open_connection():

    db_details = get_env()

    try:

        cnx = mysql.connector.connect(
            user=db_details['user'],
            password=db_details['pw'],
            host=db_details['host']
        )

        return True, cnx, None

    except mysql.connector.Error as e:

        print(e.msg)

        return False, None, e.msg


def create_schema():

    db_details = get_env()

    status, cnx, err = open_connection()

    if status:

        cursor = cnx.cursor()

        cursor.execute(
            'create schema if not exists {}'.format(
                db_details['db']
            )
        )

        cursor.close()

        cnx.close()

    else:

        print('No schema created')


def load_sql_dump(sql_dump):

    db_details = get_env()

    output = subprocess.run(
        '{} {} {} {} {} < "{}"'.format(
            db_details['exe_loc'],
            '-D {}'.format(db_details['db']),
            '-u {}'.format(db_details['user']),
            '-p{}'.format(db_details['pw']),
            '-h {}'.format(db_details['host']),
            sql_dump
        ),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return output


def run_query(sql_stmt, commit=False):

    db_details = get_env()

    result = []

    status, cnx, err = open_connection()

    if status:

        try:

            cursor = cnx.cursor()

            cursor.execute('use {}'.format(db_details['db']))

            cursor.execute(sql_stmt)

            if commit:

                cnx.commit()

            if cursor.column_names:

                df = pd.DataFrame(
                    data=[_ for _ in cursor],
                    columns=cursor.column_names
                )

                result = df.to_dict('records')

            cursor.close()

            cnx.close()

            return True, result, None

        except mysql.connector.Error as e:

            print(e.msg)

            return False, result, e.msg

    else:

        return False, result, err


if __name__ == '__main__':

    print('Attempting to extract available schemas')

    status, result, err = run_query('show schemas')

    if status:

        for _ in result:

            print(_)

    else:

        print(err)
