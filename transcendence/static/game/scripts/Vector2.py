class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, right_side_vector):
        self.x += right_side_vector.x
        self.y += right_side_vector.y

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"
