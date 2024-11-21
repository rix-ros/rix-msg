import os
from common import types

format_chars = {"char": "c", "int8_t": "b", "int16_t": "h", "int32_t": "i", "int64_t": "q", "uint8_t": "B", "uint16_t": "H", "uint32_t": "I", "uint64_t": "Q", "float": "f", "double": "d", "bool": "?" }

def generate_js(dir, msgs):
    if dir[-1] != '/':
        dir += '/'

    with open(dir + 'package.json', 'w') as file:
        file.write('{\n')
        file.write(f'    "name": "rix-msg",\n')
        file.write(f'    "version": "1.0.0",\n')
        file.write(f'    "description": "Message definitions for RIX",\n')
        file.write(f'    "main": "index.js",\n')
        file.write(f'    "scripts": {{\n')
        file.write(f'        "test": "echo \\"Error: no test specified\\" && exit 1"\n')
        file.write(f'    }},\n')
        file.write(f'    "author": "",\n')
        file.write(f'    "license": "ISC",\n')
        file.write(f'    "dependencies": {{\n')
        file.write(f'        "rix-structjs": "^1.0.0"\n')
        file.write(f'    }},\n')
        file.write(f'    "type": "module"\n')
        file.write('}\n')

    for package in msgs:
        newDir = dir + package + '/'
        os.makedirs(newDir, exist_ok=True)
        
        with open(newDir + 'index.js', 'w') as file:
            for msg in msgs[package]:
                message_name = msg[0]
                template = msg[2]
                if template:
                    message_name += 'Template'
                file.write(f'export {{ {message_name} }} from \'./{message_name}.js\';\n')

        for msg in msgs[package]:
            message_name = msg[0]
            fields = msg[1]
            template = msg[2]
            hashValue = msg[3]
            filename = newDir + message_name + '.js'

            with open(filename, 'w') as file:
                file.write(f'import {{ Structure }} from \'rix-structjs\';\n')

                include_set = set()
                for field in fields:
                    fieldType = field[0]
                    if "::" in fieldType:
                        other_package, field_type = fieldType.split("::")
                        include_file = field_type
                        if include_file not in include_set:
                            include_set.add(include_file)
                            file.write(f'import {{ {field_type} }} from \'../{other_package}/{include_file}.js\';\n')
                    elif fieldType not in types:
                            raise Exception(f"Unknown type {fieldType}")
                
                spacing = ""
                if template:
                    file.write(f'\nexport function {message_name}Template(')
                    file.write(', '.join([f'{t[1]}' for t in template]))
                    file.write(f') {{\n')
                    file.write(f'    class {message_name} extends Structure {{\n')
                    spacing = "    "
                else:
                    file.write(f'\nexport class {message_name} extends Structure {{\n')

                # fields
                file.write(f'    {spacing}static fields = [\n')
                for field in fields:
                    is_array = field[2]
                    is_nested = "::" in field[0]
                    if is_array:
                        size = None
                        has_template = False
                        try:
                            size = int(field[2][1:-1])
                        except ValueError:
                            size = field[2][1:-1]
                            has_template = True
                        
                        if is_nested:
                            typeName = field[0].split("::")[1]
                            file.write(f'        {spacing}{{name: "{field[1]}", format: {typeName}, count: {size}}},\n')
                        elif has_template:
                            typeName = field[0]
                            file.write(f'        {spacing}{{name: "{field[1]}", format: `${{ {size} }}{format_chars[field[0]]}`}},\n')
                        else:
                            file.write(f'        {spacing}{{name: "{field[1]}", format: \"{size}{format_chars[field[0]]}\"}},\n')

                    elif is_nested:
                        typeName = field[0].split("::")[1]
                        file.write(f'        {spacing}{{name: "{field[1]}", format: {typeName}}},\n')
                    else:
                        file.write(f'        {spacing}{{name: "{field[1]}", format: "{format_chars[field[0]]}"}},\n')
                file.write(f'    {spacing}];\n\n')

                # hash
                file.write(f'    {spacing}static hash() {{\n')
                file.write(f'        {spacing}return [{hashValue[0]}n, {hashValue[1]}n];\n')
                file.write(f'    {spacing}}}\n\n')

                # size
                file.write(f'    {spacing}static size() {{\n')
                file.write(f'        {spacing}return Structure.sizeof({message_name}.fields, true);\n')
                file.write(f'    {spacing}}}\n\n')

                # decode
                file.write(f'    {spacing}static decode(msg) {{\n')
                file.write(f'        {spacing}if (msg.byteLength !== {message_name}.size()) {{\n')
                file.write(f'            {spacing}return null;\n')
                file.write(f'        {spacing}}}\n\n')
                file.write(f'        {spacing}return new {message_name}(msg);\n')
                file.write(f'    {spacing}}}\n\n')

                # constructor
                file.write(f'    {spacing}constructor(buffer) {{\n')
                file.write(f'        {spacing}super({message_name}.fields, true, buffer);\n')
                file.write(f'    {spacing}}}\n\n')

                # encode
                file.write(f'    {spacing}encode() {{\n')
                file.write(f'        {spacing}return this.buffer;\n')
                file.write(f'    {spacing}}}\n')
                file.write(f'{spacing}}}\n')

                if template:
                    file.write(f'\n    return {message_name};\n')
                    file.write(f'}}\n')

    # iterate through the sub directories and generate the index.js file
    packages = [f.path.split('/')[-1] for f in os.scandir(dir) if f.is_dir()]
    with open(dir + 'index.js', 'w') as file:
        for package in packages:
            file.write(f'export * as {package} from \'./{package}/index.js\';\n')
