import argparse
import json
from . import create_modify, read, search, file_actions
from .config import get_config_file_path  # ✅ import the config path function
from . import config as Config


def load_body_from_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def handle_create(args):
    data = {}
    steps = None
    if args.json:
        with open(args.json, 'r') as f:
            data = json.load(f)
    if args.name:
        data['title'] = args.name
    if args.body:
        data['body'] = load_body_from_file(args.body)
    if not data.get('title'):
        print("Error: Experiment 'name' (title) is required.")
        return
    if "steps" in data.keys() :steps=data.pop("steps")
    exp_id = create_modify.create_experiment({'title': data['title']})
    if not exp_id:
        print("Experiment creation failed.")
        return
    if Config.verbose >= 1: print(f"Created experiment ID: {exp_id}")
    if Config.verbose >= 1: print("Modifying experiment with provided data...")
    create_modify.modify_experiment(exp_id, data)
    if args.steps or steps:
        if args.steps:
            with open(args.steps, 'r') as f:
                all_data = json.load(f)
            steps_data = all_data["steps"]
        else:
            steps_data=steps
        create_modify.add_steps(exp_id, steps_data)


def handle_modify(args):
    if not args.exp_id:
        print("Experiment ID is required for modification.")
        return
    existing = read.read_experiment(args.exp_id)
    new_data = {}
    steps=None
    if args.json:
        with open(args.json, 'r') as f:
            new_data = json.load(f)
    if args.body:
        new_data['body'] = load_body_from_file(args.body)
    if args.name:
        if args.name != existing.get("title", "") and not args.force:
            print("Warning: Provided name differs from existing title.")
            return
        new_data['title'] = args.name
    if not new_data and not args.steps:
        print("No data provided to modify.")
        return
    if "steps" in data.keys():steps=new_data.pop("steps")
    create_modify.modify_experiment(args.exp_id, new_data)
    if args.steps or steps:
        if args.steps:
            with open(args.steps, 'r') as f:
                all_data = json.load(f)
            steps_data = all_data["steps"]
        else:
            steps_data = steps
        create_modify.add_steps(args.exp_id, steps_data)


def handle_search(args):
    ids, names = search.filter_experiments(args.name_like)
    for i, n in zip(ids, names):
        print(f"{i}: {n}")


def handle_read(args):
    if args.exp_id:
        result = read.read_experiment(args.exp_id, print_out=True)
        filename = args.outfile if args.outfile else f"{args.exp_id}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        if Config.verbose >= 1: print(f"Wrote experiment data to {filename}")
    elif args.name_like:
        ids, names = search.filter_experiments(args.name_like)
        if len(ids) == 0:
            print("No matching experiments found.")
            return
        if len(ids) == 1 or args.first:
            result = read.read_experiment(ids[0], print_out=True)
            filename = args.outfile if args.outfile else f"{ids[0]}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            if Config.verbose >= 1: print(f"Wrote experiment data to {filename}")
        elif args.all:
            all_data = [read.read_experiment(i) for i in ids]
            filename = args.outfile if args.outfile else "multiple_experiments.json"
            with open(filename, 'w') as f:
                json.dump(all_data, f, indent=2)
            if Config.verbose >= 1: print(f"Wrote all experiments data to {filename}")
        else:
            print(f"Found {len(ids)} matches:")
            for idx, (i, n) in enumerate(zip(ids, names)):
                print(f"{idx+1}. {i}: {n}")
            choice = input("Enter f for first, a for all: ").strip().lower()
            if choice == 'f':
                result = read.read_experiment(ids[0], print_out=True)
                filename = args.outfile if args.outfile else f"{ids[0]}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                if Config.verbose >= 1: print(f"Wrote experiment data to {filename}")
            elif choice == 'a':
                all_data = [read.read_experiment(i) for i in ids]
                filename = args.outfile if args.outfile else "multiple_experiments.json"
                with open(filename, 'w') as f:
                    json.dump(all_data, f, indent=2)
                if Config.verbose >= 1: print(f"Wrote all experiments data to {filename}")


