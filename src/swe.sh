# python -m swebench.harness.run_evaluation \
#     --dataset_name princeton-nlp/SWE-bench_Verified \
#     --predictions_path gold \
#     --max_workers 1 \
#     --run_id test\
#     --instance_ids astropy__astropy-12907 \
#     --test_methods '["astropy/modeling/tests/test_separable.py::test_coord_matrix", "astropy/modeling/tests/test_separable.py::test_cdot", "astropy/modeling/tests/test_separable.py::test_cstack", "astropy/modeling/tests/test_separable.py::test_arith_oper", "astropy/modeling/tests/test_separable.py::test_separable[compound_model0-result0]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model1-result1]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model2-result2]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model3-result3]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model4-result4]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model5-result5]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model7-result7]", "astropy/modeling/tests/test_separable.py::test_separable[compound_model8-result8]", "astropy/modeling/tests/test_separable.py::test_custom_model_separable"]'
    

python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Verified \
    --predictions_path gold \
    --max_workers 1 \
    --run_id test00\
    --instance_ids django__django-15930  \
    --test_methods '[]'
    
#sympy__sympy-18199 psf__requests-1766 
# python -m swebench.harness.run_evaluation \
#     --dataset_name princeton-nlp/SWE-bench_Verified \
#     --predictions_path gold \
#     --max_workers 1 \
#     --run_id test\
#     --instance_ids pydata__xarray-3993 \
#     --test_methods '["xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access", "xarray/tests/test_backends_chunks.py::test_build_grid_chunks"]'
    
# '["tests/test_adapters.py::test_request_url_trims_leading_path_separators", "tests/test_help.py::test_system_ssl", "tests/test_help.py::test_idna_without_version_attribute", "tests/test_lowlevel.py::test_chunked_upload"]'

# python -m swebench.harness.run_evaluation \
#     --dataset_name princeton-nlp/SWE-bench_Verified \
#     --predictions_path gold \
#     --max_workers 1 \
#     --run_id test\
#     --instance_ids pytest-dev__pytest-5840 \
#     --test_methods '["testing/test_argcomplete.py::TestArgComplete::test_compare_with_compgen"]'
    
    
# "["astropy/wcs/wcsapi/tests/test_high_level_api.py::test_objects_to_values","astropy/wcs/wcsapi/tests/test_high_level_api.py::test_serialized_classes"]"
# use --predictions_path "gold" to verify the gold patches
# use --run_id to name the evaluation run