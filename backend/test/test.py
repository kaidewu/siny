import pandas as pd
from pathlib import Path


def main():
    df = pd.read_excel(Path("../resources/examples/INPUT-EXAMPLE-WITH-DATA.xlsx").resolve(), sheet_name="TOOLS")
    text_list_simples_commas = []
    text_list = []
    text_list_double_commas = []

    for index, row in df.iterrows():
        text_list.append(str(row["Separator"]))
        text_list_simples_commas.append(f"'{str(row["Separator"])}'")
        text_list_double_commas.append(f"\"{str(row["Separator"])}\"")

    print(f"List sin commas: {', '.join(text_list)}")
    print(f"List simples commas: {', '.join(text_list_simples_commas)}")
    print(f"List doubles commas: {', '.join(text_list_double_commas)}")


if __name__ == "__main__":
    main()
