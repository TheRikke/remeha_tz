import logging
import mysql.connector

import remeha_core
from datamap import datamap
from remeha_core import FrameDecoder

log = logging.getLogger(__name__)


class DatabaseLogger:

    def __init__(self):
        self.database_name = "boiler_log"
        self.table_name = "boiler_data"
        self.database = self.check_and_init_db()
        self.insert_cursor = self.database.cursor(prepared=True)
        self.prepared_query = {}
        self.number_of_uncommitted_records = 0
        self.frame_decoder = FrameDecoder()

    def check_and_init_db(self):
        # CREATE USER 'currentuser' IDENTIFIED BY ';osdr90378a';
        # CREATE DATABASE power_log;
        # GRANT ALL privileges ON power_log.* TO 'currentuser';

        mydb = mysql.connector.connect(
            host="odroid",
            user="currentuser",
            passwd=";osdr90378a"
        )

        db_cursor = mydb.cursor()
        db_cursor.execute("SHOW DATABASES LIKE '%s'" % self.database_name)
        if not db_cursor.with_rows or not db_cursor.fetchall():
            log.info("Database not found. Create %s" % self.database_name)
            db_cursor.reset()
            db_cursor.execute("CREATE DATABASE %s" % self.database_name)
        db_cursor.reset()

        mydb = mysql.connector.connect(
            host="odroid",
            user="currentuser",
            passwd=";osdr90378a",
            database=self.database_name
        )

        db_cursor = mydb.cursor()
        db_cursor.execute("SHOW TABLES LIKE '%s'" % self.table_name)

        if not db_cursor.with_rows or not db_cursor.fetchall():
            log.error("Table not found. Create %s" % self.table_name)
            db_cursor.reset()
            sql_query = ''
            for val_name in self.get_type_names():
                sql_query += "%s FLOAT," % val_name
            # uncomment if we need to remove the last separator
            # sql_query = sql_query[0:-1]
            sql_query = "CREATE TABLE %s (time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, %s whole_frame TINYBLOB);"\
                        % (self.table_name, sql_query)
            log.debug(sql_query)
            # print(sql_query)
            db_cursor.execute(sql_query)
        db_cursor.close()
        return mydb

    def get_type_names(self):
        for n, x in enumerate(datamap):
            #        print("Value: " + str(value))
            if isinstance(datamap[n][2], list):
                for sub_index, sub_value in enumerate(datamap[n][2]):
                    # if i[0]:
                    type_name = datamap[n][2][sub_index]
                    log.debug('subindex %s' % type_name)
                    if type_name.startswith('unknown'):
                        continue
                    yield type_name
            else:
                type_name = datamap[n][2]
                log.debug(type_name)
                if type_name.startswith('unknown'):
                    continue
                yield type_name

    def log_data(self, frame):
        unpacked_data = {i[0]: i[1] for i in list(remeha_core.parse_data(frame.get_parseddata())) if not i[0].startswith('unknown')}
        number_of_values = len(unpacked_data)
        if number_of_values not in self.prepared_query:
            sql_query = 'INSERT INTO {} ({}, whole_frame) VALUES ({}, %s)'.format(
                self.table_name,
                ', '.join(unpacked_data.keys()),
                ', '.join(['%s'] * number_of_values)
            )
            # print(sql_query)
            self.prepared_query[number_of_values] = sql_query
            log.debug(sql_query)
        else:
            sql_query = self.prepared_query[number_of_values]

        value_list = *unpacked_data.values(),frame.get_data()
        log.debug(value_list)
        self.insert_cursor.execute(sql_query, value_list)
        self.number_of_uncommitted_records += 1
        if self.number_of_uncommitted_records > 80:
            self.database.commit()
            self.number_of_uncommitted_records = 0

    def close(self):
        if self.number_of_uncommitted_records > 0:
            log.info("Ctr-c detected. Write remaining data.")
            self.database.commit()
            self.number_of_uncommitted_records = 0
            self.database.close()

