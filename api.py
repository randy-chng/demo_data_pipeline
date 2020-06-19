import os
import logging
import flask

from flask import request, jsonify
from db_controller import run_query

app = flask.Flask(__name__)


# Function to check and run SQL statement
# Better to use read only user to query
# Limiting large results?
def _run_query(api_input):

    sql_stmt = api_input['sql']

    api_output = {
        'input': api_input,
        'error_msg': None,
        'results': None
    }

    # Check if input is a string
    if not(isinstance(sql_stmt, str)):

        api_output['error_msg'] = 'Expecting String Input'

        return api_output

    # Check at high level if input is a validate select statement
    # More can be done
    if not(sql_stmt.startswith('select')):

        api_output['error_msg'] = 'Not a Select Statement'

        return api_output

    # Run SQL statement
    if api_output['error_msg'] is None:

        status, result, err = run_query(sql_stmt)

        if status:

            api_output['results'] = result

        else:

            api_output['error_msg'] = err

        return api_output


# Function to get most outdated page by category
def _get_most_outdated_page(api_input):

    category = api_input['category']

    api_output = {
        'input': api_input,
        'error_msg': None,
        'results': None
    }

    # Better to have some checks on input

    # Run SQL statement
    if api_output['error_msg'] is None:

        status, result, err = run_query(
            'select * from most_outdated_page_in_top_category where cat_title = \'{}\''.format(
                category
            )
        )

        if status:

            api_output['results'] = result

        else:

            api_output['error_msg'] = err

    return api_output


# API Listener
@app.route('/api/v1/resources/query', methods=['GET'])
def api_run_query():

    api_fields = [
        'sql'
    ]

    missing_input = [
        _
        for _ in api_fields
        if _ not in request.args
    ]

    if not missing_input:

        api_output = _run_query(request.args)

    else:

        logging.warning('Missing {} input(s)'.format(missing_input))

        api_output = {
            'input': request.args,
            'error_msg': 'Missing {} input(s)'.format(','.join(missing_input)),
            'results': None
        }
    
    return jsonify(api_output)


# API Listener
@app.route('/api/v1/resources/outdated', methods=['GET'])
def api_most_outdated_page():

    api_fields = [
        'category'
    ]

    missing_input = [
        _
        for _ in api_fields
        if _ not in request.args
    ]

    if not missing_input:

        api_output = _get_most_outdated_page(request.args)

    else:

        logging.warning('Missing {} input(s)'.format(missing_input))

        api_output = {
            'input': request.args,
            'error_msg': 'Missing {} input(s)'.format(','.join(missing_input)),
            'results': None
        }

    return jsonify(api_output)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.join(
            os.getcwd(),
            'logs',
            'api.log'
        ),
        filemode='a',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    from waitress import serve
    from paste.translogger import TransLogger

    serve(TransLogger(app, setup_console_handler=False), host='0.0.0.0', port=5000)
