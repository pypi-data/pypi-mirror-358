from scontoolkit.interfaces.catalog import ICatalogService
from scontoolkit.models.dsp.catalog import Dataset


class CKANCatalogService(ICatalogService):
    def __init__(self):
        self._datasets = {
            "dataset-1": Dataset(id="dataset-1", title="Example Dataset", description="A demo dataset")
        }

    def create_dataset(self, dataset: Dataset) -> str:
        self._datasets[dataset.id] = dataset
        return dataset.id

    def get_dataset(self, dataset_id: str) -> Dataset:
        return self._datasets[dataset_id]

    def list_datasets(self) -> list[Dataset]:
        return list(self._datasets.values())

    def delete_dataset(self, dataset_id: str) -> bool:
        return self._datasets.pop(dataset_id, None) is not None