def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for eLabFTW functions")

    # ✅ Global argument
    parser.add_argument(
        "--config-path",
        action="store_true",
        help="Print the path to the config.py file and exit."
    )

    subparsers = parser.add_subparsers(dest="command")

    parser_create = subparsers.add_parser("create_experiment")
    parser_create.add_argument("--name", help="Title for experiment")
    parser_create.add_argument("--body", help="HTML/text body file for experiment")
    parser_create.add_argument("--json", help="JSON file with full experiment data")
    parser_create.add_argument("--steps", help="JSON file with steps to be added")

    parser_modify = subparsers.add_parser("modify_experiment", help="Modify Experiments, Needs exp_id, if unsure use search_experiments function to identify an exp_id")
    parser_modify.add_argument("--exp_id", required=True, help="Experiment ID to modify, if unsure use search_experiments function to identify an exp_id")
    parser_modify.add_argument("--name", help="New title (discouraged)")
    parser_modify.add_argument("--body", help="HTML/text body file")
    parser_modify.add_argument("--json", help="JSON file with update data")
    parser_modify.add_argument("--steps", help="JSON file with steps to be added")
    parser_modify.add_argument("-f", "--force", action="store_true", help="Force title change")

    parser_search = subparsers.add_parser("search_experiments")
    parser_search.add_argument("--name-like", required=True, help="Search term for experiment names")

    parser_read = subparsers.add_parser("read_experiment")
    parser_read.add_argument("--exp_id", help="Experiment ID to read")
    parser_read.add_argument("--name-like", help="Partial or full experiment name to search")
    parser_read.add_argument("--first", action="store_true", help="Use first match automatically")
    parser_read.add_argument("--all", action="store_true", help="Fetch all matches")
    parser_read.add_argument("--outfile", help="Output JSON filename")

    parser_files = subparsers.add_parser("file-actions")
    parser_files.add_argument("--name-like", required=True, help="Name of experiment to operate on")
    parser_files.add_argument("--upload", help="Path to file to upload")
    parser_files.add_argument("--replace", action="store_true", help="Replace file if already exists")
    parser_files.add_argument("--delete", nargs="+", help="List of filename patterns to delete")
    parser_files.add_argument("--search", action="store_true", help="List files in the experiment")
    parser_files.add_argument("--download", nargs="+", help="List of filename patterns to download")

    args = parser.parse_args()

    # ✅ Respond to global flag
    if args.config_path:
        print(get_config_file_path())
        exit(0)

    if args.command == "create_experiment":
        handle_create(args)
    elif args.command == "modify_experiment":
        handle_modify(args)
    elif args.command == "search_experiments":
        handle_search(args)
    elif args.command == "read_experiment":
        handle_read(args)
    elif args.command == "file-actions":
        ids, _ = search.filter_experiments(args.name_like)
        if not ids:
            print("No matching experiment found.")
            return
        if len(ids) > 1:
            print("Multiple experiments found. Please refine your name-like.")
            for i in ids:
                print(f" - {i}")
            return
        exp_id = ids[0]

        if args.search:
            files = file_actions.get_experiment_files(exp_id)
            for f in files:
                print(f"{f['id']} - {f['filename']} (created: {f['created_at']})")

        if args.upload:
            result = file_actions.upload_file_to_experiment(exp_id, args.upload, replace=args.replace)
            if Config.verbose >= 1: print(f"Upload result: {result}")

        if args.delete:
            files = file_actions.get_experiment_files(exp_id)
            to_delete = [f['id'] for f in files if any(p in f['filename'] for p in args.delete)]
            if not to_delete:
                print("No matching files to delete.")
            else:
                file_actions.delete_uploaded_files(to_delete)

        if args.download:
            files = file_actions.get_experiment_files(exp_id)
            to_download = [f['id'] for f in files if any(p in f['filename'] for p in args.download)]
            if not to_download:
                print("No matching files to download.")
            else:
                file_actions.download_uploaded_files(exp_id, to_download)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
