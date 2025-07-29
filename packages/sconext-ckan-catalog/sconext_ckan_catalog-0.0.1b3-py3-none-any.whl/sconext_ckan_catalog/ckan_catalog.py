from scontoolkit.interfaces.catalog import ICatalogService
from scontoolkit.models.dsp.catalog import Dataset
from uuid import uuid4
from scontoolkit.models.dsp.catalog import Dataset
from scontoolkit.models.dsp.low_level import Distribution, Offer

dummy_dataset = Dataset(
    id=f"urn:uuid:{uuid4()}",
    distribution=[
        Distribution(
            accessService="urn:uuid:dataservice-1",
            format="application/json",
            hasPolicy=[
                Offer(
                    id="urn:uuid:offer-1",
                    permission=[],
                    profile=["https://w3id.org/idsa/code/EULicense"],
                    prohibition=[],
                    obligation=[]
                )
            ]
        )
    ],
    hasPolicy=[
        Offer(
            id="urn:uuid:offer-2",
            permission=[],
            profile=["https://w3id.org/idsa/code/EULicense"],
            prohibition=[],
            obligation=[]
        )
    ]
)


class CKANCatalogService(ICatalogService):
    def __init__(self):
        self._datasets = {
            "dataset-1": dummy_dataset
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
