#include "ignis_runtime.h" // Підключаємо наше "меню", щоб компілятор знав, що ми реалізуємо
#include <iostream>      // Підключаємо стандартну бібліотеку для введення/виведення

/**
 * Реалізація функції для виведення цілого числа.
 * @param value Число, яке потрібно вивести.
 */
void print_int(int64_t value) {
    std::cout << value;
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