import os
import re
import pyperclip
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
import argparse

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def find_dependencies(file_path):
    """Find all dependencies (.py and .yaml files) in the given file."""
    dependencies = set()
    with open(file_path, 'r') as file:
        content = file.read()
        # Find all import statements
        imports = re.findall(r'import (\S+)', content)
        from_imports = re.findall(r'from (\S+) import', content)
        # Find all YAML file references
        yaml_files = re.findall(r'[\'"](.+\.yaml)[\'"]', content)
        dependencies.update(imports)
        dependencies.update(from_imports)
        dependencies.update(yaml_files)
    return dependencies

def get_all_dependencies(file_path, visited=None):
    """Recursively find all dependencies for the given file."""
    if visited is None:
        visited = set()
    visited.add(file_path)
    dependencies = find_dependencies(file_path)
    all_dependencies = set()
    for dep in dependencies:
        if dep.endswith('.py') or dep.endswith('.yaml'):
            dep_path = os.path.join(os.path.dirname(file_path), dep)
            if os.path.exists(dep_path) and dep_path not in visited:
                all_dependencies.add(dep_path)
                all_dependencies.update(get_all_dependencies(dep_path, visited))
    return all_dependencies

def concatenate_files(file_paths):
    """Concatenate the contents of the given files."""
    documents_elem = Element('documents')
    for index, file_path in enumerate(file_paths, start=1):
        document_elem = SubElement(documents_elem, 'document', index=str(index))
        source_elem = SubElement(document_elem, 'source')
        source_elem.text = file_path
        document_content_elem = SubElement(document_elem, 'document_content')
        with open(file_path, 'r') as file:
            document_content_elem.text = file.read()
    return prettify(documents_elem)

def main(input_path):
    dependencies = get_all_dependencies(input_path)
    all_files = [input_path] + list(dependencies)
    concatenated_content = concatenate_files(all_files)
    pyperclip.copy(concatenated_content)
    print("Concatenated content copied to clipboard.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate Python and YAML files and their dependencies into an XML format.")
    parser.add_argument('file_path', type=str, help='The path to the main Python script')
    args = parser.parse_args()
    main(args.file_path)


# Copyright 2024 Scott Macdonell

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.