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


def run_coverage_docker(instance_id, test_methods, cov_dir, max_workers="4"):
    print(
        f"Running coverage for instance {instance_id} with {len(test_methods)} test methods"
    )
    cmd = [
        "python",
        "-m",
        "swebench.harness.run_evaluation",
        "--dataset_name",
        "princeton-nlp/SWE-bench_Verified",
        "--predictions_path",
        "gold",
        "--max_workers",
        max_workers,
        "--run_id",
        cov_dir,
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
    coverage_dir = args[1]
    suspicious_funcs_file = args[2]
    selected_tests_file = args[3]

    dataset = load_dataset(dataset_name)
    dataset = dataset["test"]
    norm_data = read_json_to_dict(suspicious_funcs_file)
    selected_tests = read_json_to_dict(selected_tests_file)

    def process_item(item):
        instance_id = item["instance_id"]
        res_dir = f"{coverage_dir}/{instance_id}/.coveragerc"
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
        # modules = get_test_modules(suspicious_funcs)

        run_coverage_docker(instance_id, test_files, coverage_dir)

    with ProcessPoolExecutor(max_workers=7) as executor:
        futures = [
            executor.submit(process_item, item)
            for item in dataset
            if "django" not in item["instance_id"]
        ]  #
        # if item['instance_id'] == "django__django-10097"

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing"
        ):
            try:
                future.result()
            except Exception as e:
                print(f"Error during processing: {e}")
