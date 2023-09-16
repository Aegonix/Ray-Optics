import pygame

class Button:
    def __init__(
        self,
        x: int,
        y: int,
        height: int,
        width: int,
        color: tuple,
        text: str,
        onpressed,
    ) -> None:
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
        self.text = text
        self.onpressed = onpressed
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, win):
        pygame.draw.rect(
            win,
            (255, 255, 255),
            self.rect,
            border_radius=10,
        )
        font = pygame.font.SysFont("JetBrains Mono", 20)
        text = font.render(self.text, True, self.color)
        win.blit(
            text,
            (
                self.x + (self.width / 2 - text.get_width() / 2),
                self.y + (self.height / 2 - text.get_height() / 2),
            ),
        )

    def update(self, win):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                self.onpressed()

        self.draw(win)