# main.py
#!/usr/bin/env python
import argparse
import pandas as pd
from pka_predictor.predict import predict

def main():
    parser = argparse.ArgumentParser(
        prog="pka-predictor",
        description="Predict pKa for a SMILES string or a CSV of SMILES"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-s", "--smiles",
        help="Single SMILES string to predict"
    )
    group.add_argument(
        "-i", "--input",
        help="Path to input CSV with a column named 'SMILES'"
    )
    parser.add_argument(
        "-p", "--pH",
        type=float,
        default=7.4,
        help="pH at which to predict (default: 7.4)"
    )
    parser.add_argument(
        "-v", "--verbose",
        type=int,
        choices=[0,1,2],
        default=0,
        help="Verbosity level (0, 1, or 2)"
    )
    parser.add_argument(
        "--atom-indices",
        nargs='+',
        type=int,
        help="Specific atom indices to target"
    )
    # Pass through GNN args with short aliases to match README
    parser.add_argument("-d", "--model-dir", type=str, default=".", help="Directory containing model weights.")
    parser.add_argument("-m", "--model-name", type=str, required=True, help="Filename of the trained model checkpoint.")
    parser.add_argument("-b", "--batch-size", type=int, default=32, help="Batch size for inference.")
    parser.add_argument("-o", "--output", help="Path to output CSV file (default: stdout)")

    args = parser.parse_args()

    if args.smiles:
        # Single SMILES: print or write to file
        pka, prot = predict(
            args.smiles,
            pH=args.pH,
            verbose=args.verbose,
            atom_indices=args.atom_indices,
            model_dir=args.model_dir,
            model_name=args.model_name,
            batch_size=args.batch_size
        )
        line = f"{pka},{prot}\n"
        if args.output:
            with open(args.output, 'w') as f:
                f.write(line)
        else:
            print(line, end='')
    else:
        # CSV input: load, predict, and write/print full table
        df = pd.read_csv(args.input)
        results = []
        for sm in df["SMILES"]:
            pka, prot = predict(
                sm,
                pH=args.pH,
                verbose=args.verbose,
                atom_indices=args.atom_indices,
                model_dir=args.model_dir,
                model_name=args.model_name,
                batch_size=args.batch_size
            )
            results.append({'predicted_pKa': pka, 'prot_smiles': prot})
        out = pd.concat([df, pd.DataFrame(results)], axis=1)
        if args.output:
            out.to_csv(args.output, index=False)
        else:
            print(out.to_csv(index=False), end='')

if __name__ == "__main__":
    main()
