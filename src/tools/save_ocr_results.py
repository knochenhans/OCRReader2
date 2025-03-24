import json
import sys
import os

project_ids = [
    "2e723ee8-e6b1-4b30-bfef-0513a46874c0",
    "4c928d84-d593-4dcd-9ac3-d29de1e70c81",
    "6a45f130-cd74-43bd-88e7-dfa3925e3cc3",
    "7bc93723-f4ae-409b-919a-0e005d55e455",
    "b5650b08-80bb-491b-b52c-5c11f0e5cd33",
    "c171fbbe-b5d8-4efd-9a11-dc5d43f503ad",
    "d08d352d-9613-417a-a455-c5982fc3526a",
]

project_root = "/home/andre/.local/share/ocrreader/projects/"


for project_id in project_ids:
    for page_file in os.listdir(f"{project_root}/{project_id}/pages"):
        if page_file.endswith(".json"):
            with open(f"{project_root}/{project_id}/pages/{page_file}") as f:
                page = json.load(f)

                boxes = page["page"]["layout"]["boxes"]

                for box in boxes:
                    if "ocr_results" in box:
                        ocr_results = box.pop("ocr_results")  # Remove from page file

                        if not os.path.exists(
                            f"{project_root}/{project_id}/ocr_results"
                        ):
                            os.makedirs(f"{project_root}/{project_id}/ocr_results")

                        with open(
                            f"{project_root}/{project_id}/ocr_results/{box['id']}.json",
                            "w",
                        ) as f:
                            json.dump(ocr_results, f)

            # Save the updated page file without "ocr_results"
            with open(f"{project_root}/{project_id}/pages/{page_file}", "w") as f:
                json.dump(page, f)
