
from rdkit import DataStructs
from .fingerprints import generate_fingerprint

def calculate_similarity(smiles1: str, smiles2: str, fingerprint_type: str, similarity_metric: str):
    """
    Calculates the similarity between two molecules.

    Args:
        smiles1: The SMILES string of the first molecule.
        smiles2: The SMILES string of the second molecule.
        fingerprint_type: The type of fingerprint to use.
        similarity_metric: The similarity metric to use.

    Returns:
        The calculated similarity score.
    """
    fp1 = generate_fingerprint(smiles1, fingerprint_type)
    fp2 = generate_fingerprint(smiles2, fingerprint_type)

    if similarity_metric == "Tanimoto":
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    elif similarity_metric == "RDKit":
        return DataStructs.RDKitSimilarity(fp1, fp2)
    elif similarity_metric == "Tversky":
        return DataStructs.TverskySimilarity(fp1, fp2, 1, 0)
    elif similarity_metric == "Euclidean":
        return DataStructs.EuclideanSimilarity(fp1, fp2)
    elif similarity_metric == "Dice":
        return DataStructs.DiceSimilarity(fp1, fp2)
    elif similarity_metric == "Cosine":
        return DataStructs.CosineSimilarity(fp1, fp2)
    elif similarity_metric == "RogotGoldberg":
        return DataStructs.RogotGoldbergSimilarity(fp1, fp2)
    elif similarity_metric == "MACCSKeys":
        return DataStructs.MACCSKeysSimilarity(fp1, fp2)
    elif similarity_metric == "Manhattan":
        return DataStructs.ManhattanSimilarity(fp1, fp2)
    else:
        raise ValueError(f"Unsupported similarity metric: {similarity_metric}")
