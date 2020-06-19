# Imports
import os
import glob
import urllib.request
import shutil
import gzip
import logging

from datetime import datetime
from db_controller import create_schema, load_sql_dump, run_query


def download_sql_dump():

    # List of tables
    # From https://meta.wikimedia.org/wiki/Data_dumps/What%27s_available_for_download#Database_tables
    tables = [
        'categorylinks',
        'category',
        'page',
        'pagelinks'
    ]

    # For each table, download SQL dump file
    # From https://dumps.wikimedia.org/simplewiki/latest/
    for _ in tables:

        filename = 'simplewiki-latest-{}.sql.gz'.format(_)

        url = 'https://dumps.wikimedia.org/simplewiki/latest/{}'.format(filename)

        logging.info('Download {}'.format(url))

        save_path = os.path.join(dump_dir, filename)

        try:

            with urllib.request.urlopen(url) as response, open(save_path, 'wb') as out_file:

                logging.info('Response {}'.format(response.status))

                shutil.copyfileobj(response, out_file)

            logging.info('Saved {}'.format(save_path))

        except urllib.error.HTTPError as e:

            logging.warning(e)


def uncompress_sql_dump():

    downloaded_dumps_location = glob.glob(
        os.path.join(dump_dir, '*.gz')
    )

    for _ in downloaded_dumps_location:

        logging.info('Uncompressing {}'.format(_))

        new_location = _[:-3]

        try:

            with gzip.open(_, 'rb') as f_in:

                with open(new_location, 'wb') as f_out:

                    shutil.copyfileobj(f_in, f_out)

        except Exception as e:

            logging.warning(e)


def load_sql_dump_files():

    uncompressed_dumps_location = glob.glob(
        os.path.join(dump_dir, '*.sql')
    )

    for _ in uncompressed_dumps_location:

        logging.info('Load {}'.format(_))

        output = load_sql_dump(_)

        # 0 means successful
        logging.info('Outcome {}'.format(output.returncode))


def preprocess_most_outdated_page_by_category():

    try:

        logging.info('Generate table outdated_pages_in_top_category')

        run_query('drop table if exists outdated_pages_in_top_category')

        run_query(
            ' \
            create table outdated_pages_in_top_category ( \
                pl_from_page_id int, \
                pl_from_page_title varbinary(255), \
                pl_from_page_touched varbinary(14), \
                pl_page_id int, \
                pl_page_title varbinary(255), \
                pl_page_touched varbinary(14), \
                page_touched_diff double, \
                cat_id int, \
                cat_title varbinary(255), \
                cat_pages int \
            )')

        run_query(
            ' \
            insert into outdated_pages_in_top_category \
            select \
                b.page_id as pl_from_page_id, \
                b.page_title as pl_from_page_title, \
                b.page_touched as pl_from_page_touched, \
                c.page_id as pl_page_id, \
                c.page_title as pl_page_title, \
                c.page_touched as pl_page_touched, \
                b.page_touched - c.page_touched as page_touched_diff, \
                e.cat_id, \
                e.cat_title as cat_title, \
                e.cat_pages \
            from pagelinks a \
            inner join ( \
                select page_id, page_title, page_touched \
                from page \
            ) b on a.pl_from = b.page_id \
            inner join ( \
                select page_id, page_title, page_namespace, page_touched \
                from page \
            ) c on a.pl_title = c.page_title and a.pl_namespace = c.page_namespace \
            inner join ( \
                select cl_from, cl_to \
                from categorylinks \
            ) d on a.pl_from = d.cl_from \
            inner join ( \
                select cat_id, cat_title, cat_pages \
                from category \
                order by cat_pages desc \
                limit 10 \
            ) e on d.cl_to = e.cat_title \
            where b.page_touched < c.page_touched',
            True
        )

        logging.info('Generate table most_outdated_page_in_top_category')

        run_query('drop table if exists most_outdated_page_in_top_category')

        run_query(
            ' \
            create table most_outdated_page_in_top_category ( \
                pl_from_page_id int, \
                pl_from_page_title varbinary(255), \
                pl_from_page_touched varbinary(14), \
                pl_page_id int, \
                pl_page_title varbinary(255), \
                pl_page_touched varbinary(14), \
                page_touched_diff double, \
                cat_id int, \
                cat_title varbinary(255), \
                cat_pages int \
            )'
        )

        # Window function not available in gcp cloud sql mysql version 5.7
        # Replaced to old school implementation
        run_query(
            ' \
            insert into most_outdated_page_in_top_category \
            select a.* \
            from outdated_pages_in_top_category a \
            inner join ( \
                select cat_id, min(page_touched_diff) as min_page_touched_diff \
                from outdated_pages_in_top_category \
                group by cat_id \
            ) b on a.cat_id = b.cat_id and a.page_touched_diff = b.min_page_touched_diff \
            ',
            True
        )

    except Exception as e:

        logging.warning(e)


if __name__ == '__main__':

    global dump_dir
    dump_dir = os.path.join(os.getcwd(), 'dump')

    now = datetime.now()

    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.join(
            os.getcwd(),
            'logs',
            '{}_data_pipeline.log'.format(now.strftime('%Y%m%d_%H%M%S'))
        ),
        filemode='a',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    download_sql_dump()

    uncompress_sql_dump()

    create_schema()

    load_sql_dump_files()

    preprocess_most_outdated_page_by_category()
