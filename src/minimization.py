import json
import os
import re
from collections import defaultdict

import coverage
from collect_rt_susfunc import get_func_lines_code
from process_norm import get_base_commit

from model_config import prompt_model


def prompt_model_to_select_test(
    tests, file, func, function_body, logger, model_name="GCP/claude-3-7-sonnet"
):
    tests_lines = "\n".join(sorted(tests))
    prompt = f"""
You are an expert in test minimization. 
For function `{func}` in file `{file}`, below are the function body and the tests that cover same lines of the function.
Your task is to minimize the test suite, select top three tests: 
###Function Body###
---BEGIN FUNCTION BODY---
{function_body}
---END FUNCTION BODY---
###Tests Covering the Function###
---BEGIN TESTS---
{tests_lines}
---END TESTS---
You should follow the format below to provide your answer. Do not include any additional text or explanations.
Here is an example:
---BEGIN SELECTED TESTS---
test1
test2
...
---END SELECTED TESTS---
"""
    logger.info(f"Prompt for model {model_name}:\n{prompt}\n")
    response = prompt_model(model_name, prompt)
    logger.info(f"Response\n{response}\n")
    if response:
        if (
            "---BEGIN SELECTED TESTS---" in response
            and "---END SELECTED TESTS---" in response
        ):
            selected_tests = (
                response.split("---BEGIN SELECTED TESTS---")[1]
                .split("---END SELECTED TESTS---")[0]
                .strip()
                .split("\n")
            )
            selected_tests = [test.strip() for test in selected_tests if test.strip()]
            return selected_tests
    else:
        logger.warning(
            f"No response from model {model_name} for function {func} in file {file}."
        )


def minimize_tests(line_to_tests, file, func, function_body, logger, filtered_tests):

    # invert line->tests to test->set of (file, line)
    test_to_lines = defaultdict(set)
    for line_key, tests in line_to_tests.items():
        for test in tests:
            if test not in filtered_tests:
                logger.warning(f"Test {test} not in passed tests, skipping.")
                continue
            if test:
                test_to_lines[test].add(line_key)

    uncovered_lines = set(line_to_tests.keys())
    selected_tests = []

    logger.info("Inverted test coverage map (test -> lines):")
    s = {k: sorted(list(v)) for k, v in test_to_lines.items()}
    for k in s:
        logger.info(f"{k}:\n {s[k]}")

    while uncovered_lines:
        test_coverage = []
        max_coverage_size = 0

        for test, lines in test_to_lines.items():
            covered = lines & uncovered_lines
            size = len(covered)
            if size > 0:
                if size > max_coverage_size:
                    max_coverage_size = size
                    test_coverage = [(test, covered)]
                elif size == max_coverage_size:
                    test_coverage.append((test, covered))

        if not test_coverage:
            logger.warning(
                f"No more tests cover the remaining {len(uncovered_lines)} lines"
            )
            break

        logger.info(
            f"Test coverage found {len(test_coverage)} tests covering {len(uncovered_lines)} uncovered lines"
        )
        logger.info(f"Test coverage details: {test_coverage}")
        # Handle ties
        if len(test_coverage) > 1:
            candidates = [test for test, _ in test_coverage]
            if len(candidates) <= 3:
                chosen_test = candidates
            else:
                chosen_test = prompt_model_to_select_test(
                    candidates, file, func, function_body, logger
                )
            selected_tests.extend(chosen_test)
            for test in chosen_test:
                uncovered_lines -= test_to_lines[test]
        else:
            test, covered = test_coverage[0]
            selected_tests.append(test)
            uncovered_lines -= covered

    return list(set(selected_tests))


def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def query_coverage_data(
    instance_id, tests, modified_file, modified_lines, cov_dir_base, logger
):
    cov_dir = os.path.join(cov_dir_base, instance_id)
    if not os.path.exists(cov_dir):
        logger.info(
            f"Coverage directory does not exist for instance {instance_id}: {cov_dir}"
        )
        return None
    all_contexts = {}
    cov = coverage.Coverage(data_file=os.path.join(cov_dir, ".coverage"))
    cov.load()
    data = cov.get_data()
    files = data.measured_files()
    if len(files) == 0:
        logger.info(f"No coverage data found for instance {instance_id}")
        return None

    for file in files:
        format_file = file.replace("/testbed/", "")
        format_file = format_file.replace(
            "/data/workspace/yang/agent/temp_repos/astropy/", ""
        )
        if modified_file == format_file:
            lineno_contexts = data.contexts_by_lineno(file)
            for lineno, contexts in lineno_contexts.items():
                if lineno in modified_lines:
                    if lineno not in all_contexts:
                        all_contexts[lineno] = []
                    all_contexts[lineno].extend(contexts)
    return all_contexts


import json
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed


