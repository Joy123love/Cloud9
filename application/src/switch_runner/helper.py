import pygame

from switch_runner.constants import BALL_RADIUS

def blit_rounded(surface, image, pos, radius=40):
    size = image.get_size()
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255,255,255,255), (0,0,*size), border_radius=radius)
    img_copy = image.copy()
    img_copy.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(img_copy, pos)

# Utility to draw a transparent bubble over the player when invincible
def blit_transparent_bubble(surface, bubble_img, center, scale=2.2, alpha=140):
    # Scale bubble
    size = int(BALL_RADIUS * 2 * scale)
    bubble = pygame.transform.smoothscale(bubble_img, (size, size)).copy()
    bubble.set_alpha(alpha)
    x = center[0] - size // 2
    y = center[1] - size // 2
    surface.blit(bubble, (x, y))
