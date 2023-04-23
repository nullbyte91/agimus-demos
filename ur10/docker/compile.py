import os
import subprocess
import sys
from pathlib import Path
import yaml

PYTHON_EXECUTABLE="/usr/bin/python3"

class BuildError(Exception):
    def __init__(self, function_name, error_message):
        self.function_name = function_name
        self.error_message = error_message
        super().__init__(f"Error in {function_name}: {error_message}")

def run_cmake_and_make(cmake_args, env=None):
    try:
        subprocess.run(["cmake", ".."] + cmake_args, check=True, env=env)
    except subprocess.CalledProcessError as e:
        raise BuildError("run_cmake_and_make", f"cmake command failed: {e}")

    try:
        subprocess.run(["make", "-j1"], check=True)
    except subprocess.CalledProcessError as e:
        raise BuildError("run_cmake_and_make", f"make command failed: {e}")

    try:
        subprocess.run(["make", "install"], check=True)
    except subprocess.CalledProcessError as e:
        raise BuildError("run_cmake_and_make", f"make install command failed: {e}")

def compile_standard_project(project_name, cmake_flags, install_dir, env):
    cmake_args = [f"-D{flag}" for flag in cmake_flags]
    cmake_args += [
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DCMAKE_INSTALL_LIBDIR=lib",
        f"-DCMAKE_BUILD_TYPE=Release",
        f"-DENFORCE_MINIMAL_CXX_STANDARD=ON",
        f"-DINSTALL_DOCUMENTATION=ON",
        f"-DCMAKE_CXX_FLAGS_RELWITHDEBINFO='-g -O3 -DNDEBUG'",
    ]
    print("#### CMAKE FLAG ##########")
    print(cmake_args)
    run_cmake_and_make(cmake_args, env)

def compile_pal_msgs_project(project_name, cmake_flags, install_dir, src_dir, env = None):
    project_path = Path(src_dir)
    cmake_args = [f"-D{flag}" for flag in cmake_flags]
    cmake_args += [
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DCMAKE_INSTALL_LIBDIR=lib",
    ]

    package_order = [
        "pal_interaction_msgs",
        "pal_wifi_localization_msgs",
        "pal_web_msgs",
        "pal_walking_msgs",
        "pal_visual_localization_msgs",
        "pal_vision_msgs",
        "pal_video_recording_msgs",
        "pal_tablet_msgs",
        "pal_simulation_msgs",
        "pal_navigation_msgs",
        "pal_multirobot_msgs",
        "pal_motion_model_msgs",
        "pal_hardware_interfaces",
        "pal_device_msgs",
        "pal_detection_msgs",
        "pal_control_msgs",
        "pal_common_msgs",
        "pal_behaviour_msgs",
    ]

    for package_name in package_order:
        subdir = project_path / package_name
        if subdir.is_dir() and (subdir / "CMakeLists.txt").is_file():
            build_dir = "build"
            build_dir.mkdir(exist_ok=True)
            os.chdir(build_dir)
            print("############## :{}".format(build_dir))

            run_cmake_and_make(cmake_args, env)

            os.chdir(src_dir)

def compile_image_pipeline_project(project_name, cmake_flags, install_dir, src_dir, env = None):
    project_path = Path(src_dir)
    cmake_args = [f"-D{flag}" for flag in cmake_flags]
    cmake_args += [
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DCMAKE_INSTALL_LIBDIR=lib",
    ]

    package_order = [
        "camera_calibration",
        "depth_image_proc",
        "image_pipeline",
        "image_proc",
        "image_publisher",
        "image_rotate",
        "stereo_image_proc",
    ]

    for package_name in package_order:
        subdir = project_path / package_name
        if subdir.is_dir() and (subdir / "CMakeLists.txt").is_file():
            build_dir = subdir / "build"
            build_dir.mkdir(exist_ok=True)
            os.chdir(build_dir)
            print("############## :{}".format(build_dir))

            run_cmake_and_make(cmake_args, env)

            os.chdir(src_dir)

def compile_vision_opencv_project(project_name, cmake_flags, install_dir, src_dir, env = None):
    project_path = Path(src_dir)
    cmake_args = [f"-D{flag}" for flag in cmake_flags]
    cmake_args += [
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DCMAKE_INSTALL_LIBDIR=lib",
    ]

    package_order = [
        "cv_bridge",
        "image_geometry",
        "vision_opencv",
    ]

    for package_name in package_order:
        subdir = project_path / package_name
        if subdir.is_dir() and (subdir / "CMakeLists.txt").is_file():
            build_dir = subdir / "build"
            build_dir.mkdir(exist_ok=True)
            os.chdir(build_dir)
            print("############## :{}".format(build_dir))

            run_cmake_and_make(cmake_args, env)

            os.chdir(src_dir)

