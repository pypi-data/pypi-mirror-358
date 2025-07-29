# pKa_predictor/predict.py
"""
Thin wrapper around the existing GNN inference in pKa_predictor/GNN/predict.py.
Handles CSV path, DataFrame, or SMILES input by writing a temporary file and
configuring the args for inferring().
"""
import os
import tempfile
import pandas as pd
from argparse import Namespace
from .GNN.predict import inferring
from .config import DEFAULT_HYPERS

__all__ = ['predict']

def predict(input_data,
            pH: float = 7.4,
            verbose: int = 0,
            atom_indices: list[int] | None = None,
            **kwargs):
    """
    Predict pKa and protonated SMILES without modifying the GNN module.

    Parameters:
        input_data (str or pd.DataFrame): Path to CSV, SMILES string, or DataFrame with 'SMILES' column.
        pH (float): pH at which to predict (default: 7.4).
        verbose (int): Verbosity level (0,1,2).
        atom_indices (list[int] | None): Specific atom indices to target.
        **kwargs: passed through to the GNN inferring args (e.g., model_dir, model_name, batch_size, etc.).

    Returns:
        None -- results are printed to stdout by the GNN inferring routine (per README).
    """
    # Load or wrap input into a DataFrame
    if isinstance(input_data, str) and os.path.exists(input_data):
        df = pd.read_csv(input_data)
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        # Assume raw SMILES string
        from rdkit import Chem
        if isinstance(input_data, str) and Chem.MolFromSmiles(input_data):
            df = pd.DataFrame([{'Smiles': input_data}])
        else:
            raise ValueError("input_data must be a CSV path, SMILES string, or DataFrame with 'SMILES' column.")

    # Rename header so GNN code finds 'Smiles'
    if 'SMILES' in df.columns:
        df = df.rename(columns={'SMILES': 'Smiles'})
    if 'smiles' in df.columns:
        df = df.rename(columns={'smiles': 'Smiles'})

    # Write standardized DataFrame to a temporary CSV
    tmp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    df.to_csv(tmp.name, index=False)
    data_dir, input_file = os.path.split(tmp.name)
    if data_dir and not data_dir.endswith(os.sep):
        data_dir += os.sep

    # Create temporary directory for GNN internal pickles
    tmp_infer_dir = tempfile.mkdtemp()

    # Merge default hyperparameters with any overrides
    params = {**DEFAULT_HYPERS, **kwargs}

    args = Namespace(
        data_path=data_dir,
        input=input_file,
        mode='test',
        pH=pH,
        verbose=verbose,
        atom_indices=atom_indices or [],
        infer_pickled=tmp_infer_dir,
        **params
    )

    # Run the GNN inferring routine (prints results)
    inferring(args)
