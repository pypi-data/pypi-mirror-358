# ChemPrep

A Python library for molecular fingerprinting and similarity calculations.

## Installation

```bash
pip install chemprep
```

**Note:** You must have `rdkit` installed in your Python environment. If you don't have it, you can install it via conda:

```bash
conda install -c conda-forge rdkit
```

## Usage

### Generating Fingerprints

```python
from chemprep import generate_fingerprint

smiles = "CCO"

# Supported fingerprint types:
fingerprint_types = [
    "FP2", "FP3", "FP4", "Topological/Daylight", "AtomPair", 
    "Torsions/Topological Torsion", "MorganFingerprint", "ECFP2", "ECFP4", "ECFP6", 
    "MACCS", "FCFP2", "FCFP4", "FCFP6", "GhoseCrippen"
]

for fp_type in fingerprint_types:
    fp = generate_fingerprint(smiles, fingerprint_type=fp_type)
    print(f"{fp_type} fingerprint for {smiles}: {fp}")

```

### Calculating Similarity

```python
from chemprep import calculate_similarity

smiles1 = "CCO"
smiles2 = "CCN"

# Supported similarity metrics:
similarity_metrics = [
    "Tanimoto", "RDKit", "Tversky", "Euclidean", "Dice", 
    "Cosine", "RogotGoldberg", "MACCSKeys", "Manhattan"
]

# Example with MorganFingerprint
for metric in similarity_metrics:
    similarity = calculate_similarity(smiles1, smiles2, fingerprint_type="MorganFingerprint", similarity_metric=metric)
    print(f"{metric} similarity (Morgan): {similarity}")

```

