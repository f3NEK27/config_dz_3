import pytest
from config_translator import ConfigParser, ConfigToTOML


def parse_config(config_text):
    """Функция для парсинга конфигурации и преобразования в TOML."""
    content = config_text.strip().splitlines()
    parser = ConfigParser(content)
    parsed_data = parser.parse()
    return ConfigToTOML.convert(parsed_data)


def test_simple_assignment():
    """Тест: Простое присваивание константы."""
    config_text = """
    let x = 10;
    """
    toml_output = parse_config(config_text)
    assert toml_output == 'x = 10'


def test_array_assignment():
    """Тест: Присваивание массива."""
    config_text = """
    let arr = #(1, 2, 3, 4);
    """
    toml_output = parse_config(config_text)
    assert toml_output == 'arr = [1, 2, 3, 4]'


def test_constant_evaluation():
    """Тест: Использование вычисляемой константы."""
    config_text = """
    let x = 10;
    let y = @{x};
    """
    toml_output = parse_config(config_text)
    assert toml_output == 'x = 10\ny = 10'


def test_invalid_assignment():
    """Тест: Неправильный синтаксис присваивания."""
    config_text = """
    let x == 10;
    """
    with pytest.raises(SyntaxError):
        parse_config(config_text)


def test_undefined_constant_evaluation():
    """Тест: Использование несуществующей константы."""
    config_text = """
    let y = @{x};
    """
    with pytest.raises(SyntaxError):
        parse_config(config_text)


if __name__ == "__main__":
    pytest.main()
