def a():
    update = False
    def b():
        nonlocal update
        while not update:
            print("Hello")
            update = True
            
    b()
    return update
print(a())