import yaml


def load_yaml_properties(md_file_path):
    """
    A function to load YAML properties from a file.

    Parameters:
    md_file_path (str): The file path of the Markdown file containing YAML properties.

    Returns:
    dict or None: The parsed YAML data if successful, or None if there was an error.
    """
    yaml_content = []
    with open(md_file_path, "r") as file:
        # Read the first line to check if it starts with ---
        first_line = file.readline()
        if first_line.strip() != "---":
            print("No YAML front matter found.")
            return None

        # Read the rest of the YAML content until the next ---
        for line in file:
            if line.strip() == "---":
                break
            yaml_content.append(line)

    # Join the lines and parse the YAML content
    yaml_str = "".join(yaml_content)
    try:
        data = yaml.safe_load(yaml_str)
        return data
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return None


def dump_yaml_properties(md_file_path: str, new_data: dict):
    """
    A function to update YAML properties in a Markdown file.

    Args:
        md_file_path (str): The file path of the Markdown file.
        new_data (dict): The new YAML properties to be updated.

    Returns:
        None
    """
    with open(md_file_path, "r+") as file:
        lines = file.readlines()

    yaml_content = []
    markdown_content_start = 0
    in_yaml = False

    # Iterate over lines to find and extract the current YAML section
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_yaml:
                in_yaml = True  # Start of YAML section
            else:
                markdown_content_start = i + 1  # End of YAML section
                break
        elif in_yaml:
            yaml_content.append(line)

    # Parse the existing YAML content if any
    existing_data = yaml.safe_load("".join(yaml_content)) if yaml_content else {}

    # Update the existing YAML data with the new data
    updated_data = {**existing_data, **new_data}

    # Convert the updated YAML data back to a string
    updated_yaml_str = yaml.safe_dump(updated_data, default_flow_style=False)

    # Write the updated YAML and the unchanged Markdown content back to the file
    with open(md_file_path, "w") as file:
        file.write("---\n")
        file.write(updated_yaml_str)
        file.write("---\n")
        file.writelines(lines[markdown_content_start:])


def create_yaml_properties(md_file_path: str, new_data: dict):
    """
    A function to create YAML properties in a file.

    Parameters:
    md_file_path (str): The file path where the YAML properties will be created.
    new_data (dict): The new YAML data to be added to the file.

    Returns:
    None
    """
    with open(md_file_path, "w") as file:
        file.write("---\n")
        yaml.dump(new_data, file, default_flow_style=False)
        file.write("---\n")