def setup_logger(instance_id, log_dir):  # ="ten_files_cov_265_0_minimization_logs"
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(instance_id)
    logger.setLevel(logging.INFO)

    # Prevent propagation to root logger (avoid duplicate messages)
    logger.propagate = False

    # Avoid duplicate handlers
    if not logger.handlers:
        log_path = os.path.join(log_dir, f"{instance_id}.log")
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def process_instance(
    instance_id, tests, suspicious_info, cov_dir, passed_tests, log_dir
):
    logger = setup_logger(instance_id, log_dir)

    if len(tests) <= 5 and len(tests) > 0:
        logger.info(
            f"Instance {instance_id} has {len(tests)} tests, skip minimization!"
        )
        return (instance_id, tests)

    if instance_id not in suspicious_info:
        logger.warning(
            f"Instance {instance_id} not found in suspicious info, skipping..."
        )
        return (instance_id, [])

    normalized_funcs = suspicious_info[instance_id]
    base_commit, repo_name = get_base_commit(instance_id)
    all_selected_tests = []

    logger.info(f"*************** Processing instance {instance_id} ***************")
    logger.info(tests)
    for t in tests:
        if "::" in t:
            all_selected_tests = list(set(tests))
            logger.info(f"Tests {len(tests)}:\n {tests} \n")
            logger.info(f"*************** END instance {instance_id} ***************\n")
            return (instance_id, all_selected_tests)

    combined_line_to_tests = defaultdict(list)
    function_info = {}
    for file in normalized_funcs:
        linenos, local_repo_path = get_func_lines_code(
            repo_name, base_commit, file, normalized_funcs[file]
        )
        for func in linenos:
            lines, func_code = linenos[func]
            result = query_coverage_data(
                instance_id, tests, file, lines, cov_dir, logger
            )

            for line, tests_list in result.items():
                key = (file, line)
                combined_line_to_tests[key].extend(t for t in tests_list if t != "")

            function_info[(file, func)] = func_code

    # Log before minimization
    all_tests = set(t for testlist in combined_line_to_tests.values() for t in testlist)
    logger.info(f"\n#Before Minimization: {len(all_tests)} unique tests")

    tests = list(all_tests)
    if len(passed_tests) and instance_id in passed_tests:
        if len(passed_tests[instance_id]) > 0:
            tests = [test for test in all_tests if test in passed_tests[instance_id]]
        logger.info(f"Filtered passed tests, remaining tests: {tests}")
    if len(tests) == 0:
        tests = list(all_tests)

    # Perform minimization on combined coverage
    file_str = ", ".join(sorted(set(f for f, _ in function_info)))
    func_str = ", ".join(sorted(set(f for _, f in function_info)))
    selected_tests = minimize_tests(
        line_to_tests=combined_line_to_tests,
        file=file_str,
        func=func_str,
        function_body=function_info,
        logger=logger,
        filtered_tests=tests,
    )

    logger.info(f"#After Minimization: {len(selected_tests)} tests selected\n")
    logger.info("Selected tests:")
    for test in selected_tests:
        logger.info(f"  {test}")

    # Collect into master test list if needed
    all_selected_tests.extend(selected_tests)
    logger.info(f"*************** END instance {instance_id} ***************\n")

    return (instance_id, all_selected_tests)


from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


def process_data(
    tests_info, suspicious_info, cov_dir, result_dir, result_json, passed_tests, log_dir
):
    os.makedirs(result_dir, exist_ok=True)

    instances_to_run = [
        instance_id
        for instance_id in tests_info
        if not os.path.exists(os.path.join(result_dir, f"{instance_id}.jsonl"))
    ]  # if instance_id == "astropy__astropy-12907"

    # read existing results save to results_to_write
    with open(result_json, "r") as f:
        existing_results = json.load(f)

    results_to_write = []

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {
            executor.submit(
                process_instance,
                instance_id,
                tests_info[instance_id],
                suspicious_info,
                cov_dir,
                passed_tests,
                log_dir,
            ): instance_id
            for instance_id in instances_to_run
            if instance_id
            not in existing_results  # if instance_id == "astropy__astropy-7166"
        }

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing"
        ):
            try:
                # if True:
                instance_id, selected_tests = future.result()
                if selected_tests:
                    line = json.dumps({instance_id: selected_tests})
                    results_to_write.append((instance_id, line))
            except Exception as e:
                instance_id = futures[future]
                print(f"Error in instance {instance_id}: {e}")

    # JSONL results after parallel processing
    for instance_id, line in results_to_write:
        instance_path = os.path.join(result_dir, f"{instance_id}.jsonl")
        with open(instance_path, "w") as f:
            f.write(line + "\n")

    # merge all into final JSON
    merged = {}
    for instance_id, line in existing_results.items():
        merged[instance_id] = line
    for instance_id, line in results_to_write:
        try:
            merged.update(json.loads(line))
        except json.JSONDecodeError:
            print(f"Error decoding line for {instance_id}")

    with open(result_json, "w") as f:
        json.dump(merged, f, indent=2)


def combine_tests(data):
    result = {}
    for instance_id, files in data.items():
        all_tests = set()
        for methods in files.values():
            for test_list in methods.values():
                all_tests.update(test_list)
        tests = list(set(sorted(all_tests)))
        result[instance_id] = [test for test in tests if test != ""]
    return result


if __name__ == "__main__":
    tests_json = "otter_inputs/final/all_tests_before_minimization_494.json"

    cov_dir = "ten_file_covs/"
    result_dir = "agentless_results_jsonl_final"
    result_json = "agentless_coverage_tests_mini_model_final.json"
    log_dir = "agentless_minimization_logs"

    suspicious_json = "result_files/confirmed_suspicious_funcs.json"

    suspicious_info = read_json_file(suspicious_json)

    tests_info = read_json_file(tests_json)

    passed_tests_json = "fq_test_results.json"
    passed_tests = read_json_file(passed_tests_json)

    process_data(
        tests_info,
        suspicious_info,
        cov_dir,
        result_dir,
        result_json,
        passed_tests,
        log_dir,
    )
