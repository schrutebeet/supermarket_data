import os
import subprocess
import inspect
import math
from typing import Any, List, Union
from itertools import compress

import pandas as pd
import psycopg2
import sqlalchemy

from config.log_config import logger
from database import models
from database.connection import SessionLocal, engine, settings
from database.models import create_dynamic_model


class UtilsDB:
    def __init__(self) -> None:
        self.engine = engine
        self.db_settings = settings
        self.dbsession = SessionLocal()

    def create_specific_model(
        self, class_name: str, model_name: str, schema_name: str, column_data: dict
    ) -> Any:
        """Create specific model inside specific schema.

        Args:
            class_name (str): Name of the class. Must be camel case - e.g.: 'AAPLDaily'.
            model_name (str): Name of the model. Must be snake case - e.g.: 'aapl_daily'.
            schema_name (str): Name of the schema where the model will be hosted.
            column_data (dict): Dictionary containing information on model columns: name, type, if primary key.
                                It must be of the type {'col1': Column(type, ...),
                                                        'col2': Column(type, ...),
                                                        'col3': Column(type, ...),
                                                         ...}

        Returns:
            object: Returns model class.
        """
        # Define the attributes for the class
        model_class = create_dynamic_model(
            class_name, model_name, schema_name, column_data
        )
        table_name = model_class.__tablename__
        schema_name = model_class.__table_args__["schema"]
        insp = sqlalchemy.inspect(self.engine)
        if not insp.has_table(table_name=table_name, schema=schema_name):
            model_class.__table__.create(self.engine)
            logger.info(
                f"Model '{model_name}' created successfully in schema '{schema_name}'."
            )
        return model_class

    def create_new_models(self) -> None:
        """Create all models found in database.models module, in case one of them is missing."""
        model_list = self.__get_all_classes("database.models")
        insp = sqlalchemy.inspect(self.engine)
        for cls in model_list:
            table_name = cls.__tablename__
            schema_name = cls.__table_args__["schema"]
            if not insp.has_table(table_name=table_name, schema=schema_name):
                cls.__table__.create(self.engine)
                logger.info(
                    f"Model '{table_name}' created successfully in schema '{schema_name}'."
                )

    @staticmethod
    def __get_all_classes(model_name: str) -> List[Any]:
        """Get a list with all models defined in the _model_name_ module."""
        all_items = inspect.getmembers(models)
        classes = [
            item[1]
            for item in all_items
            if inspect.isclass(item[1]) and item[1].__module__ == model_name
        ]
        return classes

    def get_model_class_with_name(self, table_name: str) -> object:
        model_list = self.__get_all_classes("database.models")
        for cls in model_list:
            if cls.__tablename__ == table_name:
                objective_cls = cls
        return objective_cls

    def insert_dict_in_db(
        self, data_dict: dict, model: object, batch_size: int = 10_000
    ) -> None:
        """Insert the input dataframe in the corresponding model in DB.

        Args:
            data_dict (dict): Input dictionary of which its information will be stored in the DB.
            model (object): Model class with table characteristics.
            batch_size (int, optional): Maximum rows to be inserted into the DB per iteration. Defaults to 100_000.
        """
        # Remove duplicates
        data_dict = self.remove_duplicate_ids(data_dict)
        list_of_dicts = [dict(zip(data_dict, t)) for t in zip(*data_dict.values())]
        batched_list_of_dicts = self._divide_dict_in_batches(list_of_dicts, batch_size)
        is_data_batched = len(batched_list_of_dicts) > 1
        logger.info(f"Starting data storage in DB for table '{model.__tablename__}'.")
        for idx, dict_batch in enumerate(batched_list_of_dicts):
            try:
                self.dbsession.bulk_insert_mappings(model, dict_batch)
                # Commit the changes to the database for each model
                self.dbsession.commit()
                if is_data_batched:
                    logger.info(
                    f"Batch number {idx + 1} of table '{model.__tablename__}' has been successfully stored in DB."
                    )
                else:
                    logger.info(
                        f"Table '{model.__tablename__}' has been successfully stored in DB."
                    )
            except sqlalchemy.exc.IntegrityError as e:
                logger.warning(
                    f"Duplicated primary key entries. Skipping. Error log: \n {e}"
                )
            except Exception as e:
                logger.error(
                    f"An error occurred when inserting data into database: {e}."
                )
        # Close connection
        self.dbsession.close()

    def remove_duplicate_ids(self, data_dict: dict) -> dict:
        # First, check if all values in the dictionary are of the same length
        len_keys = []
        for k, v in data_dict.items():
            len_key = len(v)
            len_keys.append(len_key)

        # Create an error log if size is not the same across elements in the list
        is_same = True
        for length in len_keys:
            if len_keys[0] != length:
                is_same = False
                break
        
        if is_same:
            logger.info(f"All values in the keys of the dictionary are of the same size: {len_keys[0]}")
            # Create mask so that the dict only contains unique ID's
            mask_list = []
            for idx, identifier in enumerate(data_dict['id']):
                if identifier not in data_dict['id'][:idx]:
                    mask_list.append(True)
                else:
                    mask_list.append(False)

            # Add unique entries in dictionary
            for k, v in data_dict.items():
                data_dict[k] = list(compress(v, mask_list))
        else:
            logger.error(f"Not all values in the keys of the dictionary are of the same size")
        return data_dict

    @staticmethod
    def _divide_dict_in_batches(
        input_dict: dict, batch_size: int
    ) -> List[List[dict]]:
        """Divide dictionary in smaller pieces for speed improvement."""
        n_chunks = math.ceil(len(input_dict) / batch_size)
        batched_list_of_dicts = []
        starting_row, ending_row = 0, batch_size
        for n in range(n_chunks):
            chunked_dict_list = input_dict[starting_row: ending_row]
            batched_list_of_dicts.append(chunked_dict_list)
            starting_row += batch_size
            ending_row += batch_size
        return batched_list_of_dicts

    def create_copy_of_db(self) -> None:

        # Path for the dump file
        dump_path = settings.BACKUP_COPY_PATH
        if os.name == "nt":     # Windows OS
            dump_command = [f"PGPASSWORD={self.db_settings.POSTGRES_PASSWORD}",
                            "pg_dump.exe",
                            "-U", self.db_settings.POSTGRES_USER,
                            "-h", self.db_settings.POSTGRES_HOST,
                            self.db_settings.POSTGRES_DATABASE,
                            ">",
                            settings.BACKUP_COPY_PATH]
        else:                   # Linux
            dump_command = ["pg_dump",
                            "-U", self.db_settings.POSTGRES_USER,
                            "-h", self.db_settings.POSTGRES_HOST,
                            "-f", dump_path,
                            self.db_settings.POSTGRES_DATABASE]

        # Execute the dump command
        subprocess.run(dump_command, check=True)
