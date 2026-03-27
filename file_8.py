import math

class CollisionManager:
    @staticmethod
    def circles_overlap(x1, y1, r1, x2, y2, r2):
        """Check if two circles overlap"""
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist < (r1 + r2)
    
    @staticmethod
    def point_in_rect(x, y, rect):
        """Check if point is in rectangle"""
        return (rect.left <= x <= rect.right and 
                rect.top <= y <= rect.bottom)
    
    @staticmethod
    def circle_rect_overlap(cx, cy, cr, rect):
        """Check if circle overlaps with rectangle"""
        closest_x = max(rect.left, min(cx, rect.right))
        closest_y = max(rect.top, min(cy, rect.bottom))
        dist = math.sqrt((cx - closest_x)**2 + (cy - closest_y)**2)
        return dist < cr