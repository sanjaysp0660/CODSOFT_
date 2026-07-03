import math
import os
import statistics
import sys
from datetime import datetime

# Terminal color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

history = []
memory_value = 0.0
previous_result = None


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_header():
    clear_screen()
    print(CYAN + "=" * 70)
    print("Sanjay'S calculator")
    print("=" * 70 + RESET)
    print(GREEN + "15+ Features | History | Memory | Conversions | Scientific" + RESET)


def prompt_number(prompt_text):
    global previous_result
    while True:
        raw = input(BLUE + prompt_text + RESET).strip()
        if raw.lower() == "p" and previous_result is not None:
            print(YELLOW + f"Using previous result: {previous_result}" + RESET)
            return previous_result
        try:
            return float(raw)
        except ValueError:
            print(RED + "Invalid number. Enter a valid numeric value or 'P' for previous result." + RESET)


def prompt_list(prompt_text):
    while True:
        raw = input(BLUE + prompt_text + RESET).strip()
        raw = raw.replace(",", " ")
        parts = raw.split()
        try:
            values = [float(value) for value in parts if value != ""]
            if len(values) < 2:
                raise ValueError
            return values
        except ValueError:
            print(RED + "Enter at least two numeric values separated by spaces or commas." + RESET)


def add_history(entry):
    history.append(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {entry}")


def save_history():
    filename = "calculator_history.txt"
    try:
        with open(filename, "a", encoding="utf-8") as file:
            for entry in history:
                file.write(entry + "\n")
        print(GREEN + f"History saved to {filename}." + RESET)
    except Exception as exc:
        print(RED + f"Failed to save history: {exc}" + RESET)


def show_history():
    print(BLUE + "\nCalculation History:" + RESET)
    if not history:
        print(YELLOW + "No calculations yet." + RESET)
        return
    for entry in history[-10:]:
        print(entry)


def show_memory():
    print(BLUE + f"\nMemory value: {memory_value}" + RESET)


def basic_operations():
    global previous_result
    print(YELLOW + "\nBasic Operations:" + RESET)
    print(" 1. Addition")
    print(" 2. Subtraction")
    print(" 3. Multiplication")
    print(" 4. Division")
    print(" 5. Modulus")
    print(" 6. Percentage")
    print(" 7. Reciprocal")
    print(" 8. Absolute value")

    choice = input(BLUE + "Choose operation (1-8): " + RESET).strip()
    a = prompt_number("Enter first number: ")
    result = None

    if choice in {"1", "2", "3", "4", "5"}:
        b = prompt_number("Enter second number: ")

    try:
        if choice == "1":
            result = a + b
            op = f"{a} + {b}"
        elif choice == "2":
            result = a - b
            op = f"{a} - {b}"
        elif choice == "3":
            result = a * b
            op = f"{a} * {b}"
        elif choice == "4":
            if b == 0:
                raise ZeroDivisionError
            result = a / b
            op = f"{a} / {b}"
        elif choice == "5":
            result = a % b
            op = f"{a} % {b}"
        elif choice == "6":
            result = a * b / 100
            op = f"{a}% of {b}"
        elif choice == "7":
            if a == 0:
                raise ZeroDivisionError
            result = 1 / a
            op = f"1/{a}"
        elif choice == "8":
            result = abs(a)
            op = f"abs({a})"
        else:
            print(RED + "Invalid selection." + RESET)
            return

        previous_result = result
        add_history(f"{op} = {result}")
        print(GREEN + f"Result: {result}" + RESET)
    except ZeroDivisionError:
        print(RED + "Error: Division by zero is not allowed." + RESET)
    except Exception as exc:
        print(RED + f"Operation failed: {exc}" + RESET)


def scientific_operations():
    global previous_result
    print(YELLOW + "\nScientific Operations:" + RESET)
    print(" 1. Exponentiation")
    print(" 2. Square root")
    print(" 3. Nth root")
    print(" 4. Factorial")
    print(" 5. Natural logarithm")
    print(" 6. Base-10 logarithm")
    print(" 7. Sine")
    print(" 8. Cosine")
    print(" 9. Tangent")
    print("10. Floor")
    print("11. Ceiling")

    choice = input(BLUE + "Choose operation (1-11): " + RESET).strip()
    try:
        if choice == "1":
            base = prompt_number("Enter base: ")
            exp = prompt_number("Enter exponent: ")
            result = math.pow(base, exp)
            op = f"{base} ^ {exp}"
        elif choice == "2":
            value = prompt_number("Enter number: ")
            if value < 0:
                raise ValueError("Negative number")
            result = math.sqrt(value)
            op = f"sqrt({value})"
        elif choice == "3":
            value = prompt_number("Enter number: ")
            n = prompt_number("Enter root degree: ")
            if n == 0:
                raise ValueError("Zero root")
            result = value ** (1 / n)
            op = f"root({n}) of {value}"
        elif choice == "4":
            value = prompt_number("Enter non-negative integer: ")
            if value < 0 or not value.is_integer():
                raise ValueError("Factorial requires a non-negative integer")
            result = math.factorial(int(value))
            op = f"{int(value)}!"
        elif choice == "5":
            value = prompt_number("Enter positive number: ")
            if value <= 0:
                raise ValueError("Non-positive number")
            result = math.log(value)
            op = f"ln({value})"
        elif choice == "6":
            value = prompt_number("Enter positive number: ")
            if value <= 0:
                raise ValueError("Non-positive number")
            result = math.log10(value)
            op = f"log10({value})"
        elif choice == "7":
            value = prompt_number("Enter degrees: ")
            result = math.sin(math.radians(value))
            op = f"sin({value}°)"
        elif choice == "8":
            value = prompt_number("Enter degrees: ")
            result = math.cos(math.radians(value))
            op = f"cos({value}°)"
        elif choice == "9":
            value = prompt_number("Enter degrees: ")
            result = math.tan(math.radians(value))
            op = f"tan({value}°)"
        elif choice == "10":
            value = prompt_number("Enter number: ")
            result = math.floor(value)
            op = f"floor({value})"
        elif choice == "11":
            value = prompt_number("Enter number: ")
            result = math.ceil(value)
            op = f"ceil({value})"
        else:
            print(RED + "Invalid selection." + RESET)
            return

        previous_result = result
        add_history(f"{op} = {result}")
        print(GREEN + f"Result: {result}" + RESET)
    except ValueError as exc:
        print(RED + f"Input error: {exc}" + RESET)
    except OverflowError:
        print(RED + "Error: Result overflowed." + RESET)
    except Exception as exc:
        print(RED + f"Operation failed: {exc}" + RESET)


def statistics_operations():
    global previous_result
    print(YELLOW + "\nStatistics Operations:" + RESET)
    print(" 1. Mean")
    print(" 2. Median")
    print(" 3. Mode")
    print(" 4. Standard deviation")
    print(" 5. Min and Max")
    print(" 6. Sum of values")

    choice = input(BLUE + "Choose operation (1-6): " + RESET).strip()
    values = prompt_list("Enter numbers separated by spaces or commas: ")

    try:
        if choice == "1":
            result = statistics.mean(values)
            op = f"mean({values})"
        elif choice == "2":
            result = statistics.median(values)
            op = f"median({values})"
        elif choice == "3":
            try:
                result = statistics.mode(values)
            except statistics.StatisticsError:
                result = "No unique mode"
            op = f"mode({values})"
        elif choice == "4":
            result = statistics.pstdev(values)
            op = f"stddev({values})"
        elif choice == "5":
            result = (min(values), max(values))
            op = f"min/max({values})"
        elif choice == "6":
            result = sum(values)
            op = f"sum({values})"
        else:
            print(RED + "Invalid selection." + RESET)
            return

        previous_result = result
        add_history(f"{op} = {result}")
        print(GREEN + f"Result: {result}" + RESET)
    except Exception as exc:
        print(RED + f"Operation failed: {exc}" + RESET)


def conversion_operations():
    global previous_result
    print(YELLOW + "\nConversion Operations:" + RESET)
    print(" 1. Celsius to Fahrenheit")
    print(" 2. Fahrenheit to Celsius")
    print(" 3. Celsius to Kelvin")
    print(" 4. Kelvin to Celsius")
    print(" 5. Fahrenheit to Kelvin")
    print(" 6. Kelvin to Fahrenheit")

    choice = input(BLUE + "Choose conversion (1-6): " + RESET).strip()
    try:
        value = prompt_number("Enter temperature value: ")
        if choice == "1":
            result = (value * 9 / 5) + 32
            op = f"{value}°C to °F"
        elif choice == "2":
            result = (value - 32) * 5 / 9
            op = f"{value}°F to °C"
        elif choice == "3":
            result = value + 273.15
            op = f"{value}°C to K"
        elif choice == "4":
            result = value - 273.15
            op = f"{value}K to °C"
        elif choice == "5":
            result = (value - 32) * 5 / 9 + 273.15
            op = f"{value}°F to K"
        elif choice == "6":
            result = (value - 273.15) * 9 / 5 + 32
            op = f"{value}K to °F"
        else:
            print(RED + "Invalid selection." + RESET)
            return

        previous_result = result
        add_history(f"{op} = {result}")
        print(GREEN + f"Result: {result}" + RESET)
    except Exception as exc:
        print(RED + f"Conversion failed: {exc}" + RESET)


def memory_operations():
    global memory_value, previous_result
    print(YELLOW + "\nMemory Operations:" + RESET)
    print(" 1. M+ (add previous result to memory)")
    print(" 2. M- (subtract previous result from memory)")
    print(" 3. MR (recall memory)")
    print(" 4. MC (clear memory)")

    choice = input(BLUE + "Choose operation (1-4): " + RESET).strip()
    if choice == "1":
        if previous_result is None:
            print(RED + "No previous result available." + RESET)
            return
        memory_value += previous_result
        add_history(f"Memory add {previous_result} -> {memory_value}")
        print(GREEN + f"Memory updated: {memory_value}" + RESET)
    elif choice == "2":
        if previous_result is None:
            print(RED + "No previous result available." + RESET)
            return
        memory_value -= previous_result
        add_history(f"Memory subtract {previous_result} -> {memory_value}")
        print(GREEN + f"Memory updated: {memory_value}" + RESET)
    elif choice == "3":
        print(BLUE + f"Memory recall: {memory_value}" + RESET)
    elif choice == "4":
        memory_value = 0.0
        add_history("Memory cleared")
        print(GREEN + "Memory cleared." + RESET)
    else:
        print(RED + "Invalid selection." + RESET)


def main_menu():
    while True:
        show_header()
        print(" 1. Basic calculator")
        print(" 2. Scientific calculator")
        print(" 3. Statistics tools")
        print(" 4. Temperature conversions")
        print(" 5. Memory functions")
        print(" 6. View history")
        print(" 7. Save history")
        print(" 8. Clear screen")
        print(" 9. Exit")
        choice = input(BLUE + "\nChoose a menu option (1-9): " + RESET).strip()

        if choice == "1":
            basic_operations()
        elif choice == "2":
            scientific_operations()
        elif choice == "3":
            statistics_operations()
        elif choice == "4":
            conversion_operations()
        elif choice == "5":
            memory_operations()
        elif choice == "6":
            show_history()
        elif choice == "7":
            save_history()
        elif choice == "8":
            clear_screen()
            continue
        elif choice == "9":
            print(GREEN + "\nThank you for using the enhanced calculator. Goodbye!" + RESET)
            break
        else:
            print(RED + "Invalid selection. Please choose between 1 and 9." + RESET)

        input(BLUE + "\nPress Enter to return to the main menu..." + RESET)


if __name__ == "__main__":
    main_menu()