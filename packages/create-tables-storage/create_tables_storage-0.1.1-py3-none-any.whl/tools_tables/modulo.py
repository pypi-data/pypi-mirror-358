from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils
from delta.tables import DeltaTable
import os

from work_infrastructure_data_avolta.src.utils.config import (
    scope_secrets,
    clave_servicio_bq,
    bq_project_id,
    uc_catalog,
    uc_schema,
    tables_json_path,
    bq_read_options,
    delta_write_options,
    write_mode,
    keypath,
    keypathmobile
)
from work_infrastructure_data_avolta.src.utils.library import Tools


def _get_dbutils(spark: SparkSession):
    try:
        return dbutils
    except NameError:
        return DBUtils(spark)


class CreateTables(Tools):
    def __init__(
        self,
        spark: SparkSession,
        storage_container: str,
        storage_base_path: str,
        # BigQuery params from config
        scope_secrets: str,
        clave_servicio_bq: str,
        bq_project_id: str,
        uc_catalog: str,
        uc_schema: str,
        tables_json_path: list,
        bq_read_options: dict,
        delta_write_options: dict,
        write_mode: str,
        keypath: str,
        keypathmobile: str,
    ):
        super().__init__(
            spark=spark,
            scope_secrets=scope_secrets,
            clave_servicio_bq=clave_servicio_bq,
            bq_project_id=bq_project_id,
            uc_catalog=uc_catalog,
            uc_schema=uc_schema,
            tables_json_path=tables_json_path,
            bq_read_options=bq_read_options,
            delta_write_options=delta_write_options,
            write_mode=write_mode,
            keypath=keypath,
            keypathmobile=keypathmobile
        )
        # Azure Data Lake parameters
        self.spark = spark
        self.dbutils = _get_dbutils(spark)
        self.container = storage_container
        self.mount_point = f"/mnt/{storage_container}"
        self.raw_folder = storage_base_path
        # Auth key for mounting
        self.auth_key = self.dbutils.secrets.get(scope_secrets, clave_servicio_bq)
        # Mount and load existing Delta tables
        self._mount_container()
        self._load_existing_tables()

    def _mount_container(self):
        source = f"abfss://{self.container}@{self.container}.dfs.core.windows.net/"
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

    def _unmount_container(self):
        try:
            self.dbutils.fs.unmount(self.mount_point)
            print(f"Unmounted container '{self.container}' from {self.mount_point}")
        except Exception as e:
            print(f"Error unmounting container '{self.container}': {e}")

    def _load_existing_tables(self):
        base_path = os.path.join(self.mount_point, self.raw_folder)
        for entry in tables_json_path:
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
        for entry in tables_json_path:
            bq_table = entry["bq_table"]
            uc_table = entry["uc_table"]
            target_path = os.path.join(self.mount_point, self.raw_folder, uc_table)

            # Skip if already Delta
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
        self._unmount_container()


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    tools = CreateTables(
        spark=spark,
        storage_container="stcprojectavolta",
        storage_base_path="tablesbigquery01",
        scope_secrets=scope_secrets,
        clave_servicio_bq=clave_servicio_bq,
        bq_project_id=bq_project_id,
        uc_catalog=uc_catalog,
        uc_schema=uc_schema,
        tables_json_path=tables_json_path,
        bq_read_options=bq_read_options,
        delta_write_options=delta_write_options,
        write_mode=write_mode,
        keypath=keypath,
        keypathmobile=keypathmobile
    )
    tools.migrate_tables()
