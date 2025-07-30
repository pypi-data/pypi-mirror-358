import sys
import os
import glob
import safetensors
from safetensors import safe_open
from tabulate import tabulate
import numpy as np


def get_dtype_size(dtype):
    if "float" in str(dtype):
        return int(str(dtype).split("float")[1]) // 8
    elif "int" in str(dtype):
        return int(str(dtype).split("int")[1]) // 8
    else:
        return 4  # default to 4 bytes


def get_all_safetensor_files(file_path):
    base_path = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)

    # Check if the file is part of a split set
    if "-" in base_name and "of-" in base_name:
        pattern = base_name.split("-")[0] + "-*"
    else:
        pattern = os.path.splitext(base_name)[0] + "*"

    return sorted(glob.glob(os.path.join(base_path, pattern + ".safetensors")))


def print_safetensor_info(file_paths):
    try:
        table_data = []
        total_params = 0
        total_bytes = 0
        dtype_params = {}
        all_tensor_names = set()

        for file_path in file_paths:
            with safe_open(file_path, framework="pt", device="cpu") as f:
                tensor_names = f.keys()
                all_tensor_names.update(tensor_names)

                for name in tensor_names:
                    tensor = f.get_tensor(name)
                    size = " x ".join(map(str, tensor.shape))
                    dtype = str(tensor.dtype)
                    num_params = np.prod(tensor.shape)
                    bytes_size = num_params * get_dtype_size(dtype)

                    total_params += num_params
                    total_bytes += bytes_size

                    if dtype not in dtype_params:
                        dtype_params[dtype] = 0
                    dtype_params[dtype] += num_params

                    table_data.append(
                        [
                            name,
                            size,
                            dtype,
                            f"{num_params:,}",
                            f"{bytes_size / (1024 * 1024):.2f} MB",
                        ]
                    )

        # Print the table
        headers = ["Tensor Name", "Size", "Data Type", "Parameters", "Memory"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Print summary
        print("\nSummary:")
        print(f"Number of files processed: {len(file_paths)}")
        print(f"Total number of unique tensors: {len(all_tensor_names)}")
        print(f"Total parameters: {total_params:,}")
        print(f"Estimated model size: {total_bytes / (1024 * 1024):.2f} MB")

        print("\nParameters by dtype:")
        for dtype, count in dtype_params.items():
            print(f"{dtype}: {count:,} ({count/total_params*100:.2f}%)")

        # Get actual total file size
        total_file_size = sum(os.path.getsize(f) for f in file_paths) / (1024 * 1024)
        print(f"\nActual total file size: {total_file_size:.2f} MB")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_safetensor_file>")
        sys.exit(1)

    initial_file_path = sys.argv[1]
    all_file_paths = get_all_safetensor_files(initial_file_path)
    print(f"Found {len(all_file_paths)} safetensor files:")
    for path in all_file_paths:
        print(f"  {path}")
    print("\nProcessing files...\n")
    print_safetensor_info(all_file_paths)
