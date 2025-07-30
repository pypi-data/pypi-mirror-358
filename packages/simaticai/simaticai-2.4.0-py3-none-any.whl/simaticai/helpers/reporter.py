# Copyright (C) Siemens AG 2025. All Rights Reserved. Confidential.

"""
Classes to generate a report for a dataflow pipeline and local pipeline runner.
"""

from pathlib import Path
import requests
import logging
import zipfile
import json
import io

WARNINGS_HEADLINE = "## Warnings\n\n"
WARNING_LINE = "{name}:{filename}:{line_number} (W) {warning_msg}\n\n"

class ReportWriter:
    """
    Base class for report writers.
    """
    def __init__(self):
        self.report_path = None
        self.warnings_text = ""

    def set_path(self, report_path: Path):
        self.report_path = report_path

    def add_warning(self, name, filename, line_number, warning_msg):
        self.warnings_text += WARNING_LINE.format(name=name, filename=filename, line_number=line_number, warning_msg=warning_msg)

    def write_report(self):
        raise NotImplementedError("Subclasses should implement this method")

    def _write_warnings(self, file):
        file.write(WARNINGS_HEADLINE)
        file.write(self.warnings_text)


class ReportWriterHandler(logging.Handler):
    """
    A handler that can be given to a logger, so the report writer can capture logged warning messages
    """
    def __init__(self, report_writer: ReportWriter):
        super().__init__()
        self.report_writer = report_writer

    def emit(self, record):
        if record.levelno == logging.WARNING:
            self.report_writer.add_warning(record.name, record.filename, record.lineno, record.getMessage())


class ZipTreeElement:
    """
    A class to represent a file or folder in a zip file. During the recursive traversal of the zip file,
    the full name and file size are stored in this class.
    """
    def __init__(self, full_name, file_size):
        self.full_name = full_name
        self.file_size = file_size


PL_REPORT_HEADLINE = "# Report on `{pipeline_name}`\n\n"

PL_INFO_HEADLINE = "## Pipeline info\n\n"
PL_INFO = """- Author: {author}
- Created on: {created_on}
- Dataflow Pipeline version: {pipeline_version}
- Package ID: {package_id}
- Project name: {project_name}

Description: {description}

"""

# TODO: check other type of PlantUML diagrams if they look better or generating images into the markdown file
PL_STRUCTURE_HEADLINE = """## Pipeline structure

The pipeline structure is visualized using PlantUML. The components are connected by arrows. Metrics are drawn with dashed arrows.

"""

PL_STRUCTURE = "{source_component} {arrow} {target_component}: {variable_name} ({variable_type})\n"

PL_PACKAGE_VULNERABILITIES_HEADLINE = """## Package vulnerabilities

Package vulnerability information is collected from the [PyPI repository](https://pypi.org/).

| Package name | Package version | Vulnerability | Link | Details | Fixed in | In pipeline components |
|--------------|-----------------|---------------|------|---------|----------|------------------------|
"""
PL_PACKAGE_VULNERABILITY_CANNOT_BE_CHECKED = "| {package_name} | {package_version} | Can not be checked | - | - | - | {components} |\n"
PL_PACKAGE_VULNERABILITY_NOT_KNOWN = "| {package_name} | {package_version} | No known vulnerability | - | - | - | {components} |\n"
PL_PACKAGE_VULNERABILITY = "| {package_name} | {package_version} | {vulnerability_aliases} | {vulnerability_link} | {vulnerability_details} | {vulnerability_fixed_in} | {components} |\n"

PL_COMPONMENT_DEPENDENCIES_HEADLINE = "## Component dependencies for `{component_name}`\n\n"
PL_COMPONENT_DIRECT_DEPENDENCIES_HEADLINE = "### Direct dependencies\n\n"
PL_COMPONENT_DIRECT_DEPENDENCY = "- {dependency_name} {dependency_version}\n"
PL_COMPONENT_TRANSITIVE_DEPENDENCIES_HEADLINE = "### Transitive dependencies\n\n"
PL_COMPONENT_TRANSITIVE_DEPENDENCY = "- {dependency_name} {dependency_version}\n"

