import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

from datasets import load_dataset
from tqdm import tqdm

from utils import read_json_to_dict

def get_test_modules(norm_info):
    modules = []
    for file in norm_info:
        mod = "/".join(file.split("/")[:-1])
        if mod not in modules:
            modules.append(mod)
    return modules


def run_coverage_docker(instance_id, test_methods, cov_dir, dataset_name, max_workers="4"):
    print(
        f"Running coverage for instance {instance_id} with {len(test_methods)} test methods"
    )
    cmd = [
        "python",
        "-m",
        "swebench.harness.run_evaluation",
        "--dataset_name",
        dataset_name, #"princeton-nlp/SWE-bench_Verified"
        "--predictions_path",
        "gold",
        "--max_workers",
        max_workers,
        "--run_id",
        cov_dir.replace("/", "_"),
        "--instance_ids",
        instance_id,
        "--test_methods",
        json.dumps(test_methods),
        "--cov_dir",
        cov_dir,
    ]
    print(cmd)

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
    return result


if __name__ == "__main__":

    args = sys.argv[1:]
    dataset_name = args[0]  #'princeton-nlp/SWE-bench_Verified'
    suspicious_funcs_file = args[1]
    selected_tests_file = args[2]
    model_name = args[3]
    coverage_dir_base = "add_coverage"
    
    coverage_dir = f"{coverage_dir_base}/coverage_results_{dataset_name.split('/')[-1]}_{model_name}"
    if not os.path.exists(coverage_dir):
        os.makedirs(coverage_dir)
    
    dataset = load_dataset(dataset_name)
    dataset = dataset["test"]
    norm_data = read_json_to_dict(suspicious_funcs_file)
    selected_tests = read_json_to_dict(selected_tests_file)
    
    #verified_claude_fixed
    only_run = ['pytest-dev__pytest-7236', 'pytest-dev__pytest-5787', 'pytest-dev__pytest-5631', 'pytest-dev__pytest-6202', 'pytest-dev__pytest-5840', 'pytest-dev__pytest-7571', 'pytest-dev__pytest-8399', 'pytest-dev__pytest-6197', 'pytest-dev__pytest-5809', 'pytest-dev__pytest-7982', 'pytest-dev__pytest-7490', 'pytest-dev__pytest-7205', 'pytest-dev__pytest-7432', 'pytest-dev__pytest-5262', 'pytest-dev__pytest-7521', 'pytest-dev__pytest-7324']

    def process_item(item):
        instance_id = item["instance_id"]
        res_dir = f"{coverage_dir}/{instance_id}/{instance_id}_coverage"
        if instance_id not in only_run:
            print(f"Skipping {instance_id} as it is not in the only_run list")
            return
        
        if not os.path.exists(coverage_dir):
            os.makedirs(coverage_dir)
        if os.path.exists(res_dir):
            print(f"Skipping {instance_id} as it already has coverage data")
            return
        if instance_id not in norm_data:
            print(f"Skipping {instance_id} as it has no normalized functions")
            return
        suspicious_funcs = norm_data[instance_id]
        test_files = selected_tests[instance_id]["selected_test_files"]
        filtered_test_files = [test_file for test_file in test_files if not test_file.endswith("/conftest.py")]
        # modules = get_test_modules(suspicious_funcs)

        run_coverage_docker(instance_id, filtered_test_files, coverage_dir, dataset_name)

    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_item, item)
            for item in dataset
            if item['instance_id'] in only_run
        ]  #
        # if item['instance_id'] == "django__django-10097"

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing"
        ):
            try:
                future.result()
            except Exception as e:
                print(f"Error during processing: {e}")
