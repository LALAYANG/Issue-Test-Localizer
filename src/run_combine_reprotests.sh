dir=(
    /home/yang/Issue-Test-Localizer/reproduction_test/claude_lite
    /home/yang/Issue-Test-Localizer/reproduction_test/claude_verified
    /home/yang/Issue-Test-Localizer/reproduction_test/gpt4o_verified
    /home/yang/Issue-Test-Localizer/reproduction_test/gpt4o_lite
)

for input_dir in "${dir[@]}"; do
    output_file="/home/yang/Issue-Test-Localizer/inputs/combined_${input_dir##*/}.json"
    python3 src/combine_reproduction_tests.py "$input_dir" "$output_file" --dedup
done