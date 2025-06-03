import unittest
import requests
from typing import Dict, Any

class TestInfiniGramAPI(unittest.TestCase):
    def setUp(self):
        self.index = 'pileval-llama'
        self.base_url = 'http://0.0.0.0:8080'

    def make_request(self, query_type: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to make API requests"""
        response = requests.post(f'{self.base_url}/{self.index}/{query_type}', json=query)
        self.assertEqual(response.status_code, 200, f"Request failed with status {response.status_code}")
        return response.json()

    def test_count_endpoint(self):
        """Test the count endpoint with various queries"""

        # Test case 1: Specific phrase
        result = self.make_request('count', {'query': 'natural language processing'})
        self.assertEqual(result['count'], 76)
        self.assertFalse(result['approx'])
        self.assertEqual(result['tokenIds'], [5613, 4086, 9068])
        self.assertEqual(result['tokens'], ['▁natural', '▁language', '▁processing'])

        # Test case 2: Empty query
        result = self.make_request('count', {'query': ''})
        self.assertEqual(result['count'], 393769120)
        self.assertFalse(result['approx'])

        # Test case 3: Non-existent phrase
        result = self.make_request('count', {'query': 'fhsdkcdshfsdf'})
        self.assertEqual(result['count'], 0)
        self.assertFalse(result['approx'])

        # Test case 4: OR query
        result = self.make_request('count_cnf', {'query': 'natural language processing OR artificial intelligence', 'max_clause_freq': 50000, 'max_diff_tokens': 20})
        self.assertEqual(result['count'], 499)
        self.assertFalse(result['approx'])

        # Test case 5: AND query
        result = self.make_request('count_cnf', {'query': 'natural language processing AND deep learning', 'max_clause_freq': 50000, 'max_diff_tokens': 20})
        self.assertEqual(result['count'], 1)
        self.assertFalse(result['approx'])

        # Test case 6: AND query
        result = self.make_request('count_cnf', {'query': 'natural language processing AND deep learning'})
        self.assertEqual(result['count'], 6)
        self.assertFalse(result['approx'])

        # Test case 7: OR AND query
        result = self.make_request('count_cnf', {'query': 'natural language processing OR artificial intelligence AND deep learning', 'max_clause_freq': 50000, 'max_diff_tokens': 20})
        self.assertEqual(result['count'], 6)
        self.assertFalse(result['approx'])

    def test_prob_endpoint(self):
        """Test the probability endpoint"""

        # Test case 1: Specific phrase
        result = self.make_request('prob', {'query': 'natural language processing'})
        self.assertEqual(result['promptCnt'], 257)
        self.assertEqual(result['contCnt'], 76)
        self.assertIsInstance(result['prob'], float)

        # Test case 2: Specific phrase
        result = self.make_request('prob', {'query': 'natural language apple'})
        self.assertEqual(result['promptCnt'], 257)
        self.assertEqual(result['contCnt'], 0)
        self.assertIsInstance(result['prob'], float)

        # Test case 3: Non-existent phrase
        result = self.make_request('prob', {'query': 'fhsdkcdshfsdf processing'})
        self.assertEqual(result['promptCnt'], 0)
        self.assertEqual(result['contCnt'], 0)
        self.assertIsInstance(result['prob'], float)

    def test_ntd_endpoint(self):
        """Test the NTD endpoint"""

        # Test case 1: low max_support
        result = self.make_request('ntd', {'query': 'natural language', 'max_support': 10})
        self.assertEqual(result['promptCnt'], 257)
        self.assertTrue(result['approx'])
        self.assertIsInstance(result['resultByTokenId'], dict)

        # Test case 2: default max_support
        result = self.make_request('ntd', {'query': 'natural language'})
        self.assertEqual(result['promptCnt'], 257)
        self.assertFalse(result['approx'])
        self.assertIsInstance(result['resultByTokenId'], dict)

        # Test case 3: empty query
        result = self.make_request('ntd', {'query': ''})
        self.assertEqual(result['promptCnt'], 393769120)
        self.assertTrue(result['approx'])
        self.assertIsInstance(result['resultByTokenId'], dict)

    def test_infgram_prob_endpoint(self):
        """Test the InfiniGram probability endpoint"""

        # Test case 1: Specific phrase
        result = self.make_request('infgram_prob', {'query': 'fhsdkcdshfsdf natural language processing'})
        self.assertEqual(result['promptCnt'], 257)
        self.assertEqual(result['contCnt'], 76)
        self.assertIsInstance(result['prob'], float)
        self.assertEqual(result['suffixLen'], 2)
        self.assertEqual(result['longestSuffix'], 'natural language')

    def test_infgram_ntd_endpoint(self):
        """Test the InfiniGram NTD endpoint"""

        # Test case 1: low max_support
        result = self.make_request('infgram_ntd', {'query': 'hsdkcdshfsdf natural language', 'max_support': 10})
        self.assertEqual(result['promptCnt'], 257)
        self.assertTrue(result['approx'])
        self.assertIsInstance(result['resultByTokenId'], dict)
        self.assertEqual(result['suffixLen'], 2)
        self.assertEqual(result['longestSuffix'], 'natural language')

        # Test case 2: default max_support
        result = self.make_request('infgram_ntd', {'query': 'hsdkcdshfsdf natural language'})
        self.assertEqual(result['promptCnt'], 257)
        self.assertFalse(result['approx'])
        self.assertIsInstance(result['resultByTokenId'], dict)
        self.assertEqual(result['suffixLen'], 2)
        self.assertEqual(result['longestSuffix'], 'natural language')


if __name__ == '__main__':
    unittest.main()