#include "ignis_runtime.h" // Підключаємо наше "меню", щоб компілятор знав, що ми реалізуємо
#include <iostream>      // Підключаємо стандартну бібліотеку для введення/виведення
#include <new>

/**
 * Реалізація функції для виведення цілого числа.
 * @param value Число, яке потрібно вивести.
 */
void print_int(int64_t value) {
    std::cout << value << std::endl;
}

/**
 * Реалізація функції для виведення символу.
 * @param value Символ, який потрібно вивести.
 */
void ignis_putchar(char value) {
    std::cout << value;
}

/**
 * Реалізація функції для читання символу.
 * @return Прочитаний символ.
 */
char ignis_getchar() {
    return static_cast<char>(std::cin.get());
}

/**
 * Виділяє пам'ять заданого розміру.
 * У майбутньому тут буде логіка "Вахтера".
 * @param size Розмір в байтах.
 * @return Вказівник на виділену пам'ять.
 */
void* ignis_alloc(size_t size) {
    return ::operator new(size);
}

/**
 * Звільняє раніше виділену пам'ять.
 * У майбутньому тут буде логіка "Вахтера".
 * @param ptr Вказівник на пам'ять, яку потрібно звільнити.
 */
void ignis_free(void* ptr) {
    ::operator delete(ptr);
}