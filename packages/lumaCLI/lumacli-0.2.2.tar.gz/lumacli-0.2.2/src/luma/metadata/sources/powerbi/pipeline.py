from luma.metadata.sources.powerbi.extract import powerbi
from luma.metadata.sources.powerbi.models import WorkspaceInfo
from luma.metadata.sources.powerbi.transform import transform


def pipeline():
    source = powerbi()
    metadata = WorkspaceInfo(**next(iter(source)))
    yield transform(metadata)


if __name__ == "__main__":
    manifest = next(iter(pipeline()))
    # print(manifest)
