import os
import subprocess
import sys
from pathlib import Path
import yaml

PYTHON_EXECUTABLE="/usr/bin/python3"

def compile_project(project_name, cmake_flags, install_dir):
    #print(install_dir)

    project_path = Path(project_name)

    print(f"Compiling {project_name}...")

    project_path.mkdir(parents=True, exist_ok=True)
    os.chdir(project_path)

    env = os.environ.copy()
    env["CMAKE_PREFIX_PATH"] = f"{install_dir}:{env.get('CMAKE_PREFIX_PATH', '')}"

    #print(f"Environment: {env}")  # Print the environment

    python_executable = sys.executable
    cmake_flags = [flag.replace("${PYTHON_EXECUTABLE}", python_executable) for flag in cmake_flags if flag is not None]

    # Replace the placeholder with the actual install directory
    cmake_flags = [flag.replace("${INSTALL_DIR}", install_dir) for flag in cmake_flags if flag is not None]

    cmake_args = [f"-D{flag}" for flag in cmake_flags]
    print(f"cmake_args: {cmake_args}")  # Print the cmake_args

    subprocess.run(["cmake", "..", "-DCMAKE_INSTALL_PREFIX=${install_dir}"] + cmake_args, check=True, env=env)

    subprocess.run(["make"], check=True)
    subprocess.run(["make", "install"], check=True)

    os.chdir("../../")

    print(f"Done compiling {project_name}.")

def get_compilation_order(data):
    projects = {item["name"]: {**item, "dependencies": item.get("dependencies", []), "cmake_flags": item.get("cmake_flags", [])} for item in data}
    compilation_order = []
    visited = set()

    def visit(project_name):
        if project_name not in visited:
            visited.add(project_name)
            project_info = projects.get(project_name)
            if project_info and "dependencies" in project_info:
                for dep_name in project_info["dependencies"]:
                    visit(dep_name)
            compilation_order.append(project_name)

    for project_info in data:
        visit(project_info["name"])

    return compilation_order

def main():
    if len(sys.argv) != 3:
        print("Usage: python compile_script.py <yaml_file> <install_directory>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    install_dir = sys.argv[2]

    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    projects = {item["name"]: {**item, "dependencies": item.get("dependencies", []), "cmake_flags": item.get("cmake_flags", [])} for item in data}
    src_path = Path("/home/nullbyte/Desktop/updated_react/react_ws/src")

    # Get the compilation order from the YAML file
    compilation_order = get_compilation_order(data)
    print(compilation_order)
    for project_name in compilation_order:
        project_info = projects.get(project_name)
        if not project_info:
            print(f"No information found for {project_name} in dependencies.yaml. Skipping.")
            continue

        sub_path = project_info["sub"]
        project_path = src_path / sub_path / project_name
        abs_path = os.path.abspath(project_path)

        if project_path.joinpath("CMakeLists.txt").is_file():
            print(f"Compiling high-level project: {project_name}")

            os.chdir(project_path)
            cmake_flags = project_info["cmake_flags"]
            compile_project("build", cmake_flags, install_dir)
            os.chdir(src_path)
        else:
            print(f"No CMakeLists.txt found for {project_name}. Skipping.")

    print("All projects compiled successfully.")

if __name__ == "__main__":
    main()
