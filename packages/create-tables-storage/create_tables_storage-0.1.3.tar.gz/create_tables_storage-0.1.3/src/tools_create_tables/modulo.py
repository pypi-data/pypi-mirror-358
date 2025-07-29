import logging
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils
from delta.tables import DeltaTable

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _get_dbutils(spark: SparkSession):
    try:
        return dbutils  # cuando ya existe en el entorno
    except NameError:
        return DBUtils(spark)


class CreateTables:
    def __init__(
        self,
        spark: SparkSession,
        tables_json_path: list,
        bq_project_id: str,
        *,
        storage_container: str = 'stcprojectavolta',
        storage_base_path: str = 'tablesbigquery01',
        bq_read_options: dict = None,
        delta_write_options: dict = None,
        write_mode: str = "overwrite",
        secret_scope: str = None,
        secret_key: str = None,
        authentication_key: str = None,
        tenant_id: str = None,
        app_id: str = None,
    ):
        self.spark = spark
        self.dbutils = _get_dbutils(spark)
        self.container = storage_container
        self.mount_point = Path(f"/mnt/{storage_container}")
        self.raw_folder = Path(storage_base_path)
        self.tables_json_path = tables_json_path
        self.bq_project_id = bq_project_id
        self.bq_read_options = bq_read_options or {}
        self.delta_write_options = delta_write_options or {}
        self.write_mode = write_mode

        # Autenticación
        if secret_scope and secret_key:
            self.auth_key = self.dbutils.secrets.get(secret_scope, secret_key)
        elif authentication_key:
            self.auth_key = authentication_key
        else:
            raise ValueError("Proporciona 'authentication_key' o ('secret_scope' y 'secret_key')")

        if not tenant_id or not app_id:
            raise ValueError("Debes proporcionar 'tenant_id' y 'app_id' para la conexión OAuth")
        self.tenant_id = tenant_id
        self.app_id = app_id
        self.gcp_credentials = authentication_key

        # Montar y cargar
        self._mount_container()
        self._load_tables()

    def _mount_container(self):
        source = f"abfss://{self.container}@{self.container}.dfs.core.windows.net/"
        mounts = [m.mountPoint for m in self.dbutils.fs.mounts()]
        if str(self.mount_point) in mounts:
            logger.info("El contenedor ya está montado en %s", self.mount_point)
            return

        endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
        configs = {
            "fs.azure.account.auth.type": "OAuth",
            "fs.azure.account.oauth.provider.type":
                "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            "fs.azure.account.oauth2.client.id": self.app_id,
            "fs.azure.account.oauth2.client.secret": self.auth_key,
            "fs.azure.account.oauth2.client.endpoint": endpoint
        }
        try:
            self.dbutils.fs.mount(
                source=source,
                mount_point=str(self.mount_point),
                extra_configs=configs
            )
            logger.info("Montado '%s' en '%s'", self.container, self.mount_point)
        except Exception as e:
            logger.error("Error montando '%s': %s", self.container, e)
            raise

    def _load_tables(self):
        base_path = self.mount_point / self.raw_folder
        for entry in self.tables_json_path:
            name = entry["uc_table"]
            path = base_path / name
            try:
                df = self.spark.read.format("delta").load(str(path))
                setattr(self, f"df_{name}", df)
                df.createOrReplaceTempView(name)
                logger.info("Cargada tabla Delta '%s' desde %s", name, path)
            except Exception as e:
                logger.warning("No se pudo cargar '%s' en %s: %s", name, path, e)

    def migrate_tables(self):
        base_path = self.mount_point / self.raw_folder
        for entry in self.tables_json_path:
            bq_table = entry["bq_table"]
            uc_table = entry["uc_table"]
            target = base_path / uc_table

            # Si ya existe como Delta, saltar
            if DeltaTable.isDeltaTable(self.spark, str(target)):
                logger.info("Saltando %s: ya existe Delta en %s", bq_table, target)
                continue

            logger.info("Leyendo %s de BigQuery...", bq_table)
            reader = (
                self.spark.read
                    .format("bigquery")
                    .option("table", bq_table)
                    .option("parentProject", self.bq_project_id)
                    .option("credentials", self.gcp_credentials)
            ).options(**self.bq_read_options)
            df = reader.load().limit(1000)

            logger.info("Escribiendo Delta en %s...", target)
            writer = df.write.format("delta").mode(self.write_mode).options(**self.delta_write_options)
            writer.save(str(target))

            count = df.count()
            logger.info("Migrado %s (%d filas) → %s", bq_table, count, target)

    def unmount(self):
        try:
            self.dbutils.fs.unmount(str(self.mount_point))
            logger.info("Desmontado %s", self.mount_point)
        except Exception as e:
            logger.error("Error desmontando %s: %s", self.mount_point, e)
            raise



