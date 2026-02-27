import os
import shutil

data_dir = r"D:\SHLT\cqgs\cqbylw\data"
archive_dir = os.path.join(data_dir, "archive_v1")

files_to_archive = ["final_data.csv", "tfp_result.csv", "实证结果报告.md"]

for file in files_to_archive:
    src = os.path.join(data_dir, file)
    if os.path.exists(src):
        dst = os.path.join(archive_dir, file)
        try:
            shutil.move(src, dst)
            print(f"Archived {file} to {dst}")
        except Exception as e:
            print(f"Error archiving {file}: {e}")
    else:
        print(f"{file} not found, skipping.")
