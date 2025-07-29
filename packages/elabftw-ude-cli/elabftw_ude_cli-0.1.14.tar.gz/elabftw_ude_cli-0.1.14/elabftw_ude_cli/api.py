import json
import os
from . import create_modify, read, search, file_actions


def _read_file_or_return(obj, is_json=False):
    if isinstance(obj, str) and os.path.exists(obj):
        with open(obj, 'r') as f:
            return json.load(f) if is_json else f.read()
    return obj


def create_experiment(name=None, body=None, json_data=None, steps=None, content_type=1):
    data = _read_file_or_return(json_data, is_json=True) if json_data else {}
    if name:
        data['title'] = name
    if body:
        data['body'] = _read_file_or_return(body, is_json=False)

    if 'title' not in data:
        raise ValueError("Experiment 'name' is required either via `name` or `json_data`.")

    exp_id = create_modify.create_experiment({'title': data['title']})
    if not exp_id:
        raise RuntimeError("Experiment creation failed.")

    if 'content_type' not in data:
        if isinstance(body, str):
            if body.endswith('.html'):
                data['content_type'] = 2
            elif body.endswith('.md'):
                data['content_type'] = 1
            else:
                data['content_type'] = content_type
        else:
            data['content_type'] = content_type
    if "steps" in data.keys() :steps=data.pop("steps")
    create_modify.modify_experiment(exp_id, data)

    if steps:
        steps_data = _read_file_or_return(steps, is_json=True)
        if isinstance(steps, str) and os.path.exists(steps):
            steps_data = steps_data["steps"]
        create_modify.add_steps(exp_id, steps_data)

    return exp_id


def modify_experiment(exp_id, name=None, body=None, json_data=None, steps=None, force=False, body_append=None):
    if not exp_id: raise ValueError("Pass exp_id is mandatory, if you dont know use search_experiments to identify one")
    existing = read.read_experiment(exp_id)
    new_data = _read_file_or_return(json_data, is_json=True) if json_data else {}

    if body and body_append:
        raise ValueError("Pass either `body` or `body_append`, not both.")

    if body:
        new_data['body'] = _read_file_or_return(body, is_json=False)

    if body_append:
        old_body = existing.get("body", "")
        content_type = existing.get("content_type", 1)
        body_append = body_append.replace("\\n", "<br>") if content_type == 2 else body_append
        new_data['body'] = f"{old_body.rstrip()}\\n\\n{body_append.strip()}"

    if name:
        if name != existing.get("title", "") and not force:
            raise ValueError("Provided name differs from existing title. Use force=True to override.")
        new_data['title'] = name
    if "steps" in new_data.keys() :steps=new_data.pop("steps")
    if new_data:
        create_modify.modify_experiment(exp_id, new_data)

    if steps:
        steps_data = _read_file_or_return(steps, is_json=True)
        if isinstance(steps, str) and os.path.exists(steps):
            steps_data=steps_data["steps"]
        create_modify.add_steps(exp_id, steps_data)

    if not new_data and not steps:
        raise ValueError("No new data or steps provided to modify.")


def search_experiments(name_like):
    return search.filter_experiments(name_like)


def read_experiment(exp_id=None, name_like=None, fetch="first"):
    if exp_id:
        return [read.read_experiment(exp_id)]
    ids, _ = search.filter_experiments(name_like)
    if not ids:
        return []
    if fetch == "first":
        return [read.read_experiment(ids[0])]
    elif fetch == "all":
        return [read.read_experiment(i) for i in ids]
    else:
        raise ValueError("Invalid fetch argument: must be 'first' or 'all'")


def complete_step(exp_id, pattern="step_1", done_by=None, change=None):
    return create_modify.complete_steps(
        exp_id_here=exp_id,
        step_pattern_to_finish=pattern,
        done_by=done_by,
        change=change
    )


def _resolve_exp_id(name_like, use="error"):
    ids, _ = search.filter_experiments(name_like)
    if not ids:
        raise ValueError(f"No experiment found matching: {name_like}")
    if len(ids) > 1:
        if use == "first":
            return ids[0]
        elif use == "latest":
            return ids[-1]
        else:
            raise ValueError(
                f"Multiple experiments matched '{name_like}': {ids}. "
                "Use use='first' or use='latest'."
            )
    return ids[0]


def search_files(name_like, pattern=None, use="error"):
    exp_id = _resolve_exp_id(name_like, use=use)
    return file_actions.get_experiment_files(exp_id, name_pattern=pattern)


def upload_file(name_like, filepath, replace=False, use="error"):
    exp_id = _resolve_exp_id(name_like, use=use)
    return file_actions.upload_file_to_experiment(exp_id, filepath, replace=replace)


def delete_files(name_like, patterns, use="error", match="all"):
    if isinstance(patterns, str):
        patterns = [patterns]

    exp_id = _resolve_exp_id(name_like, use=use)
    files = file_actions.get_experiment_files(exp_id)
    matched = [f for f in files if any(p in f['filename'] for p in patterns)]

    if not matched:
        print("No matching files found.")
        return []

    if match == "first":
        to_delete = [matched[0]['id']]
    elif match == "last":
        to_delete = [matched[-1]['id']]
    elif match == "all":
        to_delete = [f['id'] for f in matched]
    else:
        print("Invalid match argument. Use 'first', 'last', or 'all'.")
        return []

    file_actions.delete_uploaded_files(to_delete, exp_id)
    return to_delete


def download_files(name_like, patterns, target_dir="temp", use="error", match="all"):
    if isinstance(patterns, str):
        patterns = [patterns]

    exp_id = _resolve_exp_id(name_like, use=use)
    files = file_actions.get_experiment_files(exp_id)
    matched = [f for f in files if any(p in f['filename'] for p in patterns)]

    if not matched:
        print("No matching files found.")
        return []

    if match == "first":
        file_ids = [matched[0]['id']]
    elif match == "last":
        file_ids = [matched[-1]['id']]
    elif match == "all":
        file_ids = [f['id'] for f in matched]
    else:
        print("Invalid match argument. Use 'first', 'last', or 'all'.")
        return []

    return file_actions.download_uploaded_files(exp_id, file_ids, target_dir=target_dir)
