#ifndef IGNIS_RUNTIME_H
#define IGNIS_RUNTIME_H

#include <cstdint> // Підключаємо, щоб мати доступ до типу int64_t
#include <cstddef>

/*
 * Оголошення вбудованих функцій мови Ignis,
 * які будуть викликатися зі згенерованого C++ коду.
 */

// Функція для виведення 64-бітного цілого числа на екран.
void print_int(int64_t value);

// Функція для виведення одного символу.
void ignis_putchar(char value);

// Функція для читання одного символу з вводу.
char ignis_getchar();

// Функції для керування пам'яттю
void* ignis_alloc(size_t size);
void ignis_free(void* ptr);

#endif //IGNIS_RUNTIME_H