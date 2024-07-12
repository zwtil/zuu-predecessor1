import os

from zrcl.markdown import create_yaml_properties


def pandoc_generate_file_from_data(
    outtype: str,
    template: str,
    data: dict,
    outname: str = "pandoc.out",
):
    """
    Generate a file using Pandoc from input data.

    Args:
        outtype (str): The output type of the generated file.
        template (str): The template to use for generating the file.
        data (dict): The input data to be used in the generated file.
        outname (str, optional): The name of the output file. Defaults to "pandoc.out".

    Returns:
        None

    This function generates a file using Pandoc from input data. It first calls the
    `create_yaml_properties` function to create YAML properties in the current working
    directory using the provided data. Then it uses the `os.system` function to run the
    `pandoc` command to generate the file. The command takes the input file "input.md",
    generates the output file with the specified name, and uses the specified output type,
    markdown as the input format, and the provided template.

    Note:
        The function assumes that the `pandoc` command is available in the system's PATH.
    """
    create_yaml_properties(os.path.join(os.getcwd(), "input.md"), data)

    os.system(
        f'pandoc input.md -o {outname} -f markdown -t {outtype} --template="{template}"'
    )