# from pyspark.sql import SparkSession
# from pyspark.dbutils import DBUtils
# from delta.tables import DeltaTable
# import os


# def _get_dbutils(spark: SparkSession):
#     try:
#         return dbutils
#     except NameError:
#         return DBUtils(spark)


# class CreateTables:
#     def __init__(
#         self,
#         spark: SparkSession,
#         storage_container: str, 
#         storage_base_path: str,
#         tables_json_path: list,
#         bq_project_id: str,
#         bq_read_options: dict = None,
#         delta_write_options: dict = None,
#         write_mode: str = "overwrite",
#         secret_scope: str = None,
#         secret_key: str = None,
#         authentication_key: str = None,
#     ):
#         self.spark = spark
#         self.dbutils = _get_dbutils(spark)
#         self.container = storage_container
#         self.mount_point = f"/mnt/{storage_container}"
#         self.raw_folder = storage_base_path
#         self.tables_json_path = tables_json_path
#         self.bq_project_id = bq_project_id
#         self.bq_read_options = bq_read_options or {}
#         self.delta_write_options = delta_write_options or {}
#         self.write_mode = write_mode

#         # Determine authentication key for mounting
#         if secret_scope and secret_key:
#             self.auth_key = self.dbutils.secrets.get(secret_scope, secret_key)
#         elif authentication_key:
#             self.auth_key = authentication_key
#         else:
#             raise ValueError("Se debe proporcionar 'authentication_key' o ('secret_scope' y 'secret_key')")

#         # Use the same key for GCP credentials if applicable
#         self.gcp_credentials = authentication_key

#         # Mount container and load tables
#         self._mount_container()
#         self._load_tables()

#     def _mount_container(self):
#         source = f"abfss://{self.container}@{self.container}.dfs.core.windows.net/"
#         mounted = [m.mountPoint for m in self.dbutils.fs.mounts()]
#         if self.mount_point in mounted:
#             print(f"Container '{self.container}' already mounted at {self.mount_point}")
#             return
#         endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
#         configs = {
#             "fs.azure.account.auth.type": "OAuth",
#             "fs.azure.account.oauth.provider.type": \
#                 "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
#             "fs.azure.account.oauth2.client.id": self.app_id,
#             "fs.azure.account.oauth2.client.secret": self.auth_key,
#             "fs.azure.account.oauth2.client.endpoint": endpoint
#         }
#         try:
#             self.dbutils.fs.mount(
#                 source=source,
#                 mount_point=self.mount_point,
#                 extra_configs=configs
#             )
#             print(f"Mounted '{self.container}' at {self.mount_point}")
#         except Exception as e:
#             print(f"Error mounting container '{self.container}': {e}")

#     def _load_tables(self):
#         base_path = os.path.join(self.mount_point, self.raw_folder)
#         for entry in self.tables_json_path:
#             uc_table = entry.get("uc_table")
#             delta_path = os.path.join(base_path, uc_table)
#             try:
#                 df = self.spark.read.format("delta").load(delta_path)
#                 setattr(self, f"df_{uc_table}", df)
#                 df.createOrReplaceTempView(uc_table)
#                 print(f"Loaded Delta table '{uc_table}' from {delta_path}")
#             except Exception as e:
#                 print(f"Error loading table '{uc_table}' from {delta_path}: {e}")

#     def migrate_tables(self):
#         for entry in self.tables_json_path:
#             bq_table = entry["bq_table"]
#             uc_table = entry["uc_table"]
#             target_path = os.path.join(self.mount_point, self.raw_folder, uc_table)

#             try:
#                 if DeltaTable.isDeltaTable(self.spark, target_path):
#                     print(f"Skipping {bq_table}: Delta table exists at {target_path}")
#                     continue
#             except Exception:
#                 pass

#             print(f"Reading {bq_table} from BigQuery...")
#             reader = (
#                 self.spark.read
#                     .format("bigquery")
#                     .option("table", bq_table)
#                     .option("parentProject", self.bq_project_id)
#                     .option("credentials", self.gcp_credentials)
#             )
#             if self.bq_read_options:
#                 reader = reader.options(**self.bq_read_options)
#             df = reader.load().limit(1000)

#             print(f"Writing to Delta at {target_path}...")
#             writer = df.write.format("delta").mode(self.write_mode)
#             if self.delta_write_options:
#                 writer = writer.options(**self.delta_write_options)
#             writer.save(target_path)

#             count = df.count()
#             print(f"Migrated {bq_table} ({count} rows) → {target_path}\n")

#     def unmount(self):
#         try:
#             self.dbutils.fs.unmount(self.mount_point)
#             print(f"Unmounted container '{self.container}' from {self.mount_point}")
#         except Exception as e:
#             print(f"Error unmounting container '{self.container}': {e}")



