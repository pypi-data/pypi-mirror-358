
from rdkit import Chem
from rdkit.Chem import AllChem, MACCSkeys
from rdkit.Chem.AtomPairs import Pairs, Torsions
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.DataStructs import ConvertToNumpyArray

def generate_fingerprint(smiles: str, fingerprint_type: str):
    """
    Generates a molecular fingerprint for a given SMILES string.

    Args:
        smiles: The SMILES string of the molecule.
        fingerprint_type: The type of fingerprint to generate.

    Returns:
        The generated fingerprint.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES string")

    if fingerprint_type == "FP2":
        return FingerprintMols.FingerprintMol(mol, minPath=1, maxPath=2)
    elif fingerprint_type == "FP3":
        return FingerprintMols.FingerprintMol(mol, minPath=1, maxPath=3)
    elif fingerprint_type == "FP4":
        return FingerprintMols.FingerprintMol(mol, minPath=1, maxPath=4)
    elif fingerprint_type == "Topological/Daylight":
        return FingerprintMols.FingerprintMol(mol)
    elif fingerprint_type == "AtomPair":
        return Pairs.GetAtomPairFingerprint(mol)
    elif fingerprint_type == "Torsions/Topological Torsion":
        return Torsions.GetTopologicalTorsionFingerprint(mol)
    elif fingerprint_type == "MorganFingerprint":
        return AllChem.GetMorganFingerprint(mol, 2)
    elif fingerprint_type == "ECFP2":
        return AllChem.GetMorganFingerprint(mol, 1)
    elif fingerprint_type == "ECFP4":
        return AllChem.GetMorganFingerprint(mol, 2)
    elif fingerprint_type == "ECFP6":
        return AllChem.GetMorganFingerprint(mol, 3)
    elif fingerprint_type == "MACCS":
        return MACCSkeys.GenMACCSKeys(mol)
    elif fingerprint_type == "FCFP2":
        return AllChem.GetMorganFingerprint(mol, 1, useFeatures=True)
    elif fingerprint_type == "FCFP4":
        return AllChem.GetMorganFingerprint(mol, 2, useFeatures=True)
    elif fingerprint_type == "FCFP6":
        return AllChem.GetMorganFingerprint(mol, 3, useFeatures=True)
    elif fingerprint_type == "GhoseCrippen":
        return AllChem.GetGhoseCrippenFingerprint(mol)
    else:
        raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
