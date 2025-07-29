# elabftw_ude_cli

`elabftw_ude_cli` is a Python-based CLI and importable API for interacting with the [eLabFTW](https://www.elabftw.net) electronic lab notebook system, tailored for use at the University of Duisburg-Essen.

It provides:

- A command-line interface to create, modify, search, and read experiments.
- A Python API for programmatic integration with pipelines and notebooks.
- Tab-autocomplete support for fast CLI access.
- Optional integration with Python-based workflows like Snakemake.

---

## 🛠 Installation

```bash
pip install elabftw_ude_cli
```

### 🔑 Step 0: Add your API key and base URL

After installation, locate and edit your `config.py`:

```bash
elabftw-cli --config-path
```

Then open the file and update:
- `server_name_to_use` to clarify which server to use
- You can configure multiple servers and teams with different teams and/or test serversfor each server in the servers dictionary give it a name, and define its:
 - `url` pointing to your institution's instance
 - `api_key` with your generated key (see below)


#### 🎯 How to get your API key:
1. Log in to eLabFTW.
2. Click your initials in the top-right.
3. Go to **Settings → API Keys**.
4. Enter a name, set permission to **read/write**, and click **Generate API Key**.
5. **Copy and store the key safely** – it will only be shown once.

---

## ⚡ CLI Usage

After installation, use `elabftw-cli` from the command line.

### ♻️ Enable tab-completion (Optional; Dose not work for conda based enviroenments)

```bash
activate-global-python-argcomplete --user
```

Or for bash/zsh:

```bash
eval "$(register-python-argcomplete elabftw-cli)"
```

### 📋 CLI Commands

```bash
elabftw-cli create_experiment --name "Exp Title" --body body.md --steps steps.json
elabftw-cli modify_experiment --exp_id 123 --body new_body.md --steps new_steps.json
elabftw-cli search_experiments --name-like "test"
elabftw-cli read_experiment --exp_id 123
```

### 📁 File Actions via CLI

```bash
elabftw-cli file-actions --name-like "My Experiment" --upload results.csv --replace
elabftw-cli file-actions --name-like "My Experiment" --search
elabftw-cli file-actions --name-like "My Experiment" --delete log.txt error.log
elabftw-cli file-actions --name-like "My Experiment" --download report.txt
```

#### File Options
- `--replace`: Replace file if it already exists
- `--delete`: Delete files by name match (can be partial)
- `--download`: Download files to `temp/` directory
- `--search`: List uploaded files

---

## 🧑‍💻 Python API Usage

```python
import elabftw_ude_cli.api as elf

# Create an experiment
exp_id = elf.create_experiment(
    name="My Experiment",
    body="<h1>Intro</h1><p>This is HTML</p>",
    content_type=2
)

# Modify with body append and steps
elf.modify_experiment(
    exp_id=exp_id,
    body_append="Done.\nAll checked.",
    steps=[{"body": "step_3: summary"}]
)

# Complete a step
elf.complete_step(exp_id, pattern="step_3", change="first", done_by="Alice")

# Search and read
ids, names = elf.search_experiments("test")
data = elf.read_experiment(exp_id=ids[0])
```

---

## 🧬 Snakemake Integration Example

See [Snakemake Integration](https://git.uni-due.de/hb0358/resist_api_scripts/-/blob/main/eLAB/README_Snakemake_Integration.md) for examples of using this inside workflows.

## 📋 CLI auto_update and automations:

See [Auto Update Guide](https://git.uni-due.de/hb0358/resist_api_scripts/-/blob/main/eLAB/README_AutoUpdate.md) for scheduling and automation.


---

## 📦 License

MIT License. See `LICENSE` file.
