def clamp(value, min_val, max_val):
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))

def distance(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

def normalize(x, y):
    """Normalize vector"""
    length = (x**2 + y**2)**0.5
    if length == 0:
        return 0, 0
    return x / length, y / length