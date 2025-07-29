import os
import requests
import re
from datetime import datetime
from . import config as Config


def get_experiment_files(exp_id, name_pattern=None):
    """
    Get all uploaded files for a given experiment.
    Optionally filter by regex pattern in the filename.
    Returns a list of dicts with id, filename, and timestamps.
    """
    url = f"{Config.base_url}experiments/{exp_id}/uploads"
    response = requests.get(url, headers=Config.headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch uploads: {response.text}")
    try:
        files = response.json()
    except ValueError:
        raise RuntimeError("Failed to parse response JSON when listing experiment files.")

    if name_pattern:
        pattern = re.compile(name_pattern)
        files = [f for f in files if pattern.search(f['real_name'])]

    return [
        {
            'id': f['id'],
            'filename': f['real_name'],
            'created_at': f.get('created_at'),
            'modified_at': f.get('modified_at')
        }
        for f in files
    ]


def upload_file_to_experiment(exp_id, filepath, replace=False):
    """
    Upload a file to an experiment. If replace=True, replaces an existing file with same name.
    If not replacing, appends timestamp to the filename.
    Returns the upload ID.
    """
    files = get_experiment_files(exp_id)
    filename = os.path.basename(filepath)
    matching = [f for f in files if f['filename'] == filename]

    if matching and replace:
        file_id = matching[0]['id']
        if Config.verbose >= 1: print(f"Info: Replacing existing file with ID {file_id}.")
        return replace_uploaded_file(exp_id, file_id, filepath)
    elif matching:
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
        new_filename = f"{name}{timestamp}{ext}"
        print(f"Warning: File with the same name exists. Renaming file to '{new_filename}' before upload.")
        filename = new_filename

    url = f"{Config.base_url}experiments/{exp_id}/uploads"
    with open(filepath, 'rb') as file_data:
        files = {'file': (filename, file_data)}
        response = requests.post(url, headers=Config.headers, files=files)

    if response.status_code == 201:
        try:
            return response.json().get('id')
        except ValueError:
            print("Upload succeeded, but no JSON response returned.")
            return None
    else:
        raise RuntimeError(f"Upload failed: {response.status_code} - {response.text}")


def replace_uploaded_file(exp_id, file_id, filepath):
    """
    Replace an uploaded file in an experiment using its file_id.
    """
    url = f"{Config.base_url}experiments/{exp_id}/uploads/{file_id}"
    with open(filepath, 'rb') as file_data:
        files = {'file': file_data}
        response = requests.post(url, headers=Config.headers, files=files)

    if response.status_code in (200, 201):
        if Config.verbose >= 1: print(f"Info: File with ID {file_id} successfully replaced.")
        return file_id
    else:
        try:
            message = response.json()
        except ValueError:
            message = response.text
        raise RuntimeError(f"Replacement failed: {response.status_code} - {message}")


def delete_uploaded_files(file_ids, exp_id):
    """
    Delete one or multiple uploaded files by ID.
    """
    if isinstance(file_ids, int):
        file_ids = [file_ids]

    for file_id in file_ids:
        url = f"{Config.base_url}experiments/{exp_id}/uploads/{file_id}/download"
        response = requests.delete(url, headers=Config.headers)
        if response.status_code != 200:
            print(f"Warning: Deletion failed for file {file_id} - {response.text}")
        else:
            if Config.verbose >= 1: print(f"Info: File with ID {file_id} successfully deleted.")


def download_uploaded_files(exp_id, file_ids, target_dir="temp"):
    """
    Download one or more uploaded files to a local directory.
    Returns a list of paths to the downloaded files.
    """
    os.makedirs(target_dir, exist_ok=True)
    local_paths = []

    for file_id in file_ids:
        url = f"{Config.base_url}experiments/{exp_id}/uploads/{file_id}"
        response = requests.get(url, headers=Config.headers)
        if response.status_code != 200:
            print(f"Warning: Failed to download file {file_id} - {response.text}")
            continue

        cd = response.headers.get('Content-Disposition', '')
        match = re.search('filename=\\"(.+?)\\"', cd)
        filename = match.group(1) if match else f"file_{file_id}"
        local_path = os.path.join(target_dir, filename)

        with open(local_path, 'wb') as f:
            f.write(response.content)

        if Config.verbose >= 1: print(f"Info: Downloaded file {file_id} to '{local_path}'")
        local_paths.append(local_path)

    return local_paths
