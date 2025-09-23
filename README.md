# Issue Test Localizer

[Under Construction]

## 🌟 Problem Statement 
Given as input an issue description and the files in a Python repo, return as output a selected subset of relevant regression tests existing in the repo.

## 🌟 About 
This is an approach to select regression tests to assist the process of solving software development problems.
- **Localization**: We first localize the fault to specific files, then to suspicious functions.
- **Test Selection**: For each suspicious function, we identify all tests that exercise it.
- **Test Minimization**: The selected tests are further reduced to a minimal set of regression tests needed to cover the relevant functions.

## 🌟 Setup

1. Environment Setup

```shell
git clone https://github.ibm.com/tfahmed/Regression-Test-Selection
cd Regression-Test-Selection

python3.11 -m venv selection_venv
source selection_venv/bin/activate
pip install -r requirements.txt
```

2. API Key Setup

```shell
export OPENAI_API_KEY={Your_Key}
export MODEL_SERVING_URL={Base_URL} # URL of the model serving endpoint
```

## 🌟 Instructions

1. Suspicious Function Localization

```shell
bash -x src/get_suspicious_funcs.sh [dataset] [model] [log_dir]
```
After the script completes, you can find:

- Per-instance logs in `log_dir`.
- Per-instance results in `$log_dir/${model}_results` (each as a `JSON` file).
- The aggregated results for all instances in `$log_dir/${model}_combined.json`.

2. Regression Test Selection and Minimization

```shell
python3 minimization.py [suspicious_func_json] [result_json]
```
- `[suspicious_func_json]` should be the `$log_dir/${model}_combined.json` file generated in the previous step.
- `[result_json]` is the output path where you want to save the minimized results. Each entry in the output JSON will correspond to an `instance_id`, with the selected regression tests listed as its value.


