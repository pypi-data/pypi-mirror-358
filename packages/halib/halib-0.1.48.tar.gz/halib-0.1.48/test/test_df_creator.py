from argparse import ArgumentParser

# from line_profiler import LineProfiler
# profile = LineProfiler()
from tqdm import tqdm
from rich.console import Console
from rich import print as rprint
from rich import inspect
from rich.pretty import pprint
from tqdm import tqdm
from loguru import logger


def parse_args():
    parser = ArgumentParser(description="desc text")
    parser.add_argument(
        "-arg1", "--argument1", type=str, help="arg1 description", default="some_string"
    )
    parser.add_argument(
        "-arg2", "--argument2", type=int, help="arg2 description", default=99
    )
    return parser.parse_args()


# @profile
def main():
    args = parse_args()
    arg1 = args.argument1
    arg2 = args.argument2

    from halib.filetype.csvfile import DFCreator

    dfCreator = DFCreator()
    dfCreator.create_table("table1", ["col1", "col2"])
    dfCreator.create_table("table2", ["col3", "col4", "col5"])

    limit = 5
    mil_rows = [["a", "b"] for i in range(limit)]

    dfCreator.insert_rows("table1", [["a", "b"], ["d", "e"]])
    dfCreator.insert_rows("table1", mil_rows)

    dfCreator.insert_rows("table2", ["c", "d", "e"])

    for i in tqdm(range(limit)):
        dfCreator.insert_rows("table1", ["w", "z"])

    # dfCreator.display_all_table_schema()
    pprint(dfCreator.row_pool_dict)
    dfCreator.display_all_table()
    dfCreator.insert_rows("table1", ["k", "k"])
    pprint(dfCreator.row_pool_dict)
    dfCreator.display_all_table()
    pprint(dfCreator.row_pool_dict)

    dfCreator.write_all_table(".")


if __name__ == "__main__":
    main()
