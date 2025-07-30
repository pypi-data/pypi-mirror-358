import argparse
from numberdividend import NumberCore
from typing import List, Tuple
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Dividend Analysis Tool")
    parser.add_argument("path", type=str, help="Input file path")
    parser.add_argument("target", type=int, help="Value of sum the array")
    parser.add_argument("save", type=str, help="Output file path")
    parser.add_argument("--limit", type=int, help="Limit the number of elements to consider from the array", default=None)
    parser.add_argument("--display", action="store_true", help="Display the dividend distribution")

    args = parser.parse_args()

    calculation(args.path, args.target, args.save, args.limit)

    if args.display:
        display(args.path, args.target, args.save, args.limit)
        print("Displaying dividend distribution...")

    # Placeholder for the main functionality
    print(f"Input file: {args.save}")

def calculation(path: str, target_sum: float, save: str, limit: int = None) -> List[Tuple[int, int]]:
    df = pd.read_csv(path, header=None)
    df = df.astype(float).values.flatten().tolist()
    dividend = NumberCore.dividend(df, target_sum, limit)
    dividend_df = pd.DataFrame(dividend, columns=["Dividend"])
    dividend_df.to_csv(save, index=False)

def display(path: str, target_sum: float, save: str, limit: int = None) -> List[Tuple[int, int]]:
    df = pd.read_csv(path, header=None)
    df = df.astype(float).values.flatten().tolist()
    dividend = NumberCore.dividend(df, target_sum, limit)
    NumberCore.display(dividend)

if __name__ == "__main__":
    main()