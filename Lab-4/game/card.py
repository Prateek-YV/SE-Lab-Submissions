import pygame


class Card:
    _fonts = {}

    @classmethod
    def _font(cls, size):
        if size not in cls._fonts:
            cls._fonts[size] = pygame.font.SysFont(None, size)
        return cls._fonts[size]

    def __init__(self, rank_str, suit_str, numeric_rank):
        self.rank_str = rank_str
        self.suit_str = suit_str
        self.numeric_rank = numeric_rank

        self.symbol = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}.get(suit_str, "")
        self.is_red = suit_str in ("Hearts", "Diamonds")
        self.color = (220, 40, 40) if self.is_red else (30, 30, 30)

    def render(self, surface, x, y, width=130, height=180):
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 50), card_rect, width=3, border_radius=10)

        font_rank = self._font(36)
        font_symbol = self._font(64)

        rank_surf = font_rank.render(self.rank_str, True, self.color)
        surface.blit(rank_surf, (x + 10, y + 8))

        self._draw_suit(surface, x + width // 2, y + height // 2, 26)

        surface.blit(rank_surf, (x + width - rank_surf.get_width() - 10, y + height - rank_surf.get_height() - 8))

    def _draw_suit(self, surface, cx, cy, s):
        """Draws the suit with shapes so it never depends on font glyph support."""
        c = self.color
        if self.suit_str == "Hearts":
            r = s // 2
            pygame.draw.circle(surface, c, (cx - r, cy - r // 2), r)
            pygame.draw.circle(surface, c, (cx + r, cy - r // 2), r)
            pygame.draw.polygon(surface, c, [(cx - s + 1, cy - r // 4), (cx + s - 1, cy - r // 4), (cx, cy + s)])
        elif self.suit_str == "Diamonds":
            pygame.draw.polygon(surface, c, [(cx, cy - s), (cx + int(s * 0.7), cy), (cx, cy + s), (cx - int(s * 0.7), cy)])
        elif self.suit_str == "Clubs":
            r = int(s * 0.42)
            pygame.draw.circle(surface, c, (cx, cy - r), r)
            pygame.draw.circle(surface, c, (cx - r, cy + r // 2), r)
            pygame.draw.circle(surface, c, (cx + r, cy + r // 2), r)
            pygame.draw.polygon(surface, c, [(cx - 4, cy + r), (cx + 4, cy + r), (cx + 7, cy + s), (cx - 7, cy + s)])
        else:  # Spades
            r = s // 2
            pygame.draw.circle(surface, c, (cx - r, cy + r // 3), r)
            pygame.draw.circle(surface, c, (cx + r, cy + r // 3), r)
            pygame.draw.polygon(surface, c, [(cx - s + 1, cy + r // 6), (cx + s - 1, cy + r // 6), (cx, cy - s)])
            pygame.draw.polygon(surface, c, [(cx - 4, cy + r), (cx + 4, cy + r), (cx + 7, cy + s), (cx - 7, cy + s)])

    @classmethod
    def render_back(cls, surface, x, y, width=130, height=180):
        """Draws a face-down card (used for the hidden next card)."""
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (35, 60, 140), card_rect, border_radius=10)
        pygame.draw.rect(surface, (240, 240, 240), card_rect, width=3, border_radius=10)
        inner = card_rect.inflate(-24, -24)
        pygame.draw.rect(surface, (70, 100, 190), inner, width=2, border_radius=6)
        q = cls._font(64).render("?", True, (240, 240, 240))
        surface.blit(q, (card_rect.centerx - q.get_width() // 2, card_rect.centery - q.get_height() // 2))
