class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, x, y):
        self.x += x
        self.y += y

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"
