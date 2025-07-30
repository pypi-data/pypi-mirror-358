
import unittest
from chemprep import generate_fingerprint, calculate_similarity

class TestChemPrep(unittest.TestCase):

    def test_fingerprint_generation(self):
        smiles = "CCO"
        fp = generate_fingerprint(smiles, fingerprint_type="MorganFingerprint")
        self.assertIsNotNone(fp)

    def test_similarity_calculation(self):
        smiles1 = "CCO"
        smiles2 = "CCN"
        similarity = calculate_similarity(smiles1, smiles2, fingerprint_type="MorganFingerprint", similarity_metric="Tanimoto")
        self.assertIsInstance(similarity, float)

if __name__ == '__main__':
    unittest.main()
