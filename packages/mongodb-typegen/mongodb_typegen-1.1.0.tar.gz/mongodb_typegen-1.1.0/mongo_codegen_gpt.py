import argparse
from pymongo import MongoClient
from typing import TypedDict, Any
from collections import defaultdict
import typing


# --------- Schema Inference Utilities ----------

def infer_type(value):
    if isinstance(value, bool):
        return bool
    elif isinstance(value, int):
        return int
    elif isinstance(value, float):
        return float
    elif isinstance(value, str):
        return str
    elif isinstance(value, list):
        if value:
            return list[infer_type(value[0])]
        else:
            return list[Any]
    elif isinstance(value, dict):
        return dict[str, Any]
    else:
        return Any


def merge_types(types):
    unique_types = list(set(types))
    if len(unique_types) == 1:
        return unique_types[0]
    return typing.Union[tuple(unique_types)]


def infer_schema(documents):
    schema = defaultdict(list)
    for doc in documents:
        for k, v in doc.items():
            if k == "_id":
                continue
            schema[k].append(infer_type(v))
    return {k: merge_types(v) for k, v in schema.items()}


def format_type_hint(t):
    if hasattr(t, '__origin__'):
        if t.__origin__ is list:
            return f"list[{format_type_hint(t.__args__[0])}]"
        elif t.__origin__ is dict:
            return "dict[str, Any]"
        elif t.__origin__ is typing.Union:
            return " | ".join(format_type_hint(arg) for arg in t.__args__)
    elif isinstance(t, type):
        return t.__name__
    return "Any"


def generate_typeddict(name: str, schema: dict):
    lines = [f"class {name}(TypedDict, total=False):"]
    for field, typ in schema.items():
        lines.append(f"    {field}: {format_type_hint(typ)}")
    return "\n".join(lines)


# ------------- CLI Core Logic ---------------

def generate_from_db(uri: str, db_name: str, limit: int):
    client = MongoClient(uri)
    db = client[db_name]
    collections = db.list_collection_names()

    output = ["from typing import TypedDict, Any\n"]
    for coll_name in collections:
        documents = list(db[coll_name].find().limit(limit))
        if not documents:
            continue
        schema = infer_schema(documents)
        class_name = "".join(word.capitalize() for word in coll_name.split("_")) + "Doc"
        output.append(generate_typeddict(class_name, schema))
        output.append("")  # Blank line between classes
    return "\n".join(output)


# ------------- CLI Interface ---------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate TypedDict classes from MongoDB collections."
    )
    parser.add_argument("--uri", type=str, required=True, help="MongoDB URI")
    parser.add_argument("--db", type=str, required=True, help="Database name")
    parser.add_argument("--limit", type=int, default=100, help="Documents to sample per collection")
    parser.add_argument("--out", type=str, help="Write output to file (optional)")

    args = parser.parse_args()
    generated_code = generate_from_db(args.uri, args.db, args.limit)

    if args.out:
        with open(args.out, "w") as f:
            f.write(generated_code)
        print(f"TypedDicts written to {args.out}")
    else:
        print(generated_code)


if __name__ == "__main__":
    main()
