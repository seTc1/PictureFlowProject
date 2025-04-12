import os

# Словарь с файлами: ключ - название файла, значение - путь к файлу
file_dict = {
    'main.py': "main.py",
    'media_files.py': "data/media_files.py",
    'db_session.py': "data/db_session.py",
    '__all_models.py': "data/__all_models.py",
    'users_data.py': "data/users_data.py",
    'media_form.py': "forms/media_form.py",
    'base.html': 'templates/base.html',
    'main.html': 'templates/main.html',
    'post.html': 'templates/post.html',
    'profile.html': 'templates/profile.html',
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
    else:
        # Обработка ввода расширений (.py, .css и т.д.)
        new_file_names = []
        for name in file_names:
            if name.startswith('.'):
                # Ищем все файлы с таким расширением
                for file in file_dict:
                    if file.endswith(name):
                        new_file_names.append(file)
            else:
                new_file_names.append(name)
        file_names = new_file_names

    for file_name in file_names:
        if file_name in file_dict:
            file_path = file_dict[file_name]
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    combined_content += f"=== Содержимое файла {file_path} ===\n"
                    combined_content += file.read()
                    combined_content += "\n\n"
            except FileNotFoundError:
                combined_content += f"Файл {file_path} не найден\n\n"
            except Exception as e:
                combined_content += f"Ошибка при чтении файла {file_path}: {str(e)}\n\n"
        else:
            combined_content += f"Файл {file_name} не найден в словаре\n\n"

    return combined_content.strip()


if __name__ == "__main__":
    print("Доступные файлы:", ", ".join(file_dict.keys()))
    print("Вы также можете ввести расширение файла, например: .py .css .html")
    input_files = input("Введите названия файлов или расширения через пробел: ").split()

    if not input_files:
        print("Вы не ввели ни одного названия файла или расширения")
    else:
        content = read_files(input_files)
        print("\n" + content)