class PipelineReportWriter(ReportWriter):
    """
    A class to generate a report for a dataflow pipeline, including pipeline structure, component dependencies,
    and package vulnerabilities.

    Methods:
        set_path(report_path: Path):
            Sets the path where the report will be saved.
        set_pipeline_config(pipeline_config: dict):
            Sets the pipeline configuration and updates the pipeline info and structure.
        add_full_dependency_set(component_name: str, dependency_set: set[tuple]):
            Adds a full set of dependencies for a component and updates the vulnerability dictionary.
        add_direct_dependencies(component_name: str, direct_dependencies: dict):
            Adds direct dependencies for a component.
        add_warning(name, filename, line_number, warning_msg):
            Adds a warning to the report.
        write_report():
            Writes the report to the specified path.
    """
    def __init__(self):
        super().__init__()
        self.pipeline_config = {}  # pipeline config json
        self.pipeline_name = "Unnamed pipeline"

        # dependency_names and package_names are transformed dependency names (lowercase, underscore instead of dash)
        # set from outside
        self.component_direct_dependency_namelist = {}  # component -> list of dependency_names (with NO version)
        self.component_all_dependencies = {}  # component -> set of tuples of (dependency_name, dependency_version)
        # collected before writing
        self.component_direct_dependencies = {}  # component -> set of dependency_names
        self.component_transitive_dependencies = {}  # component -> set of tuples of (dependency_name, dependency_version)

        self.vulnerability_dict = {}  # (package_name, package_version) -> vulnerabilities (None | list of dictionaries)

        # report text sections to fill
        self.pipeline_structure_text = ""
        self.pipeline_info_text = ""
        self.warnings_text = ""

    def set_pipeline_config(self, pipeline_config: dict):
        self.pipeline_config = pipeline_config
        self._set_pipeline_info()
        self._set_pipeline_structure()

    @staticmethod
    def _sort_pipeline_dag(pipeline_dag: list) -> list:
        """
        Sorts a pipeline DAG in order to show dataflow from Pipeline Inputs to Pipeline Outputs.
        Databus component is a privileged source, and it is always the first component in the report.

        Args:
            pipeline_dag (list): The pipeline DAG is a list of dictionaries with "source" and "target" keys.
        Returns:
            A sorted list of dictionaries representing the pipeline DAG.
        """
        pipeline_dag.sort(key=lambda x: (x["source"], x["target"]))

        sorted_dag = [edge for edge in pipeline_dag if "Databus" in edge['source']]
        if sorted_dag == []:
            return pipeline_dag
        
        pipeline_dag = [edge for edge in pipeline_dag if "Databus" not in edge['source']]

        # Extracts name of the target or source component from the edge
        name_of_component = lambda edge, target_or_source: edge[target_or_source].rsplit(".", 1)[0]

        while len(pipeline_dag) > 0:
            sorted_targets = [name_of_component(edge, "target") for edge in sorted_dag]

            sorted_dag.extend([
                edge for edge in pipeline_dag 
                if name_of_component(edge, "source") in sorted_targets
            ])
            
            pipeline_dag = [edge for edge in pipeline_dag if edge not in sorted_dag]

        return sorted_dag

    def _set_pipeline_structure(self):
        self.pipeline_name = self.pipeline_config.get("dataFlowPipelineInfo", {}).get("projectName", "n/a")

        self.pipeline_structure_text = "```plantuml\n"
        components = self.pipeline_config.get("dataFlowPipeline", {}).get("components", [])

        variables = {}  # name: (type, is_metric)
        for component in components:
            input_variables  = {_input["name"]: (_input["type"], False) for _input in component.get("inputType")}
            output_variables = {_output["name"]: (_output["type"], _output.get("metric", False)) for _output in component.get("outputType")}
            variables.update({**input_variables, **output_variables})

        pipeline_dag = self.pipeline_config.get("dataFlowPipeline", {}).get("pipelineDag", [])
        sorted_pipeline_dag = PipelineReportWriter._sort_pipeline_dag(pipeline_dag)

        for transition in sorted_pipeline_dag:
            
            source_component_name, source_variable_name = transition["source"].rsplit(".", 1)            
            target_component_name, target_variable_name = transition["target"].rsplit(".", 1)

            variable_name_to_show = source_variable_name if source_variable_name == target_variable_name else f"{source_variable_name} -> {target_variable_name}"

            source_component_name = source_component_name.replace("Databus", "AIIS")
            target_component_name = target_component_name.replace("Databus", "AIIS")

            variable_type, is_metric = variables[source_variable_name]
            arrow = "-->" if is_metric else "->"  # metric variables are drawn with a dashed line
            self.pipeline_structure_text += PL_STRUCTURE.format(source_component=source_component_name,
                                                                arrow=arrow,
                                                                target_component=target_component_name,
                                                                variable_name=variable_name_to_show,
                                                                variable_type=variable_type)
        self.pipeline_structure_text += "```\n\n"

    def _set_pipeline_info(self):
        dataflow_pipeline_info = self.pipeline_config.get("dataFlowPipelineInfo", {})
        author = dataflow_pipeline_info.get("author", "n/a")
        created_on = dataflow_pipeline_info.get("createdOn", "n/a")
        pipeline_version = dataflow_pipeline_info.get("dataFlowPipelineVersion", "n/a")
        description = dataflow_pipeline_info.get("description", "n/a")
        package_id = dataflow_pipeline_info.get("packageId", "n/a")
        project_name = dataflow_pipeline_info.get("projectName", "n/a")
        self.pipeline_info_text = PL_INFO.format(author=author,
                                                 created_on=created_on,
                                                 pipeline_version=pipeline_version,
                                                 description=description,
                                                 package_id=package_id,
                                                 project_name=project_name)

    # Transform every dependency and package name for consistency; i.e.,
    # opencv-python-headless -> opencv_python_headless; Django -> django
    @staticmethod
    def transform_package_name(name: str):
        new_name = name.replace("-", "_")
        return new_name.lower()

    # A full dependency set is a set of (package_name, package_version) tuples
    # and contains all the dependencies installed for a component
    def add_full_dependency_set(self, component_name: str, dependency_set: set[tuple]):
        dependency_list = sorted(list(dependency_set), key=lambda x: x[0])
        self._expand_component_all_dependencies(component_name, dependency_list)
        self._update_vulnerability_dict(dependency_list)

    def _expand_component_all_dependencies(self, component_name: str, dependency_list: list[tuple]):
        if component_name not in self.component_all_dependencies:
            self.component_all_dependencies[component_name] = set()

        for package_name, package_version in dependency_list:
            transformed_package_name = PipelineReportWriter.transform_package_name(package_name)
            self.component_all_dependencies[component_name].add((transformed_package_name, package_version))

    def _update_vulnerability_dict(self, dependency_list: list[tuple]):
        vulnerability_dict = {}
        for package_name, package_version in dependency_list:
            transformed_package_name = PipelineReportWriter.transform_package_name(package_name)
            vulnerability_dict[(transformed_package_name, package_version)] = None

            url = f"https://pypi.org/pypi/{package_name}/{package_version}/json"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'vulnerabilities' in data:
                        vulnerability_dict[(transformed_package_name, package_version)] = data['vulnerabilities']
            except requests.exceptions.Timeout:
                pass
        self.vulnerability_dict.update(vulnerability_dict)

    def add_direct_dependencies(self, component_name: str, direct_dependencies: dict):
        self.component_direct_dependency_namelist[component_name] = [PipelineReportWriter.transform_package_name(name)
                                                                     for name in list(direct_dependencies.keys())]
    def write_report(self):
        if self.report_path is None:
            return
        self._set_component_dependencies()
        with open(self.report_path, "w") as file:
            self._write_headline(file)
            self._write_pipeline_info(file)
            self._write_pipeline_structure(file)
            self._write_dependencies(file)
            self._write_package_vulnerabilities(file)
            self._write_warnings(file)

    def _set_component_dependencies(self):
        for component in self.component_all_dependencies.keys():
            # self.component_direct_dependencies should contain everything from self.component_all_dependencies
            #   if it is direct, i.e., the name is in self.component_direct_dependency_namelist
            # self.component_transitive_dependencies should contain everything else
            self.component_transitive_dependencies[component] = set()
            self.component_direct_dependencies[component] = set()

            all_dependencies = self.component_all_dependencies[component]
            for dependency_name, dependency_version in all_dependencies:
                if dependency_name in self.component_direct_dependency_namelist.get(component, []):
                    self.component_direct_dependencies[component].add((dependency_name, dependency_version))
                else:
                    self.component_transitive_dependencies[component].add((dependency_name, dependency_version))

    def _write_headline(self, file):
        file.write(PL_REPORT_HEADLINE.format(pipeline_name=self.pipeline_name))

    def _write_pipeline_info(self, file):
        file.write(PL_INFO_HEADLINE)
        file.write(self.pipeline_info_text)

    def _write_pipeline_structure(self, file):
        file.write(PL_STRUCTURE_HEADLINE)
        file.write(self.pipeline_structure_text)

    def _write_dependencies(self, file):
        for component_name in self.component_all_dependencies.keys():
            direct_dependencies = self.component_direct_dependencies.get(component_name, set())
            transitive_dependencies = self.component_transitive_dependencies.get(component_name, set())

            file.write(PL_COMPONMENT_DEPENDENCIES_HEADLINE.format(component_name=component_name))
            file.write(PL_COMPONENT_DIRECT_DEPENDENCIES_HEADLINE)
            sorted_direct_dependencies = sorted(list(direct_dependencies), key=lambda x: x[0])
            for dependency_name, dependency_version in sorted_direct_dependencies:
                file.write(PL_COMPONENT_DIRECT_DEPENDENCY.format(dependency_name=dependency_name,
                                                                 dependency_version=dependency_version))
            file.write("\n")
            file.write(PL_COMPONENT_TRANSITIVE_DEPENDENCIES_HEADLINE)
            sorted_transitive_dependencies = sorted(list(transitive_dependencies), key=lambda x: x[0])
            for dependency_name, dependency_version in sorted_transitive_dependencies:
                file.write(PL_COMPONENT_TRANSITIVE_DEPENDENCY.format(dependency_name=dependency_name,
                                                                     dependency_version=dependency_version))
            file.write("\n")

    def _get_components_who_have_given_package(self, package_name, package_version):
        components = []
        for component in self.component_all_dependencies:
            dependencies = self.component_all_dependencies[component]
            if (package_name, package_version) in dependencies:
                components.append(component)
        return components

    def _write_package_vulnerabilities(self, file):
        file.write(PL_PACKAGE_VULNERABILITIES_HEADLINE)
        sorted_vulnerability_dict_items = sorted(self.vulnerability_dict.items(), key=lambda x: x[0][0])
        for (package_name, package_version), vulnerabilities in sorted_vulnerability_dict_items:
            components = ', '.join(self._get_components_who_have_given_package(package_name, package_version))
            if vulnerabilities is None:
                file.write(PL_PACKAGE_VULNERABILITY_CANNOT_BE_CHECKED.format(package_name=package_name,
                                                                             package_version=package_version,
                                                                             components=components))
            elif vulnerabilities == []:
                file.write(PL_PACKAGE_VULNERABILITY_NOT_KNOWN.format(package_name=package_name,
                                                                     package_version=package_version,
                                                                     components=components))
            else:
                for vulnerability in vulnerabilities:
                    vulnerability_aliases = vulnerability.get('aliases', 'Vulnerability found with no alias. Check [PyPI repository](https://pypi.org/) for more details.')
                    vulnerability_link = vulnerability.get('link', 'No link found')
                    if vulnerability_link != 'No link found':
                        vulnerability_link = f"[{vulnerability_link}]({vulnerability_link})"
                    vulnerability_details = vulnerability.get('details', 'No details found')
                    vulnerability_fixed_in = vulnerability.get('fixed_in', '')
                    file.write(PL_PACKAGE_VULNERABILITY.format(package_name=package_name,
                                                               package_version=package_version,
                                                               vulnerability_aliases=vulnerability_aliases,
                                                               vulnerability_link=vulnerability_link,
                                                               vulnerability_details=vulnerability_details,
                                                               vulnerability_fixed_in=vulnerability_fixed_in,
                                                               components=components))
        file.write("\n")


