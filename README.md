# Core Translator

## Version 1.0.0 Unstable

This is an application includes tools and basic structures for generating Aplan Files.

It provides tools such as:
    - TranlatorTool - A basic tool that performs translation of a specified file (SV or VHDL) depending on the provided translator.
    - Testing Tool - Generation testing tool, generates files and compares them with reference ones.
    - Regeneration Tool - File regeneration tool.

## TranlatorTool Base Preparation
```python
    if __name__ == "__main__":
        tool = BaseTool("ToolName") # Create Base tool object
        tool.setType("sv") # Set the testing file type
        tool.start("file_path","path to result") # if "path to result" not specified , tool create default "result" folder

```

## Testing Tool Preparation


Requires a json file with example data used for the test.

```json
[
        {
            "file": "examples/initial/initial.sv",
            "result_dir": "examples/initial/test_result",
            "aplan_dir": "examples/initial/aplan"
        }
]
```


```python
    if __name__ == "__main__":
        tool = BaseTool() # Create Base tool object
        tool.setType("sv") # Set the testing file type
        tool.testsStart("path to json file with examples data")
```


## Regeneration Tool  Preparation

For this tool you can have the same example file as for the Testing tool or run one specific example

```python
    if __name__ == "__main__":
        tool = BaseTool() # Create Base tool object
        tool.setType("sv") # Set the regeneration file type
        tool.regenerationStart(examples_list_path = "path to json file with examples data", )
```

```python
    if __name__ == "__main__":
        tool = BaseTool() # Create Base tool object
        tool.setType("sv") # Set the regeneration file type
        tool.regenerationStart(path_to_sv = "path to exampe file")
```

### Code Quality and Standards

This project uses several tools to enforce code quality and maintain a clean Git history.

- **[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)**: We follow the Conventional Commits specification to standardize commit messages. This helps in understanding the purpose of each commit and allows for automated tools to handle versioning and changelog generation.
- **[Commitizen](https://commitizen-tools.github.io/commitizen/)**: We use Commitizen to validate commit messages against the Conventional Commits standard.
- **[Black](https://github.com/psf/black)**: We use Black to automatically format Python code, ensuring a consistent style across the entire project.

To ensure your commits and code adhere to these standards, we highly recommend setting up the Git hooks. You can do this by running the following commands:

```bash
chmod +x scripts/bootstrap.sh 
./scripts/bootstrap.sh
```
