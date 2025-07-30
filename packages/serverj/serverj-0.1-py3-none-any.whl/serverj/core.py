def join(ser_ip):
    print(f"Joined: {ser_ip}")

def idiot(asd):
    print(f"you're a fucking retard: {asd}")

def mean5(numbers):
    if len(numbers) != 5:
        raise ValueError("You must enter exactly 5 numbers.")
    return sum(numbers) / 5

