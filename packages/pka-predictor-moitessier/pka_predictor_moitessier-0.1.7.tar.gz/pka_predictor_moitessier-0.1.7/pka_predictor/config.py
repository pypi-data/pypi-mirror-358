# For reference, these values are the same as the ones in the GNN/argParser.py file.

DEFAULT_HYPERS = {
    # GNN architecture
    'embedding_size': 128,
    'n_graph_layers': 4,
    'n_FC_layers': 2,
    'model_dense_neurons': 448,  # note: training value is 448!
    'model_attention_heads': 4,
    'GATv2Conv_Or_Other': 'GATv2Conv',
    'restart': 'none',
    'batch_size': 32,
    'lr': 0.001,
    'weight_decay': 1e-5,
    'scheduler_gamma': 0.995,

    # Atom features — match these exactly to argParser.py
    'atom_feature_atom_size': True,
    'atom_feature_element': False,
    'atom_feature_electronegativity': True,
    'atom_feature_hardness': True,
    'atom_feature_hybridization': True,
    'atom_feature_aromaticity': True,
    'atom_feature_number_of_rings': False,
    'atom_feature_ring_size': True,
    'atom_feature_number_of_Hs': True,
    'atom_feature_formal_charge': True,

    # Bond features — match these exactly to argParser.py
    'bond_feature_bond_order': True,
    'bond_feature_conjugation': True,
    'bond_feature_charge_conjugation': True,
    'bond_feature_polarization': True,
    'bond_feature_focused': False,

    # Misc (from argParser.py)
    'carbons_included': True,
    'acid_or_base': 'base',
    'mask_size': 4,
    'n_random_smiles': 10,
}
