import dlt

from luma.metadata.sources import qlik_sense


pipe = dlt.pipeline(
    pipeline_name="qlik_to_duckdb",
    destination=dlt.destinations.duckdb("db.duckdb"),
    dataset_name="qlik_sense",
)
# load_package = pipe.run(qlik().add_limit(5), refresh="drop_data") # For testing.
load_package = pipe.run(qlik_sense().add_limit(5))
print(load_package)
