import subprocess
import os
import glob
import sys

# --- Налаштування ---
# Директорія з тестовими файлами
EXAMPLES_DIR = "examples"
# Директорія для бінарних файлів
BIN_DIR = os.path.join(EXAMPLES_DIR, "bin")
# Шлях до компілятора
COMPILER_PATH = os.path.join("ignis", "main.py")
# Колір для виводу
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

TESTS_TO_EXCLUDE = [
    "test_strings",
    "test_errors",
    "test_advanced_checker"
]


def main():
    """
    Головна функція, що знаходить, компілює та запускає всі .ign тести.
    """
    print(f"{YELLOW}--- Запуск повного тестування компілятора Ignis ---{RESET}\n")

    # 1. Переконуємось, що компілятор існує
    if not os.path.exists(COMPILER_PATH):
        print(f"{RED}Помилка: Не знайдено компілятор за шляхом '{COMPILER_PATH}'.{RESET}")
        sys.exit(1)

    # 2. Знаходимо всі тестові файли .ign
    test_files_raw = glob.glob(os.path.join(EXAMPLES_DIR, "*.ign"))
    if not test_files_raw:
        print(f"{RED}Помилка: Не знайдено жодного .ign файлу в директорії '{EXAMPLES_DIR}'.{RESET}")
        sys.exit(1)

    # 3. Створюємо директорію для бінарників, якщо її немає
    os.makedirs(BIN_DIR, exist_ok=True)

    test_files = []

    for ign_file in test_files_raw:
        base_name = os.path.splitext(os.path.basename(ign_file))[0]
        if base_name not in TESTS_TO_EXCLUDE:
            test_files.append(ign_file)

    # 4. Проходимо по кожному файлу, компілюємо та запускаємо
    for ign_file in sorted(test_files):
        try:
            # Назва файлу без розширення (напр., "test_memmanag")
            base_name = os.path.splitext(os.path.basename(ign_file))[0]

            # Повний шлях до вихідного бінарного файлу
            executable_path = os.path.join(BIN_DIR, base_name)

            # --- Етап компіляції ---
            print(f"[*] Компілюємо: {ign_file}")
            compile_command = [
                sys.executable,  # Використовуємо поточний інтерпретатор Python
                COMPILER_PATH,
                "-k",  # Зберігати проміжні файли
                "-o", executable_path,
                ign_file,
                "--target=cpp"
            ]

            # Запускаємо компілятор
            subprocess.run(compile_command, check=True, capture_output=True, text=True)
            print(f"{GREEN}[✓] Компіляція успішна!{RESET}\n")

            # --- Етап виконання ---
            print(f"[*] Запускаємо: {executable_path}")

            # Запускаємо скомпільований файл
            run_result = subprocess.run([executable_path], check=True, capture_output=True, text=True)
            print(f"{GREEN}[✓] Виконання успішне!{RESET}")

            # Виводимо результат роботи програми
            if run_result.stdout:
                print("--- Вивід програми ---")
                print(run_result.stdout.strip())
                print("----------------------\n")

        except subprocess.CalledProcessError as e:
            # Якщо компіляція або запуск провалились
            print(f"\n{RED}!!! Помилка на файлі: {ign_file} !!!{RESET}")
            #if "Компілюємо" in e.args[0]:  # Heuristic to check if it was compile time
            if 1 == e.args[0]:  # Heuristic to check if it was compile time
                print(f"{RED}Етап: Компіляція{RESET}")
            else:
                print(f"{RED}Етап: Виконання{RESET}")

            # Виводимо stderr, щоб було зрозуміло, що пішло не так
            print(f"\n--- Повідомлення про помилку ---")
            print(e.stderr)
            print("--------------------------------\n")
            sys.exit(1)  # Зупиняємо весь процес

    print(f"\n{GREEN}======================================")
    print(f"🎉 Всі {len(test_files)} тестів успішно пройдено! 🎉")
    print(f"======================================{RESET}")


if __name__ == "__main__":
    main()