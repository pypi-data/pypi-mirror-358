'''
a simple set of pygame gui class's
'''
import time
import pygame

class Button:
    def __init__(self, x, y, width=100, height=100, border_size=5,
                 colour=(255, 255, 255), border_colour=(0, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_size = border_size
        self.colour = colour
        self.border_colour = border_colour
        self.toggled = False

        # internal flags to handle states
        self._was_clicked = False
        self._is_hovering = False
        self._is_pressed = False

        # callbacks
        self._click_callback = None
        self._toggle_on_callback = None
        self._toggle_off_callback = None
        self._on_hit_callback = None
        self._on_released_callback = None
        self._while_pressed_callback = None

    # --- callback setters ---

    def on_click(self, func):
        self._click_callback = func
        return func

    def on_toggle_on(self, func):
        self._toggle_on_callback = func
        return func

    def on_toggle_off(self, func):
        self._toggle_off_callback = func
        return func

    def on_hit(self, func):
        self._on_hit_callback = func
        return func

    def on_released(self, func):
        self._on_released_callback = func
        return func

    def while_pressed(self, func):
        self._while_pressed_callback = func
        return func

    # --- tick method to update and draw the button ---

    def tick(self, screen):
        import pygame  # make sure pygame is imported in your file

        # draw the button
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_colour, (self.x, self.y, self.width, self.height), self.border_size)

        # get input state
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # check hovering
        self._is_hovering = (self.x <= mouse_pos[0] <= self.x + self.width and
                             self.y <= mouse_pos[1] <= self.y + self.height)

        if self._is_hovering:
            if mouse_pressed:
                if not self._is_pressed:
                    self._is_pressed = True
                    if self._on_hit_callback:
                        self._on_hit_callback()
                if self._while_pressed_callback:
                    self._while_pressed_callback()
                if not self._was_clicked:
                    self._was_clicked = True
                    if self._click_callback:
                        self._click_callback()
                    if self.toggled:
                        self.toggled = False
                        if self._toggle_off_callback:
                            self._toggle_off_callback()
                    else:
                        self.toggled = True
                        if self._toggle_on_callback:
                            self._toggle_on_callback()
            else:
                if self._is_pressed:
                    self._is_pressed = False
                    if self._on_released_callback:
                        self._on_released_callback()
                self._was_clicked = False
        else:
            if not mouse_pressed and self._is_pressed:
                self._is_pressed = False
                if self._on_released_callback:
                    self._on_released_callback()
            self._was_clicked = False

class TextBox:
    def __init__(self, x, y, width, height, background_color, outline_color=None, font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.background_color = background_color
        self.outline_color = outline_color
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.line_spacing = 5  # Space between lines

    def tick(self, screen):
        # Draw the text box
        pygame.draw.rect(screen, self.background_color, self.rect)
        if self.outline_color:
            pygame.draw.rect(screen, self.outline_color, self.rect, 2)
        
        # Render wrapped text
        self.render_text(screen)
    
    def render_text(self, screen):
        words = self.text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < self.rect.width - 10:  # Check if it fits
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        
        lines.append(current_line)  # Add the last line
        
        y_offset = 5
        for line in lines:
            if y_offset + self.font.get_height() > self.rect.height - 5:
                break  # Stop drawing if we run out of space
            text_surface = self.font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + y_offset))
            y_offset += self.font.get_height() + self.line_spacing

    def get_text(self):
        return self.text

    def set_text(self, new_text):
        self.text = new_text

