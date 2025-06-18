def greet(name="world"):
    """Greets the user."""
    message = f"Hello, {name}!"
    print(message)
    return message

if __name__ == "__main__":
    greet()
