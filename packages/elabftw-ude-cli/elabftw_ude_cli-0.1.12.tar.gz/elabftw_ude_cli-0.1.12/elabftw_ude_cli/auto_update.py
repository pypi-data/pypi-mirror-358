import csv
import argparse
import os
from . import api
from .visibility import change_visibility
from . import config as Config

TEMPLATE_HEADERS = ['exp_id', 'name_like', 'body_path', 'mode', 'format']
TEMPLATE_INSTRUCTION_ROW = {
    'exp_id': '#000- experiment id {end of the url on the experiment page} (takes priority over name_like)',
    'name_like': 'example search string for the experiment name (exp_id has higher priority incase both are mentioned)',
    'body_path': '/path/to/body.md or body.html path of the file to upload',
    'mode': 'replace or append',
    'format': 'markdown or html'
}


def generate_mapping_template(filename='experiment_mapping_template.csv'):
    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=TEMPLATE_HEADERS)
        writer.writeheader()
        writer.writerow(TEMPLATE_INSTRUCTION_ROW)
    if Config.verbose >= 1: print(f"Template file generated at {filename}")


def parse_mapping_csv(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            exp_id = row.get('exp_id', '').strip()
            name_like = row.get('name_like', '').strip()

            # Skip placeholder/instruction row
            if str(exp_id).startswith('#'):
                continue

            yield {
                'exp_id': exp_id,
                'name_like': name_like,
                'body_path': row['body_path'].strip(),
                'mode': row.get('mode', 'replace').strip().lower(),
                'format': row.get('format', 'markdown').strip().lower(),
            }


def run_updates(mapping_path):
    for entry in parse_mapping_csv(mapping_path):
        exp_id = entry['exp_id']
        name_like = entry['name_like']
        body_path = entry['body_path']
        mode = entry['mode']
        format_str = entry['format']
        content_type = 1 if format_str == 'html' else 2

        if not exp_id:
            try:
                exp_id = api._resolve_exp_id(name_like)
            except Exception as e:
                print(f"[ERROR] Could not resolve experiment for name_like '{name_like}': {e}")
                continue

        if not os.path.exists(body_path):
            print(f"[SKIP] File not found: {body_path}")
            continue

        with open(body_path, 'r') as f:
            content = f.read()

        try:
            if mode == 'replace':
                api.modify_experiment(
                    exp_id=exp_id,
                    body=body_path,
                    force=True
                )
                if Config.verbose >= 1: print(f"[OK] Replaced body of experiment {exp_id}")
            elif mode == 'append':
                api.modify_experiment(
                    exp_id=exp_id,
                    body_append=content,
                    force=True
                )
                if Config.verbose >= 1: print(f"[OK] Appended body to experiment {exp_id}")
            else:
                print(f"[SKIP] Unknown mode '{mode}' for experiment {exp_id}")
                continue

            # Update content_type via visibility
            change_visibility(exp_id, "content_type", content_type)
            if Config.verbose >= 1: print(f"[OK] Set content_type={content_type} for experiment {exp_id}")

        except Exception as e:
            print(f"[ERROR] Failed to update experiment {exp_id}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Auto-update experiment bodies from mapping CSV")
    parser.add_argument('--exp_file_mapping', help="Path to mapping CSV file")
    parser.add_argument('--generate-mapping', action='store_true', help="Generate a mapping CSV template")

    args = parser.parse_args()

    if args.generate_mapping:
        generate_mapping_template()
    elif args.exp_file_mapping:
        run_updates(args.exp_file_mapping)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
