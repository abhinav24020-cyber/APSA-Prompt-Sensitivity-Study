"""Unit test for BaselineCSVDataset loader and registry integration."""

import unittest
from apsa.data import BaselineCSVDataset, get_dataset
from apsa.data.base_dataset import DatasetItem


class TestBaselineDataset(unittest.TestCase):
    def test_baseline_dataset_loader(self):
        dataset = BaselineCSVDataset()
        items = dataset.load()
        self.assertEqual(len(items), 100)
        self.assertIsInstance(items[0], DatasetItem)
        self.assertEqual(items[0].id, "MATH-001")
        self.assertEqual(items[0].task_category.value, "mathematical_reasoning")
        self.assertIsNotNone(items[0].gold_answer)
        self.assertIn("is_deterministic", items[0].metadata)

    def test_baseline_dataset_sampling(self):
        dataset = BaselineCSVDataset()
        sampled = dataset.load(sample_size=10, seed=42)
        self.assertEqual(len(sampled), 10)

    def test_baseline_registry_integration(self):
        dataset = get_dataset("baseline")
        self.assertIsInstance(dataset, BaselineCSVDataset)
        items = dataset.load()
        self.assertEqual(len(items), 100)


if __name__ == "__main__":
    unittest.main()
