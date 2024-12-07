import argparse
import re
import toml

class ConfigParser:
    def __init__(self, file_content):
        self.content = file_content
        self.position = 0
        self.constants = {}  # Хранилище для констант

    def parse(self):
        return self.parse_blocks()

    def parse_blocks(self):
        blocks = []
        while self.position < len(self.content):
            line = self.content[self.position].strip()
            if line.startswith("let"):
                blocks.append(self.parse_assignment(line))
            elif re.match(r"@{[a-zA-Z][_a-zA-Z0-9]*}", line):  # Проверка на выражение @{x}
                blocks.append(self.parse_evaluation(line))
            else:
                self.error(f"Unexpected syntax: {line}")
            self.position += 1
        return blocks

    def parse_assignment(self, line):
        match = re.match(r"let\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+);", line)
        if match:
            name, value = match.groups()
            self.constants[name] = self.parse_value(value.strip())
            return {"type": "assignment", "name": name, "value": self.constants[name]}
        else:
            self.error(f"Invalid assignment syntax: {line}")

    def parse_evaluation(self, line):
        match = re.match(r"@{([a-zA-Z][_a-zA-Z0-9]*)}", line)
        if match:
            const_name = match.groups()[0]
            if const_name in self.constants:
                return {"type": "evaluation", "name": const_name, "value": self.constants[const_name]}
            else:
                self.error(f"Undefined constant: {const_name}")
        else:
            self.error(f"Invalid evaluation syntax: {line}")

    def parse_value(self, value):
        # Если это выражение типа @{x}, обрабатываем как ссылку на константу
        if value.startswith('@{') and value.endswith('}'):
            const_name = value[2:-1]
            if const_name in self.constants:
                return self.constants[const_name]
            else:
                self.error(f"Undefined constant: {const_name}")
        elif re.match(r"^\d+$", value):  # Числа
            return int(value)
        elif value.startswith("#(") and value.endswith(")"):  # Массив
            return self.parse_array(value)
        else:
            self.error(f"Invalid value: {value}")

    def parse_array(self, value):
        items = value[2:-1].split(",")
        return [self.parse_value(item.strip()) for item in items]

    def error(self, message):
        raise SyntaxError(message)


class ConfigToTOML:
    @staticmethod
    def convert(data):
        result = []
        for block in data:
            if block["type"] == "assignment":
                result.append(f'{block["name"]} = {ConfigToTOML.format_value(block["value"])}')
            elif block["type"] == "evaluation":
                result.append(f'{block["name"]} = {ConfigToTOML.format_value(block["value"])}')
        return "\n".join(result)

    @staticmethod
    def format_value(value):
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, list):
            return "[" + ", ".join(map(str, value)) + "]"
        else:
            return f'"{value}"'


def main():
    parser = argparse.ArgumentParser(description="Transform a custom config language to TOML.")
    parser.add_argument("input", type=str, help="Path to the input file.")
    parser.add_argument("output", type=str, help="Path to the output TOML file.")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as file:
            content = file.readlines()

        parser = ConfigParser(content)
        parsed_data = parser.parse()

        toml_output = ConfigToTOML.convert(parsed_data)

        with open(args.output, "w", encoding="utf-8") as output_file:
            output_file.write(toml_output)

        print(f"TOML has been written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
