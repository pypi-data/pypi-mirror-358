from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils
from delta.tables import DeltaTable
import os


def _get_dbutils(spark: SparkSession):
    try:
        return dbutils
    except NameError:
        return DBUtils(spark)


class CreateTables:
    def __init__(
        self,
        spark: SparkSession,
        tables_json_path: list,
        bq_read_options: dict = None,
        delta_write_options: dict = None,
        write_mode: str = "overwrite",
        secret_scope: str = None,
        secret_key: str = None,
        authentication_key: str = None,
        storage_container: str = 'stcprojectavolta',
        storage_base_path: str = 'tablesbigquery01',
        application_id: str = 'dd627f0a-9742-4307-8851-bc16e8d2bae7',
        tenant_id: str = 'fcc7aafa-b643-4510-955d-3374a25d0f41',
        bq_project_id : str = 'ntech-dufry-databasecualif'
    ):
        self.spark = spark
        self.dbutils = _get_dbutils(spark)
        self.container = storage_container
        self.mount_point = f"/mnt/{storage_container}"
        self.raw_folder = storage_base_path
        self.tables_json_path = tables_json_path
        self.bq_project_id = bq_project_id
        self.bq_read_options = bq_read_options or {}
        self.delta_write_options = delta_write_options or {}
        self.write_mode = write_mode
        self.app_id = application_id
        self.tenant_id = tenant_id

        # Determine authentication key for mounting
        if secret_scope and secret_key:
            self.auth_key = self.dbutils.secrets.get(secret_scope, secret_key)
        elif authentication_key:
            self.auth_key = authentication_key
        else:
            raise ValueError("Se debe proporcionar 'authentication_key' o ('secret_scope' y 'secret_key')")

        # Use the same key for GCP credentials if applicable
        self.gcp_credentials = authentication_key

        # Mount container and load tables
        self._mount_container()
        self._load_tables()

    def _mount_container(self):
        source = f"abfss://{self.container}@stcprojectlab001.dfs.core.windows.net/"
        mounted = [m.mountPoint for m in self.dbutils.fs.mounts()]
        if self.mount_point in mounted:
            print(f"Container '{self.container}' already mounted at {self.mount_point}")
            return
        endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
        configs = {
            "fs.azure.account.auth.type": "OAuth",
            "fs.azure.account.oauth.provider.type": \
                "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            "fs.azure.account.oauth2.client.id": self.app_id,
            "fs.azure.account.oauth2.client.secret": self.auth_key,
            "fs.azure.account.oauth2.client.endpoint": endpoint
        }
        try:
            self.dbutils.fs.mount(
                source=source,
                mount_point=self.mount_point,
                extra_configs=configs
            )
            print(f"Mounted '{self.container}' at {self.mount_point}")
        except Exception as e:
            print(f"Error mounting container '{self.container}': {e}")

    def _load_tables(self):
        base_path = os.path.join(self.mount_point, self.raw_folder)
        for entry in self.tables_json_path:
            uc_table = entry.get("uc_table")
            delta_path = os.path.join(base_path, uc_table)
            try:
                df = self.spark.read.format("delta").load(delta_path)
                setattr(self, f"df_{uc_table}", df)
                df.createOrReplaceTempView(uc_table)
                print(f"Loaded Delta table '{uc_table}' from {delta_path}")
            except Exception as e:
                print(f"Error loading table '{uc_table}' from {delta_path}: {e}")

    def migrate_tables(self):
        for entry in self.tables_json_path:
            bq_table = entry["bq_table"]
            uc_table = entry["uc_table"]
            target_path = os.path.join(self.mount_point, self.raw_folder, uc_table)

            try:
                if DeltaTable.isDeltaTable(self.spark, target_path):
                    print(f"Skipping {bq_table}: Delta table exists at {target_path}")
                    continue
            except Exception:
                pass

            print(f"Reading {bq_table} from BigQuery...")
            reader = (
                self.spark.read
                    .format("bigquery")
                    .option("table", bq_table)
                    .option("parentProject", self.bq_project_id)
                    .option("credentials", self.gcp_credentials)
            )
            if self.bq_read_options:
                reader = reader.options(**self.bq_read_options)
            df = reader.load().limit(1000)

            print(f"Writing to Delta at {target_path}...")
            writer = df.write.format("delta").mode(self.write_mode)
            if self.delta_write_options:
                writer = writer.options(**self.delta_write_options)
            writer.save(target_path)

            count = df.count()
            print(f"Migrated {bq_table} ({count} rows) → {target_path}\n")

    def unmount(self):
        try:
            self.dbutils.fs.unmount(self.mount_point)
            print(f"Unmounted container '{self.container}' from {self.mount_point}")
        except Exception as e:
            print(f"Error unmounting container '{self.container}': {e}")



