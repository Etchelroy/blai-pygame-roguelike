import math

def check_wall_collision(entity, walls):
    for wall in walls:
        cx = max(wall.left, min(entity.x, wall.right))
        cy = max(wall.top, min(entity.y, wall.bottom))
        dx = entity.x - cx
        dy = entity.y - cy
        dist = math.hypot(dx, dy)
        if dist < entity.radius:
            if dist == 0:
                entity.x += entity.radius
                return
            overlap = entity.radius - dist
            entity.x += (dx / dist) * overlap
            entity.y += (dy / dist) * overlap

def check_entity_collision(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dist = math.hypot(dx, dy)
    return dist < (a.radius + b.radius)