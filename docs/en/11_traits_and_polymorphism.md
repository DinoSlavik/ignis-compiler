# 11. Traits and Polymorphism

In Ignis, unlike languages with classical inheritance, code flexibility is achieved not through complex class hierarchies, but through **traits**. A trait is a mechanism, borrowed from Rust, that allows for defining shared behavior for different types.

## What is a Trait?

A trait is, in essence, a **behavioral contract**. It declares a set of methods that a certain data type must implement, but it does not provide their implementation. A trait is an analogue of an **interface** in other languages.

The main idea behind traits is to **separate the definition of a behavior from its concrete implementation**. This allows writing code that works with any types that adhere to a single contract, without knowing anything about their internal structure.

## Declaring a Trait

A trait is declared using the `trait` keyword and contains a list of method signatures (their names, parameters, and return type).

```Ignis

// Declaring a contract for anything that can be drawn on the screen
trait Drawable {
    // Any type that implements Drawable must have this method
    void draw(ptr self);
}
```

## Implementing a Trait

For a class to use a trait, it must **implement** it. This process consists of two parts:
- **Declaring the implementation**: In the class header, after its name and the list of parent classes (if any), the `implements` keyword is used, followed by a list of traits.
- **Providing the implementation**: The methods declared in the trait must be implemented in an `impl` block for that class.


```Ignis

// Creating two completely different classes
class Player { public: char id; }
class Button { public: string text; }

// --- Implementation for the Player class ---

// 1. Declare that Player will implement the Drawable trait
class Player implements Drawable {

    // 2. Provide the concrete implementation for the draw method
    impl draw in Player {
        void draw(ptr Player self) {
            // ... logic for drawing the player ...
            putchar(self.id);
        }
    }
}


// --- Implementation for the Button class ---
class Button implements Drawable {
    impl draw in Button {
        void draw(ptr Button self) {
            // ... logic for drawing the button ...
            print_string(self.text);
        }
    }
}
```

Note: Due to the increased nesting, the code can become less readable, so it is recommended to write it in the following format:

```Ignis

class ClassName { ... }

class ClassName implements TraitName {
impl trait_method1 in ClassName {
    void trait_method1( ... ) { 
        ... 
    }
    
    void trait_method1( ... ) { 
        ... 
    }
}

impl trait_method2 in ClassName {
    int trait_method2( ... ) { 
        ... 
    }
}}
```

## Polymorphism: The Power of Traits

The main advantage of traits is revealed when we use them to achieve **polymorphism** — the ability to work with objects of different types through a unified interface.

A function can accept a parameter whose type is not a specific class, but a **trait**. This means that you can pass **any object** to this function, as long as its class implements that trait.

```Ignis

// This function doesn't know what it's drawing - a player, a button, or something else.
// It only knows that the object is GUARANTEED to have a draw() method.
void render_object(ptr Drawable obj) {
    obj.draw();
}

int main() {
    mut ptr Player p = new Player();
    p.id = 'P';

    mut ptr Button b = new Button();
    b.text = "[OK]";

    // We can pass objects of completely different types
    // into the same function because they both implement the Drawable trait.
    render_object(p);
    render_object(b);

    free(p);
    free(b);
    return 0;
}
```
