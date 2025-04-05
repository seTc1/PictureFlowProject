import os

# Словарь с файлами: ключ - название файла, значение - путь к файлу
file_dict = {
    'main.py': "main.py",
    'base.html': 'templates/base.html',
    'main.html': 'templates/main.html',
    'post.html': 'templates/post.html',
    'upload.html': 'templates/upload.html',
    'register.html': 'templates/register.html',
    'login.html': 'templates/login.html',
    'style.css': 'static/style.css',
    'form.css': 'static/form.css',
    'post.css': 'static/post.css',
    'main.css': 'static/main.css',
}


def read_files(file_names):
    combined_content = ""

    if "all" in file_names:
        file_names = file_dict.keys()

    for file_name in file_names:
        if file_name in file_dict:
            file_path = file_dict[file_name]
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    combined_content += f"=== Содержимое файла {file_name} ===\n"
                    combined_content += file.read()
                    combined_content += "\n\n"
            except FileNotFoundError:
                combined_content += f"Файл {file_name} не найден по пути {file_path}\n\n"
            except Exception as e:
                combined_content += f"Ошибка при чтении файла {file_name}: {str(e)}\n\n"
        else:
            combined_content += f"Файл {file_name} не найден в словаре\n\n"

    return combined_content.strip()


if __name__ == "__main__":
    print("Доступные файлы:", ", ".join(file_dict.keys()))
    input_files = input("Введите названия файлов через пробел: ").split()

    if not input_files:
        print("Вы не ввели ни одного названия файла")
    else:
        content = read_files(input_files)
        print("\n" + content)