LPLR_REPORT_HEADLINE = "# Report on Local Pipeline Runner\n\n"

LPLR_FOLDER_STRUCTURE_HEADLINE = """## Folder structure

File sizes represent uncompressed sizes.

"""
LPLR_FOLDER_STRUCTURE = """```
{file_name}
{folder_structure}```

"""
LPLR_FOLDER_STRUCTURE_FOLDER_LINE = "{prefix}{connector}{folder}\n"
LPLR_FOLDER_STRUCTURE_FILE_LINE = "{prefix}{connector}{file} ({size})\n"
LPLR_FOLDER_STRUCTURE_MID_CONNECTOR_SYMBOL = "├── "
LPLR_FOLDER_STRUCTURE_LAST_CONNECTOR_SYMBOL = "└── "
LPLR_FOLDER_STRUCTURE_MID_PREFIX_SYMBOL = "│   "
LPLR_FOLDER_STRUCTURE_LAST_PREFIX_SYMBOL = "    "

LPLR_PYTHON_PACKAGES_ZIP_CONTENT_HEADLINE = "## PythonPackages.zip content\n\n"
LPLR_PYTHON_PACKAGES_ZIP_CONTENT = "- {python_package}\n"

LPLR_COMPONENT_INSTALLED_PACKAGES_HEADLINE = """## Installed packages

Installed packages are listed in the `first report`, when the virtual environment is created for the Local Pipeline Runner. Subsequent reports will result in an empty list.

"""
LPLR_COMPONENT_INSTALLED_PACKAGES = """### Component `{component}`

| Package name | Package version | wheel name |
|--------------|-----------------|------------|
"""
LPLR_COMPONENT_INSTALLED_PACKAGES_ROW = "| {package_name} | {package_version} | {wheel_name} |\n"

