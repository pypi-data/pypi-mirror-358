from utils.descriptor import mol2vec
import pickle
from sklearn.model_selection import train_test_split

from rdkit import Chem


def dump_datasets(dataset, path):
    dataset_dumps = pickle.dumps(dataset)
    with open(path, "wb") as f:
        f.write(dataset_dumps)
    return

def generate_datasets(mols,valid=True):
    datasets = []
    for mol in mols:
        if not mol:
            continue
        atom_idx = int(mol.GetProp("idx"))
        pka = float(mol.GetProp("pka"))
        data = mol2vec(mol, atom_idx, evaluation=False, pka=pka)
        datasets.append(data)

    if valid:

        train_dataset, valid_dataset = train_test_split(datasets, test_size=0.1)
        return train_dataset, valid_dataset

    else:
        return datasets

if __name__=="__main__":
    '''f = 'random_3'
    mol_path = f'datasets/train_set_{f}.sdf'
    mols = Chem.SDMolSupplier(mol_path, removeHs=False)
    train_dataset,valid_dataset = generate_datasets(mols)

    train_path = f"datasets/train_set_{f}.pickle"
    valid_path = f"datasets/valid_set_{f}.pickle"
    dump_datasets(train_dataset, train_path)
    dump_datasets(valid_dataset, valid_path)


    test_set_path = f'datasets/test_set_{f}.sdf'
    mols_test = Chem.SDMolSupplier(test_set_path, removeHs=False)
    test_dataset = generate_datasets(mols_test, valid=False)
    test_path = f"datasets/test_set_{f}.pickle"
    dump_datasets(test_dataset, test_path)'''

    f = 'random_3'
    test_set_path = f'datasets/train_set_{f}.sdf'
    mols_test = Chem.SDMolSupplier(test_set_path, removeHs=False)
    test_dataset = generate_datasets(mols_test, valid=False)
    test_path = f"datasets/full_train_set_{f}.pickle"
    dump_datasets(test_dataset, test_path)