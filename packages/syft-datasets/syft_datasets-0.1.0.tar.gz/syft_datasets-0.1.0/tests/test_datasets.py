"""Tests for syft_datasets package."""

from unittest.mock import Mock, patch

import pytest

from syft_datasets import Dataset, DatasetCollection


class TestDataset:
    """Test cases for the Dataset class."""

    def test_dataset_init(self):
        """Test Dataset initialization."""
        dataset = Dataset(
            email="test@example.com",
            dataset_name="test_dataset",
        )

        assert dataset.email == "test@example.com"
        assert dataset.name == "test_dataset"
        assert dataset.syft_url == "syft://test@example.com/private/datasets/test_dataset"

    def test_dataset_str_repr(self):
        """Test Dataset string representation."""
        dataset = Dataset(
            email="test@example.com",
            dataset_name="test_dataset",
        )

        expected = "Dataset(email='test@example.com', name='test_dataset')"
        assert str(dataset) == expected
        assert repr(dataset) == expected

    def test_dataset_syft_url_property(self):
        """Test Dataset syft_url property."""
        dataset = Dataset(
            email="alice@example.com",
            dataset_name="financial_data",
        )

        assert dataset.syft_url == "syft://alice@example.com/private/datasets/financial_data"


class TestDatasetCollection:
    """Test cases for the DatasetCollection class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_datasets = [
            Dataset("alice@example.com", "dataset1"),
            Dataset("bob@example.com", "dataset2"),
            Dataset("alice@example.com", "test_data"),
            Dataset("charlie@example.com", "model_data"),
        ]

    @patch("syft_datasets.Client")
    def test_dataset_collection_empty_init(self, mock_client):
        """Test DatasetCollection initialization with no data."""
        # Mock the Client.load() to avoid actual SyftBox dependency
        mock_client.load.side_effect = Exception("No SyftBox client")

        collection = DatasetCollection(datasets=[])
        assert len(collection) == 0
        assert list(collection) == []

    def test_dataset_collection_with_data(self):
        """Test DatasetCollection with provided datasets."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        assert len(collection) == 4
        assert collection[0].email == "alice@example.com"
        assert collection[1].name == "dataset2"

    def test_dataset_collection_indexing(self):
        """Test DatasetCollection indexing and slicing."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        # Test single item access
        assert collection[0].email == "alice@example.com"
        assert collection[-1].email == "charlie@example.com"

        # Test slicing
        subset = collection[:2]
        assert len(subset) == 2
        assert subset[0].email == "alice@example.com"
        assert subset[1].email == "bob@example.com"

    def test_dataset_collection_search(self):
        """Test DatasetCollection search functionality."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        # Search by name
        results = collection.search("dataset1")
        assert len(results) == 1
        assert results[0].name == "dataset1"

        # Search by email
        results = collection.search("alice")
        assert len(results) == 2
        assert all("alice" in ds.email for ds in results)

        # Search with no results
        results = collection.search("nonexistent")
        assert len(results) == 0

    def test_dataset_collection_filter_by_email(self):
        """Test DatasetCollection email filtering."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        # Filter by email pattern
        results = collection.filter_by_email("alice")
        assert len(results) == 2
        assert all("alice" in ds.email for ds in results)

        # Filter by domain
        results = collection.filter_by_email("example.com")
        assert len(results) == 4  # All datasets have example.com domain

    def test_dataset_collection_get_by_indices(self):
        """Test DatasetCollection get_by_indices method."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        # Get specific indices
        results = collection.get_by_indices([0, 2])
        assert len(results) == 2
        assert results[0].email == "alice@example.com"
        assert results[1].name == "test_data"

        # Handle out of range indices
        results = collection.get_by_indices([0, 10, 2])
        assert len(results) == 2  # Only valid indices
        assert results[0].email == "alice@example.com"
        assert results[1].name == "test_data"

    def test_dataset_collection_unique_emails(self):
        """Test DatasetCollection list_unique_emails method."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        emails = collection.list_unique_emails()
        expected = ["alice@example.com", "bob@example.com", "charlie@example.com"]
        assert sorted(emails) == sorted(expected)

    def test_dataset_collection_unique_names(self):
        """Test DatasetCollection list_unique_names method."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        names = collection.list_unique_names()
        expected = ["dataset1", "dataset2", "test_data", "model_data"]
        assert sorted(names) == sorted(expected)

    def test_dataset_collection_to_list(self):
        """Test DatasetCollection to_list method."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        datasets_list = collection.to_list()
        assert len(datasets_list) == 4
        assert all(isinstance(ds, Dataset) for ds in datasets_list)

    def test_dataset_collection_iteration(self):
        """Test DatasetCollection iteration."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        # Test iteration
        datasets_list = list(collection)
        assert len(datasets_list) == 4
        assert datasets_list[0].email == "alice@example.com"

        # Test iteration with for loop
        count = 0
        for dataset in collection:
            assert isinstance(dataset, Dataset)
            count += 1
        assert count == 4

    def test_dataset_collection_str_representation(self):
        """Test DatasetCollection string representation."""
        collection = DatasetCollection(datasets=self.mock_datasets)

        str_repr = str(collection)
        assert "alice@example.com" in str_repr
        assert "dataset1" in str_repr
        assert "syft://" in str_repr

        # Test empty collection
        empty_collection = DatasetCollection(datasets=[])
        assert str(empty_collection) == "No datasets available"

    @patch("syft_datasets.Client")
    def test_dataset_collection_connection_check(self, mock_client):
        """Test DatasetCollection connection status checking."""
        # Mock successful connection
        mock_client_instance = Mock()
        mock_client_instance.email = "test@example.com"
        mock_client_instance.datasites.iterdir.return_value = [Mock(name="alice@example.com")]
        mock_client_instance.config.client_url = "http://localhost:8000"
        mock_client.load.return_value = mock_client_instance

        # Test that it attempts to check connection
        with patch("syft_datasets.init_session"), patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "go1.21"

            DatasetCollection()
            # Should not raise an exception


@pytest.fixture
def sample_datasets():
    """Fixture providing sample datasets for testing."""
    return [
        Dataset("alice@example.com", "financial_data"),
        Dataset("bob@example.com", "medical_records"),
        Dataset("charlie@example.com", "weather_data"),
    ]


def test_module_imports():
    """Test that all main components can be imported."""
    from syft_datasets import Dataset, DatasetCollection, datasets

    assert Dataset is not None
    assert DatasetCollection is not None
    assert datasets is not None


def test_dataset_collection_html_representation():
    """Test that HTML representation doesn't crash."""
    collection = DatasetCollection(datasets=[Dataset("test@example.com", "test_dataset")])

    html = collection._repr_html_()
    assert isinstance(html, str)
    assert "test@example.com" in html
    assert "test_dataset" in html
    assert "nsai-container" in html
