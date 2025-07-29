from ..csv_exporter import CsvExporter
from ..json_exporter import JsonExporter
from ..mssql_exporter import MssqlExporter
from ..mysql_exporter import MysqlExporter
from ..oracle_exporter import OracleExporter
from ..orc_exporter import OrcExporter
from ..parquet_exporter import ParquetExporter

EXPORTER_CLASSES = {
    "csv": CsvExporter(),
    "json": JsonExporter(),
    "parquet": ParquetExporter(),
    "orc": OrcExporter(),
    "mysql": MysqlExporter(),
    "mssql": MssqlExporter(),
    "oracle": OracleExporter(),
}
