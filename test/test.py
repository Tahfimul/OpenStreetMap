
def pos():
    hello()
    return 1;

def two():
    print("two")

def hello():
    print("hello")
    two()

print(pos())
