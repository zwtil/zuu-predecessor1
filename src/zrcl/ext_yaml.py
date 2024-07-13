import copy
from functools import cache
from types import MappingProxyType
import typing
import yaml

class _VAL_marker:
    def __init__(self, val):
        self.val = val

    def __hash__(self):
        return hash(f"marker({self.val})")

FYVAL = _VAL_marker

class FloYaml:
    VAL = _VAL_marker

    """
    a yaml parser that supports a superset of the yaml spec

    two features added:
    - support concatenation of keys
    - support adding values even if the structure has nested values
    
    example:
    ```yaml
    val1: 1
    val2: 2
        val3: 3
        val3: 4
            val5: 5
    ```
    will be parsed as
    ```json
    {
        "val1": 1,
        "val2" : {
            "__val__" : 2,
            "val3": [
                { "__val__": 3 },
                { "__val__": 4 , "val5": 5 },
            ]
        }
    }
    ```
            
    """

    @classmethod
    def __calc_indent_length(cls, lines: typing.List[str]):
        for line in lines:
            if len(line) == len(line.lstrip()):
                continue

            return len(line) - len(line.lstrip())

    @classmethod
    def __line_parse(cls, line: str, indentLength: int):
        indentLv = (len(line) - len(line.lstrip())) // indentLength

        if ":" not in line:
            return False, indentLv, None, None

        key, value = line.split(":", 1)

        return True, indentLv, key.strip(), value.strip()

    @classmethod
    def process(cls, string: str):
        lines = string.split("\n")
        indent_length = cls.__calc_indent_length(lines)
        processed_lines = []
        key_counts = {}  # Dictionary to track key occurrences globally
        key_registry = {}  # Registry for tracking duplicates by numerical ID
        registry_index = 0  # Unique numerical ID for each duplicate key

        paths = [
            []
            for _ in range(
                max(
                    (len(line) - len(line.lstrip(" "))) // indent_length
                    for line in lines
                    if line.strip()
                )
                + 1
            )
        ]  # Path stack for each indentation level

        for i in range(len(lines)):
            line = lines[i]
            if not line.strip():
                continue

            is_valid, indent_level, key, value = cls.__line_parse(line, indent_length)
            if not is_valid:
                continue

            # Update the current path at the current indentation level
            paths[indent_level] = [key]  # Reset the path at this level with the new key
            full_path = ".".join(
                sum(paths[: indent_level + 1], [])
            )  # Flatten and join to form the full path

            # Check and update global counts for the full path
            if full_path not in key_counts:
                key_counts[full_path] = 0
            else:
                key_counts[full_path] += 1
                # Add to registry if it's a duplicate
                modified_key = f"floyaml_{registry_index}"
                key_registry[registry_index] = full_path
                registry_index += 1
                # Replace the current key with the modified key in the path
                paths[indent_level][-1] = modified_key  # Update the current path entry
                key = modified_key

            # Look ahead to determine if the current line has children
            has_children = False
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if (
                    next_line.strip()
                    and ((len(next_line) - len(next_line.lstrip(" "))) // indent_length)
                    > indent_level
                ):
                    has_children = True

            # Construct the new line with appropriate indentation and modified key
            if has_children:
                newline = f"{key}:"
                processed_lines.append(
                    f"{' ' * (indent_level - 1) * indent_length}{newline}"
                )
                processed_lines.append(
                    f"{' ' * indent_level * indent_length}__val__: {value.strip()}"
                )
            else:
                newline = f"{key}: {value.strip()}" if value.strip() else f"{key}:"
                processed_lines.append(
                    f"{' ' * (indent_level - 1) * indent_length}{newline}"
                )

        return processed_lines, key_registry

    def pack(yaml_dict, key_registry):
        # Reverse the key_registry to get paths to indices
        path_to_indices = {}
        for index, path in key_registry.items():
            base_path, _, key = path.rpartition(".")
            if base_path not in path_to_indices:
                path_to_indices[base_path] = {}
            if key not in path_to_indices[base_path]:
                path_to_indices[base_path][key] = []
            path_to_indices[base_path][key].append(f"floyaml_{index}")

        def merge_dicts(dicts):
            """Merge multiple dictionaries, aggregating list values for common keys."""
            merged = {}
            for d in dicts:
                for k, v in d.items():
                    if k in merged:
                        if not isinstance(merged[k], list):
                            merged[k] = [merged[k]]
                        merged[k].append(v)
                    else:
                        merged[k] = v
            return merged

        # Navigate the dictionary and adjust according to registry
        for path, keys in reversed(path_to_indices.items()):
            path_parts = path.split(".")
            sub_dict = yaml_dict
            # Navigate to the correct sub-dictionary
            for part in path_parts:
                sub_dict = sub_dict.get(part, {})

            # Process each key that has duplicates
            for key, indices in keys.items():
                original_value = sub_dict.pop(key, None)
                # Gather all versions of the key, including the original
                values = [original_value] if original_value is not None else []
                for index in indices:
                    if index in sub_dict:
                        values.append(sub_dict.pop(index))

                # Merge dictionaries if necessary, or just form a list
                if all(isinstance(v, dict) for v in values):
                    sub_dict[key] = [merge_dicts(values)]
                else:
                    sub_dict[key] = values

        return yaml_dict

    @classmethod
    def load(cls, string: str, just_dict: bool = False):
        lines, key_registry = cls.process(string)
        loaded = yaml.safe_load("\n".join(lines))

        datadict = cls.pack(loaded, key_registry)
        if just_dict:
            return datadict
        else:
            return cls(datadict)

    def __init__(self, datadict: dict):
        self.__datadict = datadict


    @classmethod
    def __locate(cls, data, keys):
        """
        able to retrieve keys using following methods

        data["key1", "key2", "key3"] => data["key1"]["key2"]["key3"]
        data["key1", "key2[1]", "key3[2]"] => data["key1"]["key2"][1]["key3"][2]
        data["key1", "key2[1]", VAL("key3")] => data["key1"]["key2"][1]["key3"]; parsed a list of all values or just 1
        data["key1", "key2[1]", VAL("key3[2]")] => data["key1"]["key2"][1]["key3"][2]["__val__"]
        """
        current = data
        for key in keys:
            if isinstance(key, str):
                if '[' in key and ']' in key:
                    key, index = key.split('[')
                    index = int(index.rstrip(']'))
                    current = current[key][index]
                else:
                    current = current[key]
            elif isinstance(key, cls.VAL):
                key_val = key.val
                if '[' in key_val and ']' in key_val:
                    key_val, index = key_val.split('[')
                    index = int(index.rstrip(']'))
                    current = current[key_val][index]
                    if isinstance(current, dict) and '__val__' in current:
                        current = current['__val__']
                else:
                    current = current[key_val]
                    # Check if the current is iterable and only then iterate over it
                    if isinstance(current, list):
                        current = [item['__val__'] if isinstance(item, dict) and '__val__' in item else item for item in current]
                    else:
                        # Return the current item directly if it's not a list
                        return current
            else:
                raise TypeError(f"Unsupported key type: {type(key)}")
        return current
    
    @classmethod
    def __setval(cls, data, keys, value):
        """Set a value at a specific location in a nested data structure."""
        target = cls.__locate(data, keys[:-1])  # Get the target dictionary/list where the value needs to be set.
        final_key = keys[-1]

        if isinstance(final_key, cls.VAL):
            key_parts = final_key.val.split('[')
            base_key = key_parts[0]
            if len(key_parts) > 1:
                # Handle indexed access in VAL
                index = int(key_parts[1].strip('[]'))
                if isinstance(target[base_key], list) and len(target[base_key]) > index:
                    if isinstance(target[base_key][index], dict):
                        if '__val__' in target[base_key][index]:
                            target[base_key][index]['__val__'] = value
                        else:
                            target[base_key][index] = value  # Directly set value if '__val__' not applicable
                    else:
                        # If it's not a dict, set the value directly
                        target[base_key][index] = value
                else:
                    raise IndexError("List index out of range")
            else:
                # No index provided in VAL, set directly or to '__val__' if it's a dictionary
                if isinstance(target[base_key], dict):
                    if '__val__' in target[base_key]:
                        target[base_key]['__val__'] = value
                    else:
                        target[base_key] = value  # Replace the dictionary if '__val__' not applicable
                else:
                    target[base_key] = value  # Set value directly if not a dictionary
        else:
            # Standard string key, just set the value
            if isinstance(target[final_key], dict) and '__val__' in target[final_key]:
                target[final_key]['__val__'] = value
            else:
                target[final_key] = value


    @cache
    def __getitem__(self, key):
        return self.__locate(self.__datadict, key)

    @cache
    def __setitem__(self, key, value):
        self.__setval(self.__datadict, key, value)

    @property
    def copiedDict(self):
        return copy.deepcopy(self.__datadict)

    @property
    def datadict(self):
        return MappingProxyType(self.__datadict)

    @classmethod
    def dumps(cls, data):
        """
        dumps data into yaml-like format

        does not gurantee the same order of keys
        """

        if type(data) == cls:
            data = data.__datadict

        def recurse(obj, level=0):
            entries = []
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key == '__val__':
                        # Handle inline values for '__val__' specially
                        entries.append(' ' * 4 * level + str(val))
                    else:
                        nested = recurse(val, level + 1)
                        if isinstance(val, list):
                            # Duplicate the key for each item in the list
                            for list_item in val:
                                list_entry = recurse(list_item, level + 1)
                                entries.append(' ' * 4 * level + f"{key}:\n{list_entry}")
                        else:
                            # Standard dict handling
                            entries.append(' ' * 4 * level + f"{key}:\n{nested}")
            elif isinstance(obj, list):
                # List items are handled individually and may contain nested dictionaries
                list_entries = []
                for item in obj:
                    formatted_item = recurse(item, level + 1)
                    list_entries.append(formatted_item)
                return "\n".join(list_entries)
            else:
                # Plain values are returned directly without newlines
                return str(obj)
            
            return "\n".join(entries)

        # Start recursion from the root level (0)
        recursed =  recurse(data)
        recursed = recursed.split("\n")
        ret = []

        curr = ""
        for i in range(len(recursed)):    
            curl = recursed[i]
            if curl.endswith(":"):
                curr = curl
            elif curr and ":" not in curl:
                ret.append(f"{curr} {curl}")
                curr = ""
            else:
                ret.append(curl)
        
        return "\n".join(ret)
            
    