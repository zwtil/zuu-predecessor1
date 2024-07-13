from functools import cache, cached_property
import os
from types import MappingProxyType
import typing
import yaml

_global_counter = 0

class _FloYaml__Val:
    def __init__(self, key):
        self.key = key

    def __getitem__(self, val):
        return self.__class__(val)
    
    def __call__(self, val):
        return self.__class__(val)

VAL = _FloYaml__Val('')

class FloYaml:
    VAL = VAL

    @classmethod
    def __global_counter(cls):
        global _global_counter
        _global_counter += 1
        return _global_counter

    @cached_property
    def __baseindent(self):
        for line in self.__rawstr.split('\n'):
            if len(line) == len(line.lstrip()):
                continue

            return len(line) - len(line.lstrip())

    def __init__(self, data : str):
        if "_floyaml_" in data:
            raise ValueError("_floyaml_ is reserved for internal use")

        self.__rawstr = data
        
        parsed_block = self.__process(data)
        self.__lines = self.__partition(parsed_block)
        formatted = [i * 4 * " " + line for i, line in self.__lines]
        self.__datadict = yaml.safe_load("\n".join(formatted))

    def __process(self, raw_string: str):
        """
        Process a raw string and format its lines to extract indentation and strip unnecessary whitespaces.

        Args:
            raw_string (str): The raw string to be processed.

        Returns:
            List[Tuple[int, str]]: A list of tuples containing the indentation level and the formatted line.

        This function takes a raw string as input and splits it into lines. It then parses the lines to extract the indentation level and strip unnecessary whitespaces. It iterates over each line and checks if it contains a colon. If it does not, the line is appended as is to the formatted_lines list. Otherwise, it splits the line at the colon and strips any leading or trailing whitespaces from the key and value. It checks if the line has children by checking if the next line has a higher indentation level. If it does and the value is not empty, it adds the key and a placeholder line for the value to the formatted_lines list. Otherwise, it adds the line as is to the formatted_lines list. Finally, it returns the formatted_lines list.
        """
        lines = raw_string.split('\n')

        formatted_lines = []
        
        # Parse lines to extract indentation and strip unnecessary whitespaces
        base_extracted = [((len(line) - len(line.lstrip())) // self.__baseindent, line.strip()) for line in lines if line.strip()]

        for i in range(len(base_extracted)):
            indent, line = base_extracted[i]
            
            if ':' not in line:
                formatted_lines.append((indent, line))

            key, val = line.split(':', 1)
            key = key.strip()

            val = val.strip()
            
            # Check for children to determine whether to add __val__ line
            has_children = (i + 1 < len(base_extracted)) and (base_extracted[i + 1][0] > indent)
            if has_children and val:
                formatted_lines.append((indent, key + ':'))
                formatted_lines.append((indent + 1, '__val__ : ' + val))
            else:
                formatted_lines.append((indent, line))

        return formatted_lines

    def __partition(self, lines : list):
        """
        given lines are (indent, line) tuples
        
        ```
        a : 
            b :
                c : 
                    e : f
                d : 3
                c : 3
        a : 2
        a : 
            a : 4
            b : 5
            c : 6 
        c : 3
        ```
        as 
        [
            (0, 'a : '), 
            (1, 'b : '), # a  
            (2, 'c : '), # a.b
            (3, 'e : f'),# a.b.c
            (2, 'd : 3'),# a.b
            (2, 'c : 3'),# a.b
            (0, 'a : 2'),# <rename a> 
            (0, 'a : '), # ""
            (1, 'a : 4'),# a
            (1, 'b : 5'),# a
            (1, 'c : 6'),# a
            (0, 'c : 3'),# a
        ]

        any key that repeats in the same scope, will be renamed to a unique key (using uuid)
        then its path will be saved in an registry
    
        """
        stack = []  # Stack to maintain current scope and path
        path_registry = {}  # Registry to store paths and track all keys
        output = []  # Output list with possibly renamed lines

        for indent, line in lines:
            # Get the current key (ignore values for now)
            key = line.split(':')[0].strip() if ':' in line else line.strip()

            # Manage the stack based on current indentation
            while stack and stack[-1][0] >= indent:
                stack.pop()

            # Create a unique path for the current line
            current_path = '.'.join([s[1] for s in stack] + [key]) if stack else key
            
            # Check for duplicate keys in the same scope
            if current_path in path_registry:
                
                unique_key = f"{key}_floyaml_{FloYaml.__global_counter()}"
                new_line = line.replace(key, unique_key)
                output.append((indent, new_line))
                # Update path registry to include the new unique key under the same path
                path_registry[current_path].append(unique_key)
                # Update the stack with the new unique key instead of the original key
                stack.append((indent, unique_key))
            else:
                output.append((indent, line))
                # Initialize the path entry with the original key
                path_registry[current_path] = [key]
                stack.append((indent, key))

        return output

    # ANCHOR
    def __single_locate(self, data, key: str):
        index = None
        if '[' in key and ']' in key:
            key, index = key.split('[')
            index = int(index.rstrip(']'))
        
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
        
        if not any("_floyaml_" in k for k in data.keys()):
            return data.get(key)

        if index is None:
            ret = []
            for k, v in data.items():
                if k.startswith(f"{key}_floyaml_") or k == key:
                    ret.append(v)
            return ret
       
        counter = 0
        for k, v in data.items():
            if k.startswith(f"{key}_floyaml_") or k == key:
                if index == counter:
                    return v
                counter += 1

    
    def locate(self, keys):
        """
        get a value based on a sequence of keys
    
        a,b,c               => data[a][b][c]
        a[1], b[2], c[3]    => data[a][1][b][2][c][3]
        VAL['a'] (dict)     => get all __val__ of type a
        VAL['a[1]']         => get the 2nd __val__ of type a
        """
        current = self.__datadict
        for key in keys:
            if not isinstance(key, _FloYaml__Val):
                current = self.__single_locate(current, key)
                continue
            
            current = self.__single_locate(current, key.key)
            if isinstance(current, list):
                current = [i['__val__'] if isinstance(i, dict) else i for i in current]
            elif isinstance(current, dict) and '__val__' in current:
                current = current['__val__']
                
        return current

    def setval(self, keys, value):
        if not keys:
            raise ValueError("Keys list is empty, no location specified to set the value.")

        path_to_last_key = keys[:-1]
        last_key = keys[-1]

        if isinstance(last_key, _FloYaml__Val):
            last_key = last_key.key
            is_valed = True
        else:
            is_valed = False

        key, index = last_key.split('[')
        if index:
            index = int(index.rstrip(']'))

        container = self.locate(path_to_last_key)
        
        if index is None:
            index = 0 

        counter = 0
        for k, v in container.items():
            if k == key or k.startswith(f"{key}_floyaml_") and counter == index:
                if is_valed and isinstance(v, dict) and "__val__" in v:
                    v["__val__"] = value
                else:
                    container[k] = value
                break

            counter += 1


    #ANCHOR

    def __setitem__(self, key, value):
        self.setval(key, value)

    def __getitem__(self, key):
        return self.locate(key)
    
    # ANCHOR
    @classmethod
    def load(cls, data : typing.Union[str, typing.IO]):
        if isinstance(data, str) and os.path.isfile(data):
            with open(data, 'r') as f:
                data = f.read()
        elif isinstance(data, str):
            pass
        elif isinstance(data, typing.IO):
            data = data.read()
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        return cls(data)
    

    @classmethod
    def open(cls, path : str):
        with open(path, 'r') as f:
            data = f.read()

        return cls(data)

    def dumps(self):
        """
        Dumps data into a YAML-like format, stripping away any keys that have been
        renamed with the '_floyaml_' pattern to maintain clear and standard output.
        """

        def recurse(obj, level=0):
            entries = []
            indent = ' ' * self.__baseindent * level

            if isinstance(obj, dict):
                for key, val in obj.items():
                    # Normalize key by removing any '_floyaml_' patterns
                    normalized_key = key.split('_floyaml_')[0]

                    if isinstance(val, dict):
                        entries.append(f"{indent}{normalized_key}:")
                        entries.extend(recurse(val, level + 1))
                    elif isinstance(val, list):
                        entries.append(f"{indent}{normalized_key}:")
                        for item in val:
                            entry = recurse(item, level + 1)
                            # List items prefixed with a dash
                            prefixed_entry = "\n".join(f"{indent + ' ' * self.__baseindent}- {line}" for line in entry.split('\n'))
                            entries.append(prefixed_entry)
                    else:
                        # Handle simple values directly
                        entries.append(f"{indent}{normalized_key}: {val}")
            elif isinstance(obj, list):
                for item in obj:
                    # Handle lists at the top level specially (unlikely but included for completeness)
                    entries.append(f"{indent}- {recurse(item, level + 1)}")
            else:
                # Simple values without key
                return f"{indent}{obj}"

            return "\n".join(entries)

        return recurse(self.__datadict)

    #ANCHOR
    @property
    def datadict(self):
        return MappingProxyType(self.__datadict)