import json
import os


def generate_files(launch_json_path, output_directory):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Load the JSON data
    with open(launch_json_path, "r") as file:
        launch_config = json.load(file)

    # Parse each configuration
    for config in launch_config.get("configurations", []):
        name = config.get("name")
        if not name:
            continue  # Skip configurations without a name

        # Create OpenOCD single command shell script
        openocd_commands = ["#!/bin/bash"]
        config_files = " ".join(
            [f"-f {cfg_file}" for cfg_file in config.get("configFiles", [])]
        )
        openocd_command = f'openocd {config_files} -c "target create $_TARGETNAME cortex_m -endian little -rtos auto"'
        openocd_commands.append(openocd_command)

        openocd_filename = os.path.join(output_directory, f"{name}_openocd.sh")
        with open(openocd_filename, "w") as openocd_file:
            openocd_file.write("\n".join(openocd_commands))
        os.chmod(openocd_filename, 0o755)  # Make the file executable

        # Create GDB command shell script
        gdb_commands = ["#!/bin/bash"]
        executable = config.get("executable")
        gdb_commands.append(
            f"arm-none-eabi-gdb {os.path.join(executable)} -ex 'target extended-remote :3333' -ex 'load' "
        )

        gdb_filename = os.path.join(output_directory, f"{name}_gdb.sh")
        with open(gdb_filename, "w") as gdb_file:
            gdb_file.write("\n".join(gdb_commands))
        os.chmod(gdb_filename, 0o755)  # Make the file executable

    print(f"Command scripts generated in {output_directory}")


# Specify the path to the launch.json file and output directory
launch_json_path = ".vscode/launch.json"
output_directory = "scripts"

generate_files(launch_json_path, output_directory)