LPLR_PAYLOAD_LENGTHS_HEADLINE = "## Payload counts\n\n"
LPLR_PAYLOAD_LENGTHS = """### Component `{component}`

- Input payload count: {input_payload_length}
- Output payload count: {output_payload_length}

"""


class PipelineRunnerReportWriter(ReportWriter):
    """
    PipelineRunnerReportWriter is responsible for generating a detailed report of a local pipeline execution.
    It builds folder structures from zip files, manages component payload counts, and adds installed packages information.

    Methods:
        set_path(report_path: Path):
            Sets the path where the report will be saved.
        set_package_zip_path(zip_path: Path):
            Sets the path to the package zip file and updates the folder tree.
        set_input_payload_length(component_name: str, length: int):
            Sets the input payload length for a component.
        set_output_payload_length(component_name: str, length: int):
            Sets the output payload length for a component.
        add_installed_packages(component_name: str, pip_report_file: Path):
            Adds installed packages for a component from a pip report file.
        add_warning(name, filename, line_number, warning_msg):
            Adds a warning to the report.
        write_report():
            Writes the report to the specified path.
    """
    def __init__(self):
        super().__init__()
        self.package_zip_path = None
        self.zip_file_name = ""

        self.component_installed_packages = {}  # component_name -> list[tuple(package_name, package_version, whl_name)]
        self.component_payload_length = {}  # component_name -> [input_payload_length, output_payload_length]
        self.python_packages_zip_content = set()

        # report text sections to fill
        self.folder_tree_text = ""
        self.warnings_text = ""

    def set_package_zip_path(self, zip_path: Path):
        self.package_zip_path = zip_path

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            self.zip_file_name = zipf.filename
            zip_tree = {}
            for item_name in zipf.namelist():
                zip_tree[item_name] = ZipTreeElement(full_name=item_name, file_size=zipf.getinfo(item_name).file_size)
            self._print_structure_recursively(zip_tree, zipf)

    @staticmethod
    def _get_folder_and_file_list(item_names: list) -> tuple[list, list]:
        """
        Given a list of item names, each item name is a file that either starts with a folder name, or not.
        This function separates the folder names and the standalone file names.
        E.g., ["a/b/something.txt", "c/another.txt", "else.txt"] -> ["a/", "c/"], ["else.txt"]
        """
        folder_names = set()
        file_names = []
        for item in item_names:
            item_parts = item.split('/')
            if len(item_parts) > 1:
                if item_parts[0] != '':
                    folder_names.add(item_parts[0] + '/')
            else:
                if item != '':
                    file_names.append(item)
        return sorted(list(folder_names)), sorted(file_names)
    
    @staticmethod
    def format_size(size):
        """Format file size in human-readable form."""
        for unit in ['B', 'KB', 'MB']:
            if size < 1000:
                return f"{size} {unit}"
            size //= 1000
        return f"{size} GB"

    def _print_structure_recursively(self, zip_tree, zipf, prefix=""):
        folder_names, file_names = PipelineRunnerReportWriter._get_folder_and_file_list(zip_tree.keys())
        is_file_names_empty = file_names == []
        self._print_folder_structure(zip_tree, zipf, prefix, folder_names, is_file_names_empty)
        self._print_file_structure(zip_tree, zipf, prefix, file_names)

    def _print_folder_structure(self, zip_tree, zipf, prefix, folder_names, is_file_names_empty):
        for i, folder in enumerate(folder_names):
            is_last = (i == len(folder_names) - 1) and is_file_names_empty
            connector = LPLR_FOLDER_STRUCTURE_LAST_CONNECTOR_SYMBOL if is_last else LPLR_FOLDER_STRUCTURE_MID_CONNECTOR_SYMBOL
            self.folder_tree_text += LPLR_FOLDER_STRUCTURE_FOLDER_LINE.format(prefix=prefix,
                                                                              connector=connector,
                                                                              folder=folder)
            # create a new tree where items start with the same folder name; but cut out the folder name
            # (going deeper in the recursion)
            new_zip_tree_from_folder = {}
            for k, v in zip_tree.items():
                if k.startswith(folder):
                    new_file_name = k.split('/', 1)[1]
                    new_zip_tree_from_folder[new_file_name] = v
            prefix_post = LPLR_FOLDER_STRUCTURE_LAST_PREFIX_SYMBOL if is_last else LPLR_FOLDER_STRUCTURE_MID_PREFIX_SYMBOL
            new_prefix_from_folder = prefix + prefix_post
            self._print_structure_recursively(new_zip_tree_from_folder, zipf, new_prefix_from_folder)

    def _print_file_structure(self, zip_tree, zipf, prefix, file_names):
        for i, file_name in enumerate(file_names):
            is_last = (i == len(file_names) - 1)
            size_str = PipelineRunnerReportWriter.format_size(zip_tree[file_name].file_size)
            connector = LPLR_FOLDER_STRUCTURE_LAST_CONNECTOR_SYMBOL if is_last else LPLR_FOLDER_STRUCTURE_MID_CONNECTOR_SYMBOL
            self.folder_tree_text += LPLR_FOLDER_STRUCTURE_FILE_LINE.format(prefix=prefix,
                                                                            connector=connector,
                                                                            file=file_name,
                                                                            size=size_str)
            # zip files are handled similarly to folders:
            # create a new tree where items start with the same folder name; but cut out the folder name
            # (going deeper in the recursion)
            if not file_name.endswith('.zip'):
                continue
            full_name = zip_tree[file_name].full_name
            with zipf.open(full_name) as nested_zip_file:
                nested_zip_data = io.BytesIO(nested_zip_file.read())
                with zipfile.ZipFile(nested_zip_data, 'r') as nested_zipf:
                    if file_name == "PythonPackages.zip":
                        self.python_packages_zip_content.update(sorted(list(nested_zipf.namelist())))
                    # create a new tree where items start with the same folder name; but cut out the folder name
                    new_zip_tree_from_zip = {}
                    for nested_item_name in nested_zipf.namelist():
                        new_zip_tree_from_zip[nested_item_name] = ZipTreeElement(nested_item_name,
                                                                                 nested_zipf.getinfo(nested_item_name).file_size)
                    prefix_post = LPLR_FOLDER_STRUCTURE_LAST_PREFIX_SYMBOL if is_last else LPLR_FOLDER_STRUCTURE_MID_PREFIX_SYMBOL
                    new_prefix_from_zip = prefix + prefix_post
                    self._print_structure_recursively(new_zip_tree_from_zip, nested_zipf, new_prefix_from_zip)

    def set_input_payload_length(self, component_name: str, length: int):
        if component_name in self.component_payload_length:
            self.component_payload_length[component_name][0] = length
        else:
            self.component_payload_length[component_name] = [length, 0]

    def set_output_payload_length(self, component_name: str, length: int):
        if component_name in self.component_payload_length:
            self.component_payload_length[component_name][1] = length
        else:
            self.component_payload_length[component_name] = [0, length]

    def add_installed_packages(self, component_name: str, pip_report_file: Path):
        pip_report = {}
        with open(pip_report_file, 'r') as file:
            pip_report = json.load(file)

        if component_name not in self.component_installed_packages:
            self.component_installed_packages[component_name] = []

        installed_packages = pip_report.get("install", [])
        for package in installed_packages:
            package_url = package.get("download_info", {}).get("url", "")
            wheel_name = package_url.split("/")[-1] if package_url.endswith(".whl") else "n/a"
            metadata = package.get("metadata", {})
            package_name = metadata.get("name", "n/a")
            package_version = metadata.get("version", "n/a")
            self.component_installed_packages[component_name].append((package_name, package_version, wheel_name))

    # check if one or more reports already exists; set the report path so a new report will have a new index
    def _set_path_from_zip_path(self):
        if self.package_zip_path is None:
            return
        workdir = self.package_zip_path.parent
        base_name = self.package_zip_path.stem
        report_files = list(workdir.glob(f"{base_name}_execution_report_*.md"))
        max_index = 0
        for report_file in report_files:
            try:
                index = int(report_file.stem.split('_')[-1])
                if index > max_index:
                    max_index = index
            except ValueError:
                continue
        self.set_path(workdir / f"{base_name}_execution_report_{max_index + 1}.md")

    def write_report(self):
        # if the report path is not set, set it from the zip path
        self._set_path_from_zip_path()
        if self.report_path is None:
            return

        with open(self.report_path, "w") as file:
            self._write_headline(file)
            self._write_folder_structure(file)
            self._write_python_packages_zip_content(file)
            self._write_component_installed_packages(file)
            self._write_payload_lengths(file)
            self._write_warnings(file)

    def _write_headline(self, file):
        file.write(LPLR_REPORT_HEADLINE)

    def _write_folder_structure(self, file):
        file.write(LPLR_FOLDER_STRUCTURE_HEADLINE.format(file_name=self.zip_file_name))
        file.write(LPLR_FOLDER_STRUCTURE.format(file_name=self.zip_file_name, folder_structure=self.folder_tree_text))

    def _write_python_packages_zip_content(self, file):
        file.write(LPLR_PYTHON_PACKAGES_ZIP_CONTENT_HEADLINE)
        sorted_zip_content = sorted(list(self.python_packages_zip_content))
        for package in sorted_zip_content:
            file.write(LPLR_PYTHON_PACKAGES_ZIP_CONTENT.format(python_package=package))
        file.write("\n")        

    def _write_component_installed_packages(self, file):
        file.write(LPLR_COMPONENT_INSTALLED_PACKAGES_HEADLINE)
        for component in self.component_installed_packages:
            file.write(LPLR_COMPONENT_INSTALLED_PACKAGES.format(component=component))
            sorted_installed_packages = sorted(self.component_installed_packages[component], key=lambda x: x[0])
            for package_name, package_version, wheel_name in sorted_installed_packages:
                file.write(LPLR_COMPONENT_INSTALLED_PACKAGES_ROW.format(package_name=package_name,
                                                                        package_version=package_version,
                                                                        wheel_name=wheel_name))
            file.write("\n")

    def _write_payload_lengths(self, file):
        file.write(LPLR_PAYLOAD_LENGTHS_HEADLINE)
        for component in self.component_payload_length:
            input_payload_length, output_payload_length = self.component_payload_length[component]
            file.write(LPLR_PAYLOAD_LENGTHS.format(component=component,
                                                   input_payload_length=input_payload_length,
                                                   output_payload_length=output_payload_length))