class TextInputBox:
    def __init__(self, x, y, width, height, char_limit, background_color, outline_color=None, font_size=30, bg_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.char_limit = char_limit
        self.background_color = background_color
        self.outline_color = outline_color
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.Typeing_ = False  # Flag: True while user is typing
        self.InputBegin_ = False
        self.clearOnInputBegin = False
        self.line_spacing = font_size + (font_size / 4)  # Line spacing for new lines
        self.lines = [""]  # List of lines to render
        self.backspace_held = False
        self.backspace_timer = 0
        self.backspace_delay = 300  # Initial delay before holding (ms)
        self.backspace_repeat = 50  # Repeat rate when holding (ms)
        self.bg_text = bg_text  # Background text when empty

        # Callback attributes for decorator registration:
        self._on_typing = None
        self._on_input_ended = None
        self._prev_typing = False  # To detect state changes

    def wrap_text(self):
        """
        Rebuilds self.lines based on self.text.
        Newline characters (added via Shift+Enter) are honored so that
        they force a line break rather than displaying a literal "\n".
        """
        self.lines = []
        current_line = ""
        for char in self.text:
            # If we encounter a newline, append the current line and start a new one.
            if char == "\n":
                self.lines.append(current_line)
                current_line = ""
            else:
                test_line = current_line + char
                # Check if the test_line width is within the text box (with some padding)
                if self.font.size(test_line)[0] < self.rect.width - 10:
                    current_line = test_line
                else:
                    # If not, append the current line and start a new one with the character.
                    self.lines.append(current_line)
                    current_line = char
        self.lines.append(current_line)

        # Limit the number of lines to fit the text box height.
        max_lines = int(self.rect.height // self.line_spacing)
        self.lines = self.lines[-max_lines:]

    def tick(self, events, screen):
        # Store previous typing state so we can detect when input ends.
        prev_typing = self.Typeing_
        
        pygame.draw.rect(screen, self.background_color, self.rect)
        if self.outline_color:
            pygame.draw.rect(screen, self.outline_color, self.rect, 2)
        
        # Render each line separately.
        if self.text:
            for i, line in enumerate(self.lines):
                text_surface = self.font.render(line, True, (0, 0, 0))
                screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5 + i * self.line_spacing))
        else:
            bg_text_surface = self.font.render(self.bg_text, True, (150, 150, 150))
            screen.blit(bg_text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        keys = pygame.key.get_pressed()
        if self.Typeing_ and keys[pygame.K_BACKSPACE]:
            if not self.backspace_held:
                self.text = self.text[:-1]
                self.wrap_text()
                self.backspace_held = True
                self.backspace_timer = pygame.time.get_ticks() + self.backspace_delay
            elif pygame.time.get_ticks() > self.backspace_timer:
                self.text = self.text[:-1]
                self.wrap_text()
                self.backspace_timer = pygame.time.get_ticks() + self.backspace_repeat
        else:
            self.backspace_held = False
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    # Toggle input begin
                    self.InputBegin_ = not self.Typeing_
                    self.Typeing_ = True
                    if self.clearOnInputBegin and self.InputBegin_:
                        self.text = ""
                else:
                    self.Typeing_ = False
                    self.InputBegin_ = False
            
            if event.type == pygame.KEYDOWN and self.Typeing_:
                if event.key == pygame.K_RETURN:
                    # If Shift+Enter is pressed, add a newline so that during rendering the text is split into lines.
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Optionally, you could check if there is space for another line.
                        self.text += "\n"
                        self.wrap_text()
                    else:
                        # Otherwise, end typing mode on Enter.
                        self.Typeing_ = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.wrap_text()
                elif len(self.text) < self.char_limit:
                    self.text += event.unicode
                    self.wrap_text()

        # Call the on_typing callback (if any) while typing.
        if self.Typeing_ and self._on_typing:
            self._on_typing()

        # Call the input-ended callback when transitioning from typing to not typing.
        if prev_typing and not self.Typeing_ and self._on_input_ended:
            self._on_input_ended()

    # Decorator method to register a callback for typing activity.
    def Typeing(self, func):
        self._on_typing = func
        return func

    # Decorator method to register a callback for when input ends.
    def InputEnded(self, func):
        self._on_input_ended = func
        return func

    def get_text(self):
        # If you want the raw text with newline characters, you can simply return self.text.
        # The original version replaced "\n" with a space.
        return self.text

    def set_text(self, new_text):
        self.text = new_text[:self.char_limit]
        self.wrap_text()

class console:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.data = []  # Stores the lines of text to be displayed
        self.font = pygame.font.Font(None, 24)  # Default font
        self.scroll_offset = 0  # Keeps track of the current scroll position
        self.answer = ""  # Stores the input when using input() method
        self.input_received = False  # Indicates if input has been given
        self.last_scroll_event_time = 0
        self.scroll_event_interval = 0.2  # Interval in seconds to reduce scrolling sensitivity

    def tick(self, events, screen):
        # Handle scrolling with the mouse wheel
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_time = time.time()
                if event.button == 4:  # Scroll up
                    if current_time - self.last_scroll_event_time > self.scroll_event_interval:
                        self.scroll_offset = max(self.scroll_offset - 1, 0)
                        self.last_scroll_event_time = current_time
                elif event.button == 5:  # Scroll down
                    if current_time - self.last_scroll_event_time > self.scroll_event_interval:
                        self.scroll_offset = min(self.scroll_offset + 1, max(0, len(self.data) - self.rect.height // 24))
                        self.last_scroll_event_time = current_time
        
        # Drawing the console rectangle
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Displaying text
        visible_lines = self.rect.height // 24  # Number of lines that can fit in the console
        start_line = self.scroll_offset
        end_line = start_line + visible_lines

        for i, line in enumerate(self.data[start_line:end_line]):
            text_surface = self.font.render(line, True, (255, 255, 255))  # White color text
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5 + i * 24))

    def print(self, data):
        # Add a new line to the console
        self.data.append(str(data))
        # Adjust the scroll offset to always show the latest lines
        if len(self.data) > self.rect.height // 24:
            self.scroll_offset = len(self.data) - self.rect.height // 24

    def input(self, prompt, screen):
        # Display the prompt without a new line
        self.print(prompt)
        input_active = True
        current_input = ""

        while input_active:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.answer = current_input
                        self.input_received = True
                        self.print(prompt + current_input)  # Display the complete prompt and input
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        current_input = current_input[:-1]
                    else:
                        current_input += event.unicode

            # Display the current input
            self.tick(events, screen)
            text_surface = self.font.render(prompt + current_input, True, (255, 255, 255))
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5 + (len(self.data) - 1) * 24))
            pygame.display.flip()
