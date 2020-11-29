import logging
import mysql.connector

import remeha_core
from datamap import datamap
from remeha_core import FrameDecoder

log = logging.getLogger(__name__)


class DatabaseLogger:
    def __init__(self, config):
        self.database = None
        if config and 'database_logger' in config:
            self.database_name = "boiler_log"
            self.table_name = "boiler_data"
            self.database = self.__check_and_init_db(config['database_logger'])
            if self.database:
                self.insert_cursor = self.database.cursor(prepared=True)
                self.prepared_query = {}
                self.number_of_uncommitted_records = 0
                self.frame_decoder = FrameDecoder()

    def __check_and_init_db(self, database_config):
        # CREATE USER 'currentuser' IDENTIFIED BY ';osdr90378a';
        # CREATE DATABASE power_log;
        # GRANT ALL privileges ON power_log.* TO 'currentuser';
        remeha_db = None
        if 'enabled' in database_config and database_config['enabled']:
            if 'config_file' in database_config:
                remeha_db = mysql.connector.connect(
                    option_files=database_config['config_file']
                )
            elif 'host' in database_config and 'user_name' in database_config and 'password' in database_config:
                try:
                    remeha_db = mysql.connector.connect(
                        host=database_config['host'],
                        user=database_config['user_name'],
                        passwd=database_config['password']
                    )
                except mysql.connector.errors.ProgrammingError as error:
                    log.error('Could not access database: %s' % error)
            else:
                log.error("Database config incomplete.")
        else:
            log.info('Logging to database disabled in config')

        if remeha_db:
            db_cursor = remeha_db.cursor()
            db_cursor.execute("SHOW DATABASES LIKE '%s'" % self.database_name)
            if not db_cursor.with_rows or not db_cursor.fetchall():
                log.info("Database not found. Create %s" % self.database_name)
                db_cursor.reset()
                db_cursor.execute("CREATE DATABASE %s" % self.database_name)
            db_cursor.reset()

            remeha_db.cmd_init_db(self.database_name)

            db_cursor = remeha_db.cursor()
            db_cursor.execute("SHOW TABLES LIKE '%s'" % self.table_name)

            if not db_cursor.with_rows or not db_cursor.fetchall():
                log.error("Table not found. Create %s" % self.table_name)
                db_cursor.reset()
                sql_query = ''
                for val_name in self.get_type_names():
                    sql_query += "{} {},".format(val_name[0], val_name[1])

                # uncomment if we need to remove the last separator
                # sql_query = sql_query[0:-1]
                sql_query = "CREATE TABLE %s (time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, %s whole_frame TINYBLOB);"\
                            % (self.table_name, sql_query)
                log.debug(sql_query)
                # print(sql_query)
                db_cursor.execute(sql_query)

                # create tables for mapped values or if exists check for correct mapping. otherwise add new mapping
                for data in datamap:
                    if isinstance(data[4], dict):
                        table_name = '{}_mapped'.format(data[2])
                        db_cursor.execute("SHOW TABLES LIKE '{}'".format(table_name))
                        if not db_cursor.with_rows or not db_cursor.fetchall():
                            create_mapped_query = "CREATE TABLE %s (value INT KEY, name TINYTEXT);" % table_name
                            db_cursor.execute(create_mapped_query)
                            table_data = ""
                            for mapping_value in data[4]:
                                table_data += "({},'{}'),".format(mapping_value, data[4][mapping_value])
                            table_data = table_data[0:-1] + ';'
                            insert_mapped_query = 'INSERT INTO {} (value,name) VALUES {})'.format(table_name, table_data)
                            db_cursor.execute(insert_mapped_query)

            db_cursor.close()
        return remeha_db

    @staticmethod
    def get_type_names():
        for n, x in enumerate(datamap):
            if isinstance(datamap[n][2], list):
                for sub_index, sub_value in enumerate(datamap[n][2]):
                    type_name = datamap[n][2][sub_index]
                    if type_name.startswith('unknown'):
                        continue
                    yield type_name, 'BOOL'
            elif isinstance(datamap[n][4], dict):
                type_name = datamap[n][2]
                log.debug(type_name)
                if type_name.startswith('unknown'):
                    continue
                yield type_name, 'TINYINT UNSIGNED'
            else:
                type_name = datamap[n][2]
                log.debug(type_name)
                if type_name.startswith('unknown'):
                    continue
                yield type_name, 'FLOAT'

    def log_data(self, frame):
        if self.database:
            unpacked_data = {i[0]: i[1] for i in list(remeha_core.parse_data(frame.get_parseddata(), map_resolve=False))
                             if not i[0].startswith('unknown')}
            number_of_values = len(unpacked_data)
            if number_of_values not in self.prepared_query:
                sql_query = 'INSERT INTO {} ({}, whole_frame) VALUES ({}, %s)'.format(
                    self.table_name,
                    ', '.join(unpacked_data.keys()),
                    ', '.join(['%s'] * number_of_values)
                )
                self.prepared_query[number_of_values] = sql_query
                log.debug(sql_query)
            else:
                sql_query = self.prepared_query[number_of_values]

            value_list = *unpacked_data.values(), frame.get_data()
            log.debug(value_list)
            self.insert_cursor.execute(sql_query, value_list)
            self.number_of_uncommitted_records += 1
            if self.number_of_uncommitted_records > 80:
                self.database.commit()
                self.number_of_uncommitted_records = 0

    def retrieve_data(self, query):
        self.insert_cursor.execute(query)
        return self.insert_cursor

    def close(self):
        if self.database and self.number_of_uncommitted_records > 0:
            log.info("Ctr-c detected. Write remaining data.")
            self.database.commit()
            self.number_of_uncommitted_records = 0
            self.database.close()
