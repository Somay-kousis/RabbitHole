import os
import json

data_dir = "/Users/apple/RabbitHole/app/courtroom/data"
output_file = "/Users/apple/RabbitHole/app/courtroom/rag/structure/nodes/law.json"

index = {
    "laws": {},
    "cases": {}
}

# Scan laws
laws_path = os.path.join(data_dir, "laws")
if os.path.exists(laws_path):
    for category in os.listdir(laws_path):
        cat_path = os.path.join(laws_path, category)
        if os.path.isdir(cat_path):
            index["laws"][category] = sorted([
                f.replace(".txt", "") for f in os.listdir(cat_path) if f.endswith(".txt")
            ])

# Scan cases
cases_path = os.path.join(data_dir, "cases")
if os.path.exists(cases_path):
    for category in os.listdir(cases_path):
        cat_path = os.path.join(cases_path, category)
        if os.path.isdir(cat_path):
            index["cases"][category] = sorted([
                f.replace(".txt", "") for f in os.listdir(cat_path) if f.endswith(".txt")
            ])

# Ensure parent directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w") as f:
    json.dump(index, f, indent=4)

total_laws = sum(len(v) for v in index["laws"].values())
total_cases = sum(len(v) for v in index["cases"].values())
print(f"Success: Generated doc index containing {total_laws} laws and {total_cases} cases.")
