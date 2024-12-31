# A Python script that concatinates your Python source files and copies them to the
# clipboard. It recursively parses your main script and any dependencies to 
# only include files actually required to run your program. 

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
    pretty_xml = reparsed.toprettyxml(indent="\t")
    # Fix document_content closing tag indentation
    return re.sub(r'\t\t\t</document_content>', '\t\t</document_content>', pretty_xml)

def find_dependencies(file_path, project_root=None):
    """Find all dependencies (.py and .yaml files) in the given file."""
    dependencies = set()
    base_dir = os.path.dirname(file_path)
    if project_root is None:
        project_root = base_dir
    
    with open(file_path, 'r') as file:
        content = file.read()
        
        # Find all import statements
        imports = re.findall(r'import\s+([\w.]+)(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*', content)
        # Handle both absolute and relative imports
        from_imports = re.findall(r'from\s+(\.{0,2}[\w.]*)\s+import', content)
        
        # Find all YAML file references
        yaml_files = re.findall(r'[\'"](.+\.yaml)[\'"]', content)
        
        # Process imports and from_imports
        all_imports = []
        for imp in imports:
            all_imports.extend(imp.split(','))
        
        for imp in from_imports:
            imp = imp.strip()
            if imp.startswith('.'):
                # Handle relative imports
                dots = len(re.match(r'\.+', imp).group())
                module_parts = imp[dots:].split('.')
                current_path = os.path.dirname(file_path)
                # Go up directories based on number of dots
                for _ in range(dots - 1):
                    current_path = os.path.dirname(current_path)
                if module_parts[0]:  # If there's a module path after the dots
                    module_path = os.path.join(current_path, *module_parts)
                else:
                    module_path = current_path
            else:
                all_imports.append(imp)
                module_path = imp.replace('.', os.sep)
            
            if isinstance(module_path, str) and not imp.startswith('.'):
                # For absolute imports
                possible_paths = [
                    # Current directory
                    os.path.join(base_dir, module_path + '.py'),
                    os.path.join(base_dir, module_path, '__init__.py'),
                    # Project root directory
                    os.path.join(project_root, module_path + '.py'),
                    os.path.join(project_root, module_path, '__init__.py'),
                    # One directory up from current
                    os.path.join(base_dir, '..', module_path + '.py'),
                    os.path.join(base_dir, '..', module_path, '__init__.py'),
                    # Relative to project root with proper package structure
                    os.path.join(project_root, *module_path.split(os.sep) + ['.py']),
                    os.path.join(project_root, *module_path.split(os.sep), '__init__.py')
                ]
            else:
                # For relative imports where module_path is already resolved
                possible_paths = [
                    module_path + '.py',
                    os.path.join(module_path, '__init__.py')
                ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    dependencies.add(os.path.normpath(path))
                    break
        
        # Process YAML files
        for yaml_file in yaml_files:
            yaml_path = os.path.join(base_dir, yaml_file)
            if os.path.exists(yaml_path):
                dependencies.add(os.path.normpath(yaml_path))
    
    return dependencies

def get_all_dependencies(file_path, project_root=None, visited=None):
    """Recursively find all dependencies for the given file."""
    if visited is None:
        visited = set()
    
    norm_file_path = os.path.normpath(file_path)
    if norm_file_path in visited:
        return set()
        
    visited.add(norm_file_path)
    dependencies = find_dependencies(norm_file_path, project_root)
    all_dependencies = set()
    
    for dep_path in dependencies:
        if dep_path not in visited:
            all_dependencies.add(dep_path)
            all_dependencies.update(get_all_dependencies(dep_path, project_root, visited))
    
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
            content = file.read()
            lines = content.split('\n')
            # Add three tabs to each line except the last one
            indented_lines = ['\t\t\t' + line for line in lines[:-1]]
            # Handle the last line specially to avoid extra newline
            if lines:
                indented_lines.append('\t\t\t' + lines[-1])
            document_content_elem.text = '\n' + '\n'.join(indented_lines)
    return prettify(documents_elem)

def main(input_path, project_root=None):
    if project_root is None:
        project_root = os.path.dirname(input_path)
    dependencies = get_all_dependencies(input_path, project_root)
    all_files = [input_path] + list(dependencies)
    concatenated_content = concatenate_files(all_files)
    pyperclip.copy(concatenated_content)
    print("Concatenated content copied to clipboard.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate Python and YAML files and their dependencies into an XML format.")
    parser.add_argument('file_path', type=str, help='The path to the main Python script')
    parser.add_argument('--project-root', type=str, help='The root directory of the project (defaults to the directory containing file_path)')
    args = parser.parse_args()
    main(args.file_path, args.project_root)


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