def compile_universal_robot(project_name, cmake_flags, install_dir, src_dir, env=None):
    project_path = Path(src_dir)
    cmake_args = [f"-D{flag}" for flag in cmake_flags]
    cmake_args += [
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DCMAKE_INSTALL_LIBDIR=lib",
    ]
    for subdir in project_path.iterdir():
        if subdir.is_dir() and (subdir / "CMakeLists.txt").is_file():
            build_dir = subdir / "build"
            build_dir.mkdir(exist_ok=True)
            os.chdir(build_dir)

            run_cmake_and_make(cmake_args, env)

            os.chdir(src_dir)

def compile_project(project_name, cmake_flags, install_dir, src_dir):
    project_path = Path(project_name)

    print(f"Compiling {project_name}...")

    project_path.mkdir(parents=True, exist_ok=True)
    os.chdir(project_path)

    env = os.environ.copy()
    env["CMAKE_PREFIX_PATH"] = f"{install_dir}:{env.get('CMAKE_PREFIX_PATH', '')}"

    python_executable = sys.executable
    cmake_flags = [flag.replace("${PYTHON_EXECUTABLE}", python_executable) for flag in cmake_flags if flag is not None]

    # Replace the placeholder with the actual install directory
    cmake_flags = [flag.replace("${INSTALL_DIR}", install_dir) for flag in cmake_flags if flag is not None]

    if project_name == "universal_robot":
        compile_universal_robot(project_name, cmake_flags, install_dir, src_dir, env)
    elif project_name == "pal_msgs":
        compile_pal_msgs_project(project_name, cmake_flags, install_dir, src_dir, env)
    elif project_name == "image_pipeline":
        compile_image_pipeline_project(project_name, cmake_flags, install_dir, src_dir, env)
    elif project_name == "vision_opencv":
        compile_vision_opencv_project(project_name, cmake_flags, install_dir, src_dir, env)
    else:
        compile_standard_project(project_name, cmake_flags, install_dir, env)

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

def get_compilation_order_for_package(data, package_name):
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

    visit(package_name)

    return compilation_order

def handle_build_options(project_info):
    build_options = project_info.get("build_options", [])
    build_type = "Release"
    build_testing = "ON"

    for option in build_options:
        if "BUILD_TYPE" in option:
            build_type = option.split("=")[1]
        elif "BUILD_TESTING" in option:
            build_testing = option.split("=")[1]

    if build_type == "Debug":
        build_folder = "build"
    else:
        build_folder = "build-rel"
        build_testing = "OFF"

    project_info["cmake_flags"].append(f"-DBUILD_TESTING={build_testing}")
    return build_folder

def main():
    if len(sys.argv) < 3:
        print("Usage: python compile_script.py <yaml_file> <install_directory> [<package_name>]")
        sys.exit(1)

    yaml_file = sys.argv[1]
    install_dir = sys.argv[2]
    package_name = None
    if len(sys.argv) == 4:
        package_name = sys.argv[3]

    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    projects = {item["name"]: {**item, "dependencies": item.get("dependencies", []), "cmake_flags": item.get("cmake_flags", [])} for item in data}
    src_path = Path("/home/nullbyte/Desktop/updated_react/react_ws/src")

    if package_name:
        # Get the compilation order for the given package and its dependencies
        compilation_order = get_compilation_order_for_package(data, package_name)
    else:
        # Get the compilation order for all projects
        compilation_order = get_compilation_order(data)
    print(compilation_order)

    for project_name in compilation_order:
        print(project_name)
        project_info = projects.get(project_name)
        if not project_info:
            print(f"No information found for {project_name} in dependencies.yaml. Skipping.")
            continue
        sub_path = project_info["sub"]
        project_path = src_path / sub_path / project_name
        abs_path = os.path.abspath(project_path)
        print(abs_path)
        print(project_path)
        if project_name == "pal_msgs" or project_name == "universal_robot":
            os.chdir(project_path)
            # os.chdir(abs_path)
            cmake_flags = project_info["cmake_flags"]
            try:
                compile_project(project_name, cmake_flags, install_dir, abs_path)
            except BuildError as e:
                print(e)
            compile_project(project_name, cmake_flags, install_dir, abs_path)
            os.chdir(src_path)
        elif project_path.joinpath("CMakeLists.txt").is_file():
            print(f"Compiling high-level project: {project_name}")

            os.chdir(abs_path)
            cmake_flags = project_info["cmake_flags"]
            try:
                compile_project(project_name, cmake_flags, install_dir, abs_path)
            except BuildError as e:
                print(e)
            os.chdir(src_path)
        else:
            print(f"No CMakeLists.txt found for {project_name}. Skipping.")

    print("All projects compiled successfully.")

if __name__ == "__main__":
    main()
