import pygame
import random
import sys
import math
from typing import List

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_SIZE = (1200, 900)  # Increased window size to accommodate larger board
SPACE_SIZE = 70  # Slightly smaller tiles to fit more
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "BLUE": (45, 156, 219),    # Food tiles
    "GREEN": (34, 139, 34),    # Daily tiles
    "YELLOW": (255, 184, 76),  # Special tiles
    "RED": (255, 105, 180),    # Star tiles
    "BACKGROUND": (240, 240, 240),
    "PRAYER": (255, 236, 214),  # Prayer tiles
    "BLACK_HOLE": (20, 20, 20)  # Dark color for black hole tiles
}

class BlessingCard:
    def __init__(self, question: str, options: List[str], correct_option: int, category: str):
        self.question = question
        self.options = options
        self.correct_option = correct_option
        self.category = category

class PowerUp:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

class Player:
    def __init__(self, name: str, number: int):
        self.name = name
        self.position = 0
        self.correct_answers = 0
        self.color = COLORS["BLACK"]
        self.number = number
        self.power_ups = []
        
    def add_power_up(self, power_up):
        self.power_ups.append(power_up)

class BerachotGame:
    def __init__(self):
        # Add try-except for pygame initialization
        try:
            pygame.init()
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Failed to initialize pygame: {e}")
            sys.exit(1)

        # Initialize in windowed mode
        self.fullscreen = False
        self.window_size = WINDOW_SIZE
        self.screen = pygame.display.set_mode(self.window_size)
        self.window_width, self.window_height = self.screen.get_size()
        pygame.display.set_caption("Berachot Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.players: List[Player] = []
        self.current_player = 0
        self.board_size = 56  # Changed from 36 to 56
        self.board_positions = []
        self.cards = self.initialize_cards()
        self.board = self.create_board()
        self.game_started = False

        # Try to load sound effects, but continue if files are missing
        try:
            self.roll_sound = pygame.mixer.Sound('sounds/dice_roll.wav')
            self.correct_sound = pygame.mixer.Sound('sounds/correct.wav')
            self.wrong_sound = pygame.mixer.Sound('sounds/wrong.wav')
            self.win_sound = pygame.mixer.Sound('sounds/win.wav')
            self.sound_enabled = True
            
            # Try to load and play background music
            try:
                pygame.mixer.music.load('sounds/background_music.mp3')
                pygame.mixer.music.play(-1)
            except:
                print("Background music file not found")
        except:
            print("Sound effects files not found - running without sound")
            self.sound_enabled = False

        self.question_history = {
            "Food": [],
            "Daily": [],
            "Special": [],
            }
        self.min_questions_before_repeat = 4  # Minimum questions before a repeat
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode using a more robust macOS compatible method."""
        try:
            # Store current window size before any changes
            current_size = self.screen.get_size()
            
            if self.fullscreen:
                # Switch to windowed mode
                self.screen = pygame.display.set_mode(
                    WINDOW_SIZE,  # Use original window size constant
                    pygame.RESIZABLE
                )
                self.fullscreen = False
            else:
                # Get current display info before switching
                display_info = pygame.display.Info()
                # Switch to fullscreen mode
                self.screen = pygame.display.set_mode(
                    (display_info.current_w, display_info.current_h),
                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                )
                self.fullscreen = True
            
            # Update window dimensions
            self.window_width, self.window_height = self.screen.get_size()
            
            # Force a complete redraw
            self.screen.fill(COLORS["BACKGROUND"])
            
            # Recalculate board positions
            self.board_positions = self.calculate_board_positions()
            
            # Redraw everything
            self.draw_board()
            self.draw_info_panel()
            pygame.display.flip()
            
            # Small delay to let the display settle
            pygame.time.wait(100)
            
        except pygame.error as e:
            print(f"Fullscreen toggle failed: {e}")
            # Fallback to windowed mode
            self.screen = pygame.display.set_mode(
                WINDOW_SIZE,
                pygame.RESIZABLE
            )
            self.fullscreen = False
            self.window_width, self.window_height = self.screen.get_size()
            self.board_positions = self.calculate_board_positions()

    def initialize_cards(self):
        cards = {
            "Food": [
                BlessingCard("What is the blessing for bread?",
                            ["Hamotzi", "Mezonot", "Shehakol", "Ha'adama"],
                            0, "Food"),
                BlessingCard("In what language should berachot ideally be recited?",
                            ["Any language is fine", 
                             "Hebrew if possible", 
                             "Only Hebrew", 
                             "Only Aramaic"], 
                            1, "Food"),
                BlessingCard("Which of the following is not a category under food blessings (Birchot Ha'nehenin)?",
                            ["Ha'Eitz", "Ha'Adamah", "Mezonot", "Ha'Mitvot"],
                            3, "Food"),
                BlessingCard("True or False: Birchot Ha'nehenin include blessings said over both food and fragrance.",
                            ["True", "False"],
                            0, "Food"),
                BlessingCard("How much must be eaten for a food to require a Bracha Rishona (first blessing)?",
                            ["A full meal", "A kizayit", "Any amount", "A half portion"],
                            2, "Food"),
                BlessingCard("What is the defining feature of a tree that requires the blessing Ha'Eitz?",
                            ["It bears citrus fruit", "It grows on vines", 
                             "It continues to produce from year to year", "It grows below ground"],
                            2, "Food"),
                BlessingCard("Which food category has the highest priority in halachic importance?",
                            ["HaEitz", "Mezonot", "HaMotzi", "HaAdamah"],
                            2, "Food"),
                # New questions from images
                BlessingCard("How much must be eaten for a food to require a Bracha Rishona?",
                            ["A full meal", "A kizayit", "Any amount", "A half portion"],
                            2, "Food"),
                BlessingCard("True or False: A kizayit is approximately 3.3-3.5 ounces.",
                            ["True", "False"],
                            1, "Food"),
                BlessingCard("True or False: If you prefer the taste of a HaAdamah food over a HaEitz food, HaAdamah comes first.",
                            ["True", "False"],
                            0, "Food"),
                BlessingCard("Which of the following is NOT one of the Shivat Haminim?",
                            ["Fig", "Pomegranate", "Apple", "Grapes"],
                            2, "Food"),
                BlessingCard("Mezonot is said over which foods?",
                            ["Fruits only", "Raw vegetables", "Cooked or baked grain-based items", "Dairy items"],
                            2, "Food"),
                BlessingCard("True or False: Noodles and cookies require the Mezonot blessing.",
                            ["True", "False"],
                            0, "Food"),
                BlessingCard("Which food requires a Shehakol blessing?",
                            ["Apple", "Watermelon (raw)", "Potato latkes", "Grape juice"],
                            2, "Food"),
                BlessingCard("Ha'Adamah is said when the source food _____ after producing fruit.",
                            ["grows", "dies", "changes", "ripens"],
                            1, "Food")
            ],
            "Daily": [
                BlessingCard("What is the first beracha we say in the morning?", ["Modeh Ani", "Shema", "Birkat Hamazon", "Asher Yatzar"], 0, "Daily"),
                BlessingCard("What is the beracha for seeing lightning?", ["Shehakol", "Oseh Ma'aseh Bereishit", "Ha'adama", "Hamotzi"], 1, "Daily"),
                BlessingCard("When do we say Birkat Hamazon?", ["Before eating", "After eating bread", "Before sleeping", "In the morning"], 1, "Daily"),
                BlessingCard("What blessing do we say after using the bathroom?", ["Modeh Ani", "Shema", "Asher Yatzar", "Al Netilat Yadayim"], 2, "Daily"),
                BlessingCard("When do we say the blessing for washing hands?", ["Before eating bread", "After eating", "Before sleeping", "After the bathroom"], 0, "Daily"),
                BlessingCard("What blessing do we say before studying Torah?", ["Shema", "La'asok B'divrei Torah", "Ahavat Olam", "Emet V'yatziv"], 1, "Daily"),
                BlessingCard("When do we say the Shema?", ["Morning and evening", "Afternoon only", "Morning only", "Evening only"], 0, "Daily"),
                BlessingCard("What blessing do we say on candles before Shabbat?", ["Borei Pri Hagafen", "L'hadlik Ner", "Hamotzi", "Shehecheyanu"], 1, "Daily"),
                BlessingCard("Why do we say Asher Yatzar after using the bathroom?",
                            ["Because our body works with wondrous wisdom",
                             "It's just tradition",
                             "To be polite",
                             "No special reason"],
                            0, "Daily"),
                BlessingCard("True or False: Only Birkat Hamazon is considered a Torah blessing by most authorities?",
                            ["True", "False"], 
                            0, "Daily"),
                BlessingCard("How many berachot should one try to say daily?",
                            ["50", "75", "100", "150"], 
                            2, "Daily"),
                BlessingCard("Complete the phrase: 'rofey _____ kol basar'",
                            ["cholay", "cholim", "choleh", "cholot"], 
                            0, "Daily"),
                BlessingCard("According to most authorities, only which blessing is a Torah commandment?",
                            ["Birkat HaMazon", "Asher Yatzar", "HaMotzi", "Mezonot"],
                            0, "Daily"),
                BlessingCard("When should berachot generally be recited?",
                            ["After enjoying something", "During the act", 
                             "Over lesiyatan – before receiving benefit", "Only on holidays"],
                            2, "Daily"),
                BlessingCard("Why did King David institute the recitation of 100 blessings daily?",
                            ["People weren't praying", "It was commanded in the Torah",
                             "People were dying without explanation", "There were 100 prophets"],
                            2, "Daily"),
                BlessingCard("What should you do if you begin a blessing but realize you have no food after saying Ado-noy?",
                            ["Stop and say Baruch Shem", "Wait and then eat",
                             "End with lamdeni chukecha", "Continue the blessing anyway"],
                            2, "Daily"),
                BlessingCard("True or False: You may say a blessing even if the food or water is not yet present.",
                            ["True", "False"],
                            1, "Daily"),
                BlessingCard("If one realizes after saying 'Elokainu' that they have no food, they should say:",
                            ["Nothing", "Baruch Shem Kevod Malchuto Leolam Vaed",
                             "Start over", "Continue anyway"],
                            1, "Daily"),
                BlessingCard("When should a person recite the Asher Yatzar blessing?",
                            ["After waking up", "After eating", "After leaving the bathroom", "Before sleeping"],
                            2, "Daily"),
                BlessingCard("True or False: The blessing Asher Yatzar refers to how the human body functions with wisdom.",
                            ["True", "False"],
                            0, "Daily"),
                BlessingCard("True or False: After saying 'Elokainu' in error, you can continue with the blessing if you get food.",
                            ["True", "False"],
                            1, "Daily")
            ],
            "Special": [
                BlessingCard("What is the beracha for a new fruit?", ["Shehecheyanu", "Borei Pri Ha'etz", "Shehakol", "Hamotzi"], 0, "Special"),
                BlessingCard("What is the beracha for hearing thunder?", ["Shehakol", "Oseh Ma'aseh Bereishit", "Shehecheyanu", "Hamotzi"], 1, "Special"),
                BlessingCard("What blessing do we say on Chanukah candles?", ["L'hadlik Ner", "Shehecheyanu", "Both A and B", "Neither"], 2, "Special"),
                BlessingCard("When do we say Shehecheyanu?", ["On new things", "Every morning", "Before eating", "Before sleeping"], 0, "Special"),
                BlessingCard("What blessing do we say when seeing a rainbow?", ["Oseh Ma'aseh Bereishit", "Zocher HaBrit", "Shehecheyanu", "None"], 1, "Special"),
                BlessingCard("What blessing do we say on seeing the ocean?", ["Shehecheyanu", "Oseh Ma'aseh Bereishit", "Zocher HaBrit", "None"], 1, "Special"),
                BlessingCard("What blessing do we say on Rosh Hashanah apples?", ["Borei Pri Ha'etz", "Shehecheyanu", "Both A and B", "Neither"], 2, "Special"),
                BlessingCard("What blessing do we say at a wedding?", ["Shehecheyanu", "Asher Bara", "Both A and B", "Neither"], 1, "Special"),
                BlessingCard("When should berachot generally be recited?",
                            ["After the action", 
                             "Before the action (over lesiyatan)", 
                             "During the action",
                             "Anytime"], 
                            1, "Special"),
                BlessingCard("Who benefits from saying a beracha?",
                            ["G-d", "The person saying it", "Both", "Neither"], 
                            1, "Special"),
                BlessingCard("Why do we recite berachot?",
                            ["To thank G-d actively",
                             "Because we have to",
                             "To make noise",
                             "No reason"], 
                            0, "Special"),
                BlessingCard("True or False: A person should say berachot by rote without thinking of their meaning",
                            ["True", "False"], 
                            1, "Special"),
                BlessingCard("The word beracha comes from braycha, which means:",
                            ["River", "Spring", "Blessing", "Prayer"],
                            1, "Special"),
                BlessingCard("True or False: God receives benefit from our blessings.",
                            ["True", "False"],
                            1, "Special"),
                BlessingCard("Why do we recite berachot?",
                            ["To earn reward", "To fulfill obligation",
                             "To recognize and thank Hashem", "To announce holiness"],
                            2, "Special"),
                BlessingCard("True or False: You may say a blessing even if the food or water is not yet present.",
                            ["True", "False"],
                            1, "Special"),
                BlessingCard("If you say Shehakol by mistake on any food, what should you do?",
                            ["Always redo the blessing", "Continue eating - it's valid",
                             "Say Baruch Shem", "Ask a rabbi"],
                            1, "Special"),
                BlessingCard("Match the type of bracha: What requires Birchot Ha'nehenin?",
                            ["Shofar", "Shmoneh Esrai", "Food", "Prayer"],
                            2, "Special"),
                BlessingCard("True or False: According to most authorities, only Birkat Ha'mazon is a Torah commandment.",
                            ["True", "False"],
                            0, "Special"),
                BlessingCard("Why did King David institute 100 blessings daily?",
                            ["People weren't praying", "Torah commanded it",
                             "People were dying unexplainedly", "There were 100 prophets"],
                            2, "Special"),
                BlessingCard("True or False: If Hashem stopped providing sustenance, all blessings would continue regardless.",
                            ["True", "False"],
                            1, "Special"),
                BlessingCard("The word 'beracha' comes from 'braycha,' which means:",
                            ["River", "Spring", "Blessing", "Prayer"],
                            1, "Special"),
                BlessingCard("True or False: The phrase 'Baruch Atah' means 'You are the source of all blessings.'",
                            ["True", "False"],
                            0, "Special"),
                BlessingCard("This recognition [of blessings] is strictly for _____, not for Hashem.",
                            ["us", "them", "angels", "creation"],
                            0, "Special"),
                BlessingCard("True or False: Hashem's involvement stops after the food has grown.",
                            ["True", "False"],
                            1, "Special")
            ]
        }
        return cards

    def create_board(self):
        # First verify board_size is correctly set
        if self.board_size != 56:
            raise ValueError(f"Board size must be 56, got {self.board_size}")
            
        # Define the pattern of tiles ensuring exactly 56 tiles
        tile_types = [
            "START",  # 1
            # Column 1 (7 tiles)
            "Daily", "Food", "Special", "Black_Hole", "Star", "Daily", "Food",
            # Column 2 (7 tiles)
            "Special", "Star", "Food", "Daily", "Prayer", "Black_Hole", "Star",
            # Column 3 (7 tiles)
            "Food", "Daily", "Black_Hole", "Special", "Star", "Food", "Daily",
            # Column 4 (7 tiles)
            "Prayer", "Special", "Star", "Black_Hole", "Daily", "Prayer", "Special",
            # Column 5 (7 tiles)
            "Star", "Food", "Daily", "Prayer", "Black_Hole", "Star", "Food",
            # Column 6 (7 tiles)
            "Daily", "Prayer", "Special", "Star", "Food", "Black_Hole", "Prayer",
            # Column 7 (7 tiles)
            "Special", "Star", "Food", "Daily", "Prayer", "Special", "Star",
            # Column 8 (6 tiles to make total of 56)
            "Prayer", "Daily", "Special", "Food", "Star", "END"
        ]
        
        # Debug print to verify count
        print(f"Number of tiles: {len(tile_types)}")
        
        # Verify tile count before creating board
        if len(tile_types) != self.board_size:
            raise ValueError(f"Tile count mismatch: expected {self.board_size}, got {len(tile_types)}")
        
        return tile_types

    def calculate_board_positions(self):
        positions = []
        # Calculate margins based on screen size
        margin_x = self.window_width * 0.1
        margin_y = self.window_height * 0.8
        spacing = min(self.window_width * 0.06, self.window_height * 0.08)  # Dynamic spacing
        
        columns = 8
        rows = 7
        
        # Calculate positions column by column with screen size adjustments
        for col in range(columns):
            row_positions = range(rows) if col % 2 == 0 else range(rows-1, -1, -1)
            for row in row_positions:
                x = margin_x + (col * (spacing + self.window_width * 0.02))
                y = margin_y - (row * spacing)
                positions.append((int(x), int(y)))
        
        return positions

    def start_screen(self):
        while True:
            self.screen.fill(COLORS["BACKGROUND"])
            
            # Draw title
            title_text = self.font.render("Berachot Game", True, COLORS["BLACK"])
            title_rect = title_text.get_rect(center=(self.window_width // 2, 100))
            self.screen.blit(title_text, title_rect)

            # Draw begin button
            start_button = pygame.Rect(self.window_width // 2 - 50, 300, 100, 50)
            pygame.draw.rect(self.screen, COLORS["BLUE"], start_button)
            start_text = self.font.render("Begin", True, COLORS["WHITE"])
            start_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_rect)

            # Add exit instructions
            exit_text = self.font.render("Press ESC to exit", True, COLORS["BLACK"])
            exit_rect = exit_text.get_rect(center=(self.window_width // 2, 500))
            self.screen.blit(exit_text, exit_rect)

            # Add fullscreen instructions
            fullscreen_text = self.font.render("Press F to toggle fullscreen", True, COLORS["BLACK"])
            fullscreen_rect = fullscreen_text.get_rect(center=(self.window_width // 2, 450))
            self.screen.blit(fullscreen_text, fullscreen_rect)

            pygame.display.flip()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_f:  # Changed from F11 to F key
                        self.toggle_fullscreen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        return True

            self.clock.tick(60)
        return False

    def setup_players(self):
        running = True
        num_players = 2
        players_confirmed = False
        player_names = []
        current_name = ""
        
        while running:
            self.screen.fill(COLORS["BACKGROUND"])
            
            if not players_confirmed:
                # Draw player count selection
                title_text = self.font.render("Select Number of Players", True, COLORS["BLACK"])
                title_rect = title_text.get_rect(center=(self.window_width // 2, 100))
                self.screen.blit(title_text, title_rect)
                
                # Increase size and visibility of player count
                player_count_font = pygame.font.Font(None, 48)  # Larger font
                text = player_count_font.render(f"{num_players} Players", True, COLORS["BLUE"])
                text_rect = text.get_rect(center=(self.window_width // 2, 200))
                self.screen.blit(text, text_rect)
                
                # Add increment/decrement buttons
                inc_button = pygame.Rect(self.window_width // 2 + 100, 190, 30, 30)
                dec_button = pygame.Rect(self.window_width // 2 - 130, 190, 30, 30)
                pygame.draw.rect(self.screen, COLORS["BLUE"], inc_button)
                pygame.draw.rect(self.screen, COLORS["BLUE"], dec_button)
                
                # Draw + and - symbols
                plus = self.font.render("+", True, COLORS["WHITE"])
                minus = self.font.render("-", True, COLORS["WHITE"])
                self.screen.blit(plus, (inc_button.centerx - 5, inc_button.centery - 10))
                self.screen.blit(minus, (dec_button.centerx - 5, dec_button.centery - 10))
                
                # Add confirm button
                confirm_button = pygame.Rect(self.window_width // 2 - 60, 300, 120, 40)
                pygame.draw.rect(self.screen, COLORS["GREEN"], confirm_button)
                confirm_text = self.font.render("Confirm", True, COLORS["WHITE"])
                confirm_rect = confirm_text.get_rect(center=confirm_button.center)
                self.screen.blit(confirm_text, confirm_rect)
            else:
                # Player name input screen
                title_text = self.font.render(f"Enter Player {len(player_names) + 1} Name", True, COLORS["BLACK"])
                title_rect = title_text.get_rect(center=(self.window_width // 2, 100))
                self.screen.blit(title_text, title_rect)
                
                # Display current name being typed
                name_text = self.font.render(current_name + "|", True, COLORS["BLACK"])
                name_rect = name_text.get_rect(center=(self.window_width // 2, 200))
                self.screen.blit(name_text, name_rect)
                
                # Add confirm name button if name is not empty
                if current_name:
                    confirm_name_button = pygame.Rect(self.window_width // 2 - 60, 300, 120, 40)
                    pygame.draw.rect(self.screen, COLORS["GREEN"], confirm_name_button)
                    confirm_text = self.font.render("Next", True, COLORS["WHITE"])
                    confirm_rect = confirm_text.get_rect(center=confirm_name_button.center)
                    self.screen.blit(confirm_text, confirm_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_f:  # Changed from F11 to F key
                        self.toggle_fullscreen()
                    elif players_confirmed:
                        if event.key == pygame.K_RETURN and current_name:
                            player_names.append(current_name)
                            current_name = ""
                            if len(player_names) == num_players:
                                # Create players and return
                                for i, name in enumerate(player_names):
                                    self.players.append(Player(name, i + 1))
                                return
                        elif event.key == pygame.K_BACKSPACE:
                            current_name = current_name[:-1]
                        else:
                            # Add character to name if it's a valid key
                            if event.unicode.isalnum() or event.unicode.isspace():
                                current_name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not players_confirmed:
                        if inc_button.collidepoint(event.pos):
                            num_players = min(num_players + 1, 4)  # Changed from 6 to 4
                        elif dec_button.collidepoint(event.pos):
                            num_players = max(num_players - 1, 2)
                        elif confirm_button.collidepoint(event.pos):
                            players_confirmed = True
                    else:
                        if current_name and confirm_name_button.collidepoint(event.pos):
                            player_names.append(current_name)
                            current_name = ""
                            if len(player_names) == num_players:
                                # Create players and return
                                for i, name in enumerate(player_names):
                                    self.players.append(Player(name, i + 1))
                                return

            self.clock.tick(60)

    def run_game(self):
        self.start_screen()
        self.setup_players()
        self.board_positions = self.calculate_board_positions()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_turn()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_f:  # Changed from F11 to F key
                        self.toggle_fullscreen()
                        # Redraw everything
                        self.draw_board()
                        self.draw_info_panel()

            self.draw_board()
            self.draw_info_panel()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def draw_board(self):
        self.screen.fill(COLORS["BACKGROUND"])
        
        # Draw decorative background pattern
        for i in range(0, self.window_width, 50):
            for j in range(0, self.window_height, 50):
                pygame.draw.circle(self.screen, (*COLORS["BACKGROUND"], 50), 
                                 (i, j), 3)
        
        # Draw connecting lines between tiles with gradient effect
        for i in range(len(self.board_positions) - 1):
            start_pos = (self.board_positions[i][0] + SPACE_SIZE//2, 
                        self.board_positions[i][1] + SPACE_SIZE//2)
            end_pos = (self.board_positions[i + 1][0] + SPACE_SIZE//2, 
                      self.board_positions[i + 1][1] + SPACE_SIZE//2)
            pygame.draw.line(self.screen, COLORS["BLACK"], start_pos, end_pos, 3)
            # Add decorative dots along the path
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            pygame.draw.circle(self.screen, COLORS["BLACK"], (mid_x, mid_y), 4)
        
        # Draw tiles with decorative borders
        for i, pos in enumerate(self.board_positions):
            # Draw tile shadow
            shadow_rect = pygame.Rect(pos[0] + 3, pos[1] + 3, SPACE_SIZE - 5, SPACE_SIZE - 5)
            pygame.draw.rect(self.screen, (*COLORS["BLACK"], 128), shadow_rect)
            
            # Draw main tile with special pattern for Black Hole
            color = self._get_tile_color(i)
            tile_rect = pygame.Rect(pos[0], pos[1], SPACE_SIZE - 5, SPACE_SIZE - 5)
            
            if self.board[i] == "Black_Hole":
                # Draw base white background and stripes
                pygame.draw.rect(self.screen, COLORS["WHITE"], tile_rect)
                
                # Draw diagonal stripes contained within tile
                stripe_spacing = 10
                stripe_width = 4
                num_stripes = int((SPACE_SIZE * 2) / stripe_spacing) + 2
                
                for n in range(-num_stripes, num_stripes):
                    start_x = pos[0] - SPACE_SIZE + (n * stripe_spacing)
                    start_y = pos[1]
                    end_x = start_x + SPACE_SIZE
                    end_y = pos[1] + SPACE_SIZE - 5
                    
                    # Clip lines to tile boundaries
                    if start_x < pos[0]:
                        start_y = pos[1] + (pos[0] - start_x)
                        start_x = pos[0]
                    if end_x > pos[0] + SPACE_SIZE - 5:
                        end_y = pos[1] + SPACE_SIZE - 5 - (end_x - (pos[0] + SPACE_SIZE - 5))
                        end_x = pos[0] + SPACE_SIZE - 5
                        
                    if start_y <= end_y:
                        pygame.draw.line(self.screen, COLORS["BLACK_HOLE"],
                                       (start_x, start_y),
                                       (end_x, end_y),
                                       stripe_width)
                
                # Draw border
                pygame.draw.rect(self.screen, COLORS["BLACK"], tile_rect, 2)
                
            else:
                pygame.draw.rect(self.screen, color, tile_rect)
                pygame.draw.rect(self.screen, COLORS["BLACK"], tile_rect, 2)

            # Draw tile numbers (moved outside the if/else block)
            number_font = pygame.font.Font(None, 32 if self.board[i] == "Black_Hole" else 24)
            number_color = COLORS["YELLOW"] if self.board[i] == "Black_Hole" else COLORS["BLACK"]
            number_text = number_font.render(str(i + 1), True, number_color)
            number_rect = number_text.get_rect(topleft=(pos[0] + 5, pos[1] + 5))
            self.screen.blit(number_text, number_rect)
            
            # Draw tile type indicators
            if i == 0:
                text = "START"
            elif i == self.board_size - 1:
                text = "END"
            else:
                text = {
                    "Food": "F",
                    "Daily": "D",
                    "Special": "S",
                    "Star": "★",
                    "Prayer": "P",
                    "Black_Hole": "⚫",
                }.get(self.board[i], "")
            
            # Draw tile type text
            type_font = pygame.font.Font(None, 28)
            type_text = type_font.render(text, True, COLORS["BLACK"])
            type_rect = type_text.get_rect(center=(pos[0] + SPACE_SIZE//2, pos[1] + SPACE_SIZE//2))
            self.screen.blit(type_text, type_rect)
            
            # Add small colored indicator in corner for card types
            if self.board[i] in ["Food", "Daily", "Special"]:
                indicator_size = 15
                pygame.draw.rect(self.screen, 
                               self._get_tile_color(i),
                               (pos[0] + SPACE_SIZE - indicator_size - 5,
                                pos[1] + 5,
                                indicator_size,
                                indicator_size))

            # Draw players on the tile with spacing
            players_on_tile = [p for p in self.players if p.position == i]
            for idx, player in enumerate(players_on_tile):
                row = idx // 3
                col = idx % 3
                player_x = pos[0] + 20 + (col * 25)
                player_y = pos[1] + 35 + (row * 25)
                
                # Draw player circle
                pygame.draw.circle(self.screen, player.color, (player_x, player_y), 12)
                
                # Draw player number
                player_num = str(player.number)
                number_font = pygame.font.Font(None, 24)
                player_text = number_font.render(player_num, True, COLORS["WHITE"])
                text_rect = player_text.get_rect(center=(player_x, player_y))
                self.screen.blit(player_text, text_rect)

            # Add special tile indicators
            tile_type = self.board[i]
            if tile_type == "Star":
                # Draw star power-up indicator centered in bottom half of tile
                star_color = COLORS["RED"]
                star_size = 12
                # Calculate position for center of tile
                star_center_x = pos[0] + SPACE_SIZE//2
                star_center_y = pos[1] + (SPACE_SIZE * 3//4)  # Place in bottom half
                
                # Draw star shape
                points = [
                    (star_center_x, star_center_y - star_size),  # Top
                    (star_center_x + star_size//2, star_center_y + star_size//2),  # Bottom right
                    (star_center_x - star_size, star_center_y),  # Left
                    (star_center_x + star_size, star_center_y),  # Right
                    (star_center_x - star_size//2, star_center_y + star_size//2)   # Bottom left
                ]
                pygame.draw.polygon(self.screen, star_color, points)
            
            elif tile_type == "Prayer":
                # Draw prayer power-up indicator centered in bottom half of tile
                prayer_color = COLORS["PRAYER"]
                prayer_center_x = pos[0] + SPACE_SIZE//2
                prayer_center_y = pos[1] + (SPACE_SIZE * 3//4)  # Place in bottom half
                
                pygame.draw.circle(self.screen, prayer_color,
                                 (prayer_center_x, prayer_center_y), 6)
                pygame.draw.circle(self.screen, COLORS["BLACK"],
                                 (prayer_center_x, prayer_center_y), 6, 1)

    def _get_tile_color(self, index):
        tile_type = self.board[index]
        return {
            "Food": COLORS["BLUE"],      # Food questions
            "Daily": COLORS["GREEN"],    # Daily blessings
            "Special": COLORS["YELLOW"], # Special occasions
            "Star": COLORS["RED"],       # Power-up tile
            "Prayer": COLORS["PRAYER"],  # Prayer tile
            "START": COLORS["WHITE"],
            "END": COLORS["WHITE"],
            "Black_Hole": COLORS["BLACK_HOLE"],
        }.get(tile_type, COLORS["WHITE"])

    def draw_info_panel(self):
        current = self.players[self.current_player]
        text = f"Current Player: {current.name}"
        text_surface = self.font.render(text, True, COLORS["BLACK"])
        self.screen.blit(text_surface, (50, 50))

    def handle_turn(self):
        current = self.players[self.current_player]
        
        # Draw the board first
        self.draw_board()
        self.draw_info_panel()
        
        # Add a "Roll Dice" button
        roll_button = pygame.Rect(self.window_width - 150, 100, 100, 40)
        pygame.draw.rect(self.screen, COLORS["BLUE"], roll_button)
        roll_text = self.font.render("Roll", True, COLORS["WHITE"])
        roll_rect = roll_text.get_rect(center=roll_button.center)
        self.screen.blit(roll_text, roll_rect)
        pygame.display.flip()

        # Wait for roll
        waiting_for_roll = True
        while waiting_for_roll:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if roll_button.collidepoint(event.pos):
                        old_position = current.position
                        roll = random.randint(1, 6)
                        self._show_dice_roll(roll)
                        
                        # Move player
                        new_position = min(old_position + roll, self.board_size - 1)
                        self._animate_player_movement(current, old_position, new_position)
                        current.position = new_position

                        # Handle tile effects based on where player landed
                        tile_type = self.board[new_position]
                        
                        if tile_type in ["Food", "Daily", "Special"]:
                            # Get and ask a question
                            card = self.get_next_question(tile_type)
                            if self.ask_question(card):
                                current.correct_answers += 1
                            else:
                                move_back = random.randint(1, 3)
                                self._show_move_back_message(move_back)
                                new_position = max(0, new_position - move_back)
                                self._animate_player_movement(current, current.position, new_position)
                                current.position = new_position
                        elif tile_type == "Black_Hole":
                            self._show_black_hole_effect()
                            new_position = self._find_previous_black_hole(new_position)
                            self._animate_player_movement(current, current.position, new_position)
                            current.position = new_position
                        elif tile_type == "Prayer":
                            category = self.handle_tile_effect(tile_type, current)
                            if category:
                                # Get and ask a question from chosen category
                                card = self.get_next_question(category)
                                if self.ask_question(card):
                                    current.correct_answers += 1
                                    # Add bonus move for correct answer on prayer tile
                                    bonus_move = 2
                                    new_position = min(current.position + bonus_move, self.board_size - 1)
                                    self._show_special_effect(f"Correct! Move forward {bonus_move} spaces!")
                                    self._animate_player_movement(current, current.position, new_position)
                                    current.position = new_position
                                else:
                                    self._show_move_back_message(1)
                                    new_position = max(0, current.position - 1)
                                    self._animate_player_movement(current, current.position, new_position)
                                    current.position = new_position
                        else:
                            effect = self.handle_tile_effect(tile_type, current)
                            if effect:
                                new_position = min(current.position + effect, self.board_size - 1)
                                self._animate_player_movement(current, current.position, new_position)
                                current.position = new_position

                        waiting_for_roll = False

        # Check for winner
        if current.position == self.board_size - 1:
            self.display_winner(current)
            return

        # Move to next player
        self.current_player = (self.current_player + 1) % len(self.players)
        
        # Show whose turn is next
        self._show_next_player()
        
        # Redraw board for next player
        self.draw_board()
        self.draw_info_panel()
        pygame.display.flip()

    def _show_next_player(self):
        self.screen.fill(COLORS["BACKGROUND"])
        next_player = self.players[self.current_player]
        
        # Create fade-in effect
        for alpha in range(0, 255, 5):
            self.screen.fill(COLORS["BACKGROUND"])
            
            # Draw player name with increasing opacity
            text_surface = self.font.render(f"{next_player.name}'s Turn", True, COLORS["BLACK"])
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(self.window_width//2, self.window_height//2))
            self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            pygame.time.wait(10)
        
        pygame.time.wait(1000)  # Show final message for 1 second

    def _show_dice_roll(self, roll):
        if hasattr(self, 'sound_enabled') and self.sound_enabled:
            self.roll_sound.play()
        
        # Show dice animation
        for _ in range(10):  # Quick animation
            temp_roll = random.randint(1, 6)
            self.screen.fill(COLORS["BACKGROUND"])
            roll_text = self.font.render(f"Rolling... {temp_roll}", True, COLORS["BLACK"])
            text_rect = roll_text.get_rect(center=(self.window_width//2, self.window_height//2))
            self.screen.blit(roll_text, text_rect)
            pygame.display.flip()
            pygame.time.wait(50)
        
        # Show final roll
        self.screen.fill(COLORS["BACKGROUND"])
        roll_text = self.font.render(f"You rolled a {roll}!", True, COLORS["BLACK"])
        text_rect = roll_text.get_rect(center=(self.window_width//2, self.window_height//2))
        self.screen.blit(roll_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)

    def ask_question(self, card: BlessingCard):
        running = True
        answer_given = False
        
        # Calculate the maximum width needed for options
        max_width = 0
        option_surfaces = []
        for option in card.options:
            option_text = self.font.render(f"{len(option_surfaces) + 1}. {option}", True, COLORS["WHITE"])
            option_surfaces.append(option_text)
            max_width = max(max_width, option_text.get_width())
        
        # Add padding to the width
        button_width = max_width + 40  # Add 40 pixels padding
        button_height = 50  # Increased height for better visibility
        
        while running and not answer_given:
            self.screen.fill(COLORS["BACKGROUND"])
            
            # Display question - wrap text if too long
            words = card.question.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.font.render(test_line, True, COLORS["BLACK"])
                if test_surface.get_width() < self.window_width - 100:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))
            
            # Draw wrapped question text
            question_y = 100
            for line in lines:
                question_text = self.font.render(line, True, COLORS["BLACK"])
                question_rect = question_text.get_rect(midleft=(50, question_y))
                self.screen.blit(question_text, question_rect)
                question_y += 40

            # Create clickable option buttons
            option_buttons = []
            button_x = (self.window_width - button_width) // 2  # Center buttons horizontally
            start_y = question_y + 20  # Start buttons below question
            
            for i, option_surface in enumerate(option_surfaces):
                button_rect = pygame.Rect(button_x, start_y + i * (button_height + 10), 
                                        button_width, button_height)
                option_buttons.append(button_rect)
                
                # Draw button background
                pygame.draw.rect(self.screen, COLORS["BLUE"], button_rect)
                # Draw button text centered in button
                text_rect = option_surface.get_rect(center=button_rect.center)
                self.screen.blit(option_surface, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, button in enumerate(option_buttons):
                        if button.collidepoint(event.pos):
                            correct = i == card.correct_option
                            self._show_result(
                                "Correct!" if correct else "Incorrect!", 
                                COLORS["GREEN"] if correct else COLORS["RED"]
                            )
                            answer_given = True
                            return correct
                elif event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_4:
                        answer = event.key - pygame.K_1
                        if answer < len(card.options):
                            correct = answer == card.correct_option
                            self._show_result(
                                "Correct!" if correct else "Incorrect!", 
                                COLORS["GREEN"] if correct else COLORS["RED"]
                            )
                            answer_given = True
                            return correct

            self.clock.tick(60)
        return False

    def _show_result(self, text, color):
        if hasattr(self, 'sound_enabled') and self.sound_enabled:
            if "Correct" in text:
                self.correct_sound.play()
            else:
                self.wrong_sound.play()
        # Display result for 2 seconds
        self.screen.fill(COLORS["BACKGROUND"])
        result_text = self.font.render(text, True, color)
        text_rect = result_text.get_rect(center=(self.window_width//2, self.window_height//2))
        self.screen.blit(result_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    def display_winner(self, winner: Player):
        if hasattr(self, 'sound_enabled') and self.sound_enabled:
            self.win_sound.play()
        
        victory_screen = True
        while victory_screen:
            self.screen.fill(COLORS["BACKGROUND"])
            
            # Draw victory message
            title_font = pygame.font.Font(None, 64)
            winner_text = title_font.render(f"{winner.name} Wins!", True, COLORS["BLUE"])
            text_rect = winner_text.get_rect(center=(self.window_width//2, self.window_height//2))
            self.screen.blit(winner_text, text_rect)
            
            # Draw stats
            stats_font = pygame.font.Font(None, 32)
            stats_text = stats_font.render(
                f"Correct Answers: {winner.correct_answers}", 
                True, 
                COLORS["BLACK"]
            )
            stats_rect = stats_text.get_rect(center=(self.window_width//2, self.window_height//2 + 50))
            self.screen.blit(stats_text, stats_rect)
            
            # Draw exit instruction
            exit_text = self.font.render("Press any key to exit", True, COLORS["BLACK"])
            exit_rect = exit_text.get_rect(center=(self.window_width//2, self.window_height//2 + 100))
            self.screen.blit(exit_text, exit_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    victory_screen = False
                elif event.type == pygame.KEYDOWN:
                    victory_screen = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    victory_screen = False
        
        pygame.quit()
        sys.exit()

    def _show_move_back_message(self, spaces):
        self.screen.fill(COLORS["BACKGROUND"])
        message = f"Wrong answer! Moving back {spaces} spaces"
        text = self.font.render(message, True, COLORS["RED"])
        text_rect = text.get_rect(center=(self.window_width//2, self.window_height//2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    def handle_tile_effect(self, tile_type, player):
        if tile_type == "Star":
            # Bonus move on correct answer
            return self._handle_star_tile(player)
        elif tile_type == "Prayer":
            # Choose category for next turn
            return self._handle_prayer_tile(player)
    
    def _handle_star_tile(self, player):
        # Show special star effect
        self._show_special_effect("★ Bonus Move Available! ★")
        if self.ask_question(random.choice(self.cards[random.choice(list(self.cards.keys()))])):
            bonus = random.randint(1, 3)
            self._show_special_effect(f"Move forward {bonus} spaces!")
            return bonus
        return 0

    def _handle_prayer_tile(self, player):
        """Handle landing on a Prayer tile."""
        self._show_special_effect("Prayer Tile - Choose Category")
        categories = ["Food", "Daily", "Special"]
        
        # Draw category selection buttons
        button_height = 50
        button_spacing = 20
        total_height = (button_height + button_spacing) * len(categories)
        start_y = (self.window_height - total_height) // 2
        
        buttons = []
        for i, category in enumerate(categories):
            button_rect = pygame.Rect(
                self.window_width // 4,
                start_y + i * (button_height + button_spacing),
                self.window_width // 2,
                button_height
            )
            buttons.append((button_rect, category))
        
        # Handle category selection
        running = True
        while running:
            self.screen.fill(COLORS["BACKGROUND"])
            
            for button, category in buttons:
                pygame.draw.rect(self.screen, COLORS["BLUE"], button)
                text = self.font.render(category, True, COLORS["WHITE"])
                text_rect = text.get_rect(center=button.center)
                self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button, category in buttons:
                        if button.collidepoint(event.pos):
                            return category
        
        return random.choice(categories)  # Fallback

    def _show_special_effect(self, text):
        self.screen.fill(COLORS["BACKGROUND"])
        # Create pulsing text effect
        for size in range(32, 48, 2):
            effect_font = pygame.font.Font(None, size)
            effect_text = effect_font.render(text, True, COLORS["YELLOW"])
            text_rect = effect_text.get_rect(center=(self.window_width//2, self.window_height//2))
            
            self.screen.fill(COLORS["BACKGROUND"])
            self.screen.blit(effect_text, text_rect)
            pygame.display.flip()
            pygame.time.wait(50)
        
        pygame.time.wait(1000)

    def _animate_player_movement(self, player, old_pos, new_pos):
        if old_pos == new_pos:
            return
            
        # Ensure positions are within valid range
        old_pos = max(0, min(old_pos, self.board_size - 1))
        new_pos = max(0, min(new_pos, self.board_size - 1))
        
        # Calculate all positions between old and new
        direction = 1 if new_pos > old_pos else -1
        positions = range(old_pos, new_pos + direction, direction)
        
        for pos in positions:
            player.position = pos
            # Flash the tile being moved to
            if 0 <= pos < len(self.board_positions):
                self._highlight_tile(self.board_positions[pos])
                self.draw_board()
                pygame.display.flip()
                pygame.time.wait(300)  # Slow down animation

    def _highlight_tile(self, pos):
        highlight = pygame.Surface((SPACE_SIZE, SPACE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (*COLORS["YELLOW"], 128),
                        (0, 0, SPACE_SIZE, SPACE_SIZE))
        self.screen.blit(highlight, pos)

    def get_next_question(self, category):
        """Get next question avoiding recent repeats."""
        available_questions = []
        all_questions = self.cards[category]
        
        # Get questions that haven't been used recently
        for i, question in enumerate(all_questions):
            if i not in self.question_history[category]:
                available_questions.append((i, question))
        
        # If running low on questions, clear older history
        if len(available_questions) < 3:  # Changed threshold
            self.question_history[category] = self.question_history[category][
                -min(len(all_questions) // 2, self.min_questions_before_repeat):]
            # Rebuild available questions
            available_questions = [(i, q) for i, q in enumerate(all_questions)
                                 if i not in self.question_history[category]]
        
        # Select random question
        index, question = random.choice(available_questions)
        self.question_history[category].append(index)
        
        return question

    def _find_previous_black_hole(self, current_pos):
        """Find the position of the previous black hole tile."""
        # Look for previous black hole
        for pos in range(current_pos - 1, -1, -1):
            if self.board[pos] == "Black_Hole":
                return pos
                
        # If no previous black hole found (we're at first black hole), return START
        return 0  # Send player back to START if at first black hole

    def _show_black_hole_effect(self):
        """Display black hole effect animation."""
        self.screen.fill(COLORS["BACKGROUND"])
        text = "Black Hole! Moving back..."
        
        # Create swirl effect
        center_x, center_y = self.window_width // 2, self.window_height // 2
        for radius in range(100, 0, -5):
            self.screen.fill(COLORS["BACKGROUND"])
            pygame.draw.circle(self.screen, COLORS["BLACK_HOLE"], 
                             (center_x, center_y), radius)
            
            if radius < 50:
                effect_text = self.font.render(text, True, COLORS["WHITE"])
                text_rect = effect_text.get_rect(center=(center_x, center_y))
                self.screen.blit(effect_text, text_rect)
            
            pygame.display.flip()
            pygame.time.wait(50)
        
        pygame.time.wait(1000)


if __name__ == "__main__":
    game = BerachotGame()
    game.run_game( )
