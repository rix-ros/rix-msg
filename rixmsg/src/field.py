from type_regex import (
    is_static_array,
    is_dynamic_array,
    is_map,
    get_value_type,
    get_key_type,
    is_base_type,
    get_static_array_size,
)


class Field:
    def __init__(self, name: str, type_str: str, package: str | None = None):
        self.name = name
        self.type_str = type_str
        self.package = package

        value_type = get_value_type(type_str)
        if value_type is not None:
            self.value_type = value_type
        else:
            self.value_type = str()
            raise ValueError(f"Error: Invalid type {type_str} for field {name}")
        
        self.is_dynamic_array = is_dynamic_array(type_str)
        self.is_static_array = is_static_array(type_str)
        self.is_map = is_map(type_str)

        self.value_is_base = is_base_type(self.value_type)
        
        if self.is_static_array:
            static_array_size = get_static_array_size(type_str)
            if static_array_size is not None:
                self.static_array_size = static_array_size
            else:
                raise ValueError(f"Error: Invalid static array size in type {type_str} for field {name}")

        if self.is_map:
            key_type = get_key_type(type_str)
            if key_type is not None:
                self.key_type = key_type
                self.key_is_base = is_base_type(self.key_type)
            else:
                raise ValueError(f"Error: Invalid key type in type {type_str} for field {name}")
            

        if self.is_map and not self.key_is_base:
            raise ValueError(
                f"Error: Value type for associative container cannot be custom type {self.value_type}"
            )
