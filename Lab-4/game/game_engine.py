import pygame
from game.deck import Deck


class GameEngine:
    # Game states
    WAITING = "WAITING"      # player is choosing HIGHER / LOWER
    REVEALING = "REVEALING"  # new card is being flipped / shown, input locked

    FLIP_MS = 350            # duration of the flip animation
    REVEAL_MS = 1300         # total time the result stays on screen (includes flip)
    MAX_MULTIPLIER = 5       # streak multiplier cap

    CARD_W, CARD_H = 130, 180

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deck = Deck()

        self.current_card = self.deck.draw()
        self.next_card = None
        self.score = 0
        self.streak = 0
        self.multiplier = 1
        self.state = self.WAITING
        self.reveal_start = 0
        self.status_msg = "Will the next card be HIGHER or LOWER?"
        self.status_color = (220, 220, 220)
        self.pending_msg = self.status_msg
        self.pending_color = self.status_color

        btn_w, btn_h = 140, 48
        self.btn_higher = pygame.Rect(width // 2 - btn_w - 20, height - 90, btn_w, btn_h)
        self.btn_lower = pygame.Rect(width // 2 + 20, height - 90, btn_w, btn_h)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 24)

        gap = 30
        self.left_x = width // 2 - self.CARD_W - gap
        self.right_x = width // 2 + gap
        self.card_y = 100

    # ------------------------------------------------------------------ logic
    def streak_multiplier(self):
        """x1 on the first win, then x2, x3 ... capped at MAX_MULTIPLIER."""
        return min(max(self.streak, 1), self.MAX_MULTIPLIER)

    def evaluate_guess(self, guess):
        """Draws next card, evaluates prediction, starts the reveal."""
        self.next_card = self.deck.draw()
        cur, nxt = self.current_card, self.next_card

        # Compare by numeric rank (2 < ... < 10 < J < Q < K < A), never by string.
        if nxt.numeric_rank == cur.numeric_rank:
            outcome = "PUSH"
        elif guess == "HIGHER":
            outcome = "CORRECT" if nxt.numeric_rank > cur.numeric_rank else "WRONG"
        else:
            outcome = "CORRECT" if nxt.numeric_rank < cur.numeric_rank else "WRONG"

        if outcome == "CORRECT":
            self.streak += 1
            self.multiplier = self.streak_multiplier()
            self.score += self.multiplier
            self.pending_msg = (
                f"CORRECT! {nxt.rank_str} vs {cur.rank_str}  "
                f"+{self.multiplier} (streak {self.streak}, x{self.multiplier})"
            )
            self.pending_color = (80, 220, 80)
        elif outcome == "WRONG":
            self.streak = 0
            self.multiplier = 1
            self.score = max(0, self.score - 1)
            self.pending_msg = f"WRONG! {nxt.rank_str} vs {cur.rank_str}  streak reset"
            self.pending_color = (235, 75, 75)
        else:  # PUSH: score and streak untouched
            self.pending_msg = f"PUSH! {nxt.rank_str} vs {cur.rank_str}  score and streak kept"
            self.pending_color = (240, 200, 70)

        self.state = self.REVEALING
        self.reveal_start = pygame.time.get_ticks()
        self.status_msg = "Revealing..."
        self.status_color = (220, 220, 220)

    def handle_event(self, event):
        if self.state != self.WAITING:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_higher.collidepoint(event.pos):
                self.evaluate_guess("HIGHER")
            elif self.btn_lower.collidepoint(event.pos):
                self.evaluate_guess("LOWER")

    def update(self):
        if self.state != self.REVEALING:
            return
        elapsed = pygame.time.get_ticks() - self.reveal_start
        if elapsed >= self.FLIP_MS:
            self.status_msg = self.pending_msg
            self.status_color = self.pending_color
        if elapsed >= self.REVEAL_MS:
            self.current_card = self.next_card
            self.next_card = None
            self.state = self.WAITING

    # ---------------------------------------------------------------- drawing
    def _draw_flip(self, screen, elapsed):
        """Right-hand card: back shrinks to a sliver, then the face grows out."""
        t = min(elapsed / self.FLIP_MS, 1.0)
        surf = pygame.Surface((self.CARD_W, self.CARD_H), pygame.SRCALPHA)
        if t < 0.5:
            Card_back = self.next_card.render_back
            Card_back(surf, 0, 0, self.CARD_W, self.CARD_H)
            scale = 1 - t * 2
        else:
            self.next_card.render(surf, 0, 0, self.CARD_W, self.CARD_H)
            scale = (t - 0.5) * 2
        w = max(2, int(self.CARD_W * scale))
        scaled = pygame.transform.smoothscale(surf, (w, self.CARD_H))
        screen.blit(scaled, (self.right_x + (self.CARD_W - w) // 2, self.card_y))

    def _button(self, screen, rect, fill, label):
        enabled = self.state == self.WAITING
        pygame.draw.rect(screen, fill if enabled else (90, 90, 90), rect, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=8)
        surf = self.font_medium.render(label, True, (255, 255, 255) if enabled else (170, 170, 170))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

    def render(self, screen):
        screen.fill((25, 80, 45))

        title_surf = self.font_title.render("High-Low Card Predictor", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (30, 30))
        streak_surf = self.font_small.render(
            f"Streak: {self.streak}  (x{self.streak_multiplier() if self.streak else 1})", True, (255, 200, 120)
        )
        screen.blit(streak_surf, (30, 58))

        rem_surf = self.font_small.render(f"Deck: {self.deck.remaining} left", True, (210, 210, 210))
        screen.blit(rem_surf, (self.width - rem_surf.get_width() - 30, 35))

        # Side-by-side cards with captions
        left_label = "PREVIOUS" if self.state == self.REVEALING else "CURRENT"
        right_label = "NEW CARD" if self.state == self.REVEALING else "NEXT"
        for label, x in ((left_label, self.left_x), (right_label, self.right_x)):
            cap = self.font_small.render(label, True, (200, 230, 200))
            screen.blit(cap, (x + self.CARD_W // 2 - cap.get_width() // 2, self.card_y - 24))

        self.current_card.render(screen, self.left_x, self.card_y, self.CARD_W, self.CARD_H)
        if self.state == self.REVEALING:
            self._draw_flip(screen, pygame.time.get_ticks() - self.reveal_start)
        else:
            self.current_card.render_back(screen, self.right_x, self.card_y, self.CARD_W, self.CARD_H)

        status_surf = self.font_small.render(self.status_msg, True, self.status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 310))

        self._button(screen, self.btn_higher, (40, 140, 60), "HIGHER")
        self._button(screen, self.btn_lower, (170, 50, 50), "LOWER")
