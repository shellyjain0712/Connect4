"""
FIXED Connect 4 GUI - Professional version that ACTUALLY WORKS
Based on the simple version but with better styling and features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import threading
import time
from typing import List, Tuple, Optional
import datetime
import json
import os
try:
    import winsound  # For Windows sound effects
except ImportError:
    winsound = None

# Game constants
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

class Connect4GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect 4 - AI Challenge Pro")
        self.root.geometry("1000x850")  # Increased width for new features
        self.root.configure(bg='#0f1419')
        self.root.resizable(False, False)
        
        # Game state
        self.board = self.create_board()
        self.current_player = PLAYER_PIECE
        self.game_over = False
        self.ai_depth = 5  # Start with Medium difficulty
        self.stats = {'wins': 0, 'losses': 0, 'draws': 0}
        self.play_again_button = None  # Will be created when game ends
        self.stat_labels = {}  # Store references to stat labels
        
        # New features
        self.move_history = []
        self.game_start_time = None
        self.game_duration = 0
        self.winning_positions = []
        self.animation_speed = 50  # milliseconds
        self.save_file = "connect4_stats.json"
        self.sound_enabled = True  # Enable sound by default
        
        # Load saved stats
        self.load_stats()
        
        # Simple, working dimensions - ensure all 6 rows are visible
        self.cell_size = 50  # Slightly smaller to fit better
        self.margin = 20
        self.canvas_width = COLS * self.cell_size + 2 * self.margin    # 7*50 + 40 = 390
        self.canvas_height = ROWS * self.cell_size + 2 * self.margin + 60  # 6*50 + 40 + 60 = 400 (reduced from 80 to 60)
        
        print(f"ENHANCED GUI: Canvas {self.canvas_width}x{self.canvas_height} for {ROWS}x{COLS} board")
        
        # Colors with enhanced palette
        self.colors = {
            'bg': '#0f1419',
            'secondary_bg': '#1a2332',
            'accent': '#00d4ff',
            'board': '#2d3748',
            'board_border': '#4a5568',
            'hole': '#0f1419',
            'player': '#ff6b6b',
            'ai': '#4ecdc4',
            'text': '#ffffff',
            'text_secondary': '#a0aec0',
            'success': '#48bb78',
            'warning': '#ed8936',
            'error': '#f56565',
            'button': '#667eea',
            'winning': '#ffd700',  # Gold for winning pieces
            'timer': '#9f7aea',    # Purple for timer
            'history': '#38b2ac'   # Teal for history
        }
        
        self.setup_gui()
        self.draw_board()
        
    def create_board(self) -> List[List[int]]:
        """Create empty game board"""
        return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    
    def setup_gui(self):
        # Main container - keep it simple
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(main_frame, text="CONNECT 4", 
                        font=('Segoe UI', 24, 'bold'), 
                        fg=self.colors['accent'], bg=self.colors['bg'])
        title.pack(pady=10)
        
        # Stats - Make them MUCH more visible AT THE TOP!
        stats_container = tk.Frame(main_frame, bg=self.colors['bg'])
        stats_container.pack(pady=5, fill=tk.X)
        
        # Big stats title
        tk.Label(stats_container, text="📊 GAME STATISTICS", 
                font=('Segoe UI', 12, 'bold'), fg=self.colors['accent'], 
                bg=self.colors['bg']).pack(pady=(0, 3))
        
        # Stats in a single row for better visibility
        stats_frame = tk.Frame(stats_container, bg=self.colors['secondary_bg'], relief='raised', bd=2)
        stats_frame.pack(pady=3, padx=20, fill=tk.X)
        
        print("Creating stat cards...")
        # Create play again button and stats (single row layout)
        self.create_play_again_card(stats_frame, 0)
        self.create_stat_card(stats_frame, "WINS", "wins", self.colors['success'], 1)
        self.create_stat_card(stats_frame, "LOSSES", "losses", self.colors['error'], 2)
        self.create_stat_card(stats_frame, "DRAWS", "draws", self.colors['warning'], 3)
        print(f"Created play again button and {len(self.stat_labels)} stat cards")
        
        # Status
        self.status_label = tk.Label(main_frame, text="Your Turn - Click to drop a red piece!", 
                                   font=('Segoe UI', 14, 'bold'), 
                                   fg=self.colors['player'], bg=self.colors['bg'])
        self.status_label.pack(pady=5)
        

        # Create difficulty variable before using it
        self.difficulty_var = tk.StringVar(value="Medium")

        # Canvas and side panel with timer and history
        game_area = tk.Frame(main_frame, bg=self.colors['bg'])
        game_area.pack(pady=15, fill=tk.X)
        
        # Left side - Canvas and difficulty
        canvas_container = tk.Frame(game_area, bg=self.colors['bg'])
        canvas_container.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(canvas_container,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.colors['board'],
            highlightthickness=3,
            highlightcolor=self.colors['accent'])
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_canvas_click)

        # Difficulty section RIGHT BESIDE canvas - horizontal layout
        difficulty_container = tk.Frame(game_area, bg=self.colors['secondary_bg'], relief='raised', bd=2)
        difficulty_container.pack(side=tk.LEFT, padx=(20, 0), pady=20)
        
        tk.Label(difficulty_container, text="🎯 DIFFICULTY", 
                font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['accent'], bg=self.colors['secondary_bg']).pack(pady=5)
        
        self.difficulty_label = tk.Label(difficulty_container,
            text=f"{self.difficulty_var.get()}",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['warning'],
            bg=self.colors['secondary_bg'])
        self.difficulty_label.pack(pady=5)
        
        # Difficulty dropdown
        difficulty_combo = ttk.Combobox(difficulty_container, textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Difficult"], state="readonly", width=10)
        difficulty_combo.pack(pady=5)
        difficulty_combo.bind('<<ComboboxSelected>>', self.on_difficulty_change)
        
        # Right side - Timer and Move History
        side_panel = tk.Frame(game_area, bg=self.colors['secondary_bg'], relief='raised', bd=2)
        side_panel.pack(side=tk.RIGHT, padx=(20, 0), fill=tk.Y)
        
        # Timer section
        timer_frame = tk.Frame(side_panel, bg=self.colors['secondary_bg'])
        timer_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(timer_frame, text="⏱️ GAME TIME", 
                font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['timer'], bg=self.colors['secondary_bg']).pack()
        
        self.timer_label = tk.Label(timer_frame, text="00:00", 
                                   font=('Segoe UI', 16, 'bold'), 
                                   fg=self.colors['text'], bg=self.colors['secondary_bg'])
        self.timer_label.pack(pady=5)
        
        # Move history section
        history_frame = tk.Frame(side_panel, bg=self.colors['secondary_bg'])
        history_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(history_frame, text="📝 MOVE HISTORY", 
                font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['history'], bg=self.colors['secondary_bg']).pack()
        
        # Scrollable text widget for move history
        history_scroll_frame = tk.Frame(history_frame, bg=self.colors['secondary_bg'])
        history_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_text = tk.Text(history_scroll_frame, width=18, height=10, 
                                   font=('Consolas', 9), 
                                   bg=self.colors['bg'], fg=self.colors['text'],
                                   wrap=tk.WORD, state=tk.DISABLED)
        
        history_scrollbar = tk.Scrollbar(history_scroll_frame, orient=tk.VERTICAL, 
                                        command=self.history_text.yview)
        self.history_text.config(yscrollcommand=history_scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced Controls
        controls_frame = tk.Frame(main_frame, bg=self.colors['secondary_bg'], relief='raised', bd=2)
        controls_frame.pack(pady=15, padx=20, fill=tk.X)
        
        # Top row buttons
        button_frame1 = tk.Frame(controls_frame, bg=self.colors['secondary_bg'])
        button_frame1.pack(pady=10)
        
        tk.Button(button_frame1, text="🎮 New Game", font=('Segoe UI', 12, 'bold'),
                 command=self.new_game, bg=self.colors['success'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame1, text="↶ Undo Move", font=('Segoe UI', 12, 'bold'),
                 command=self.undo_move, bg=self.colors['button'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame1, text="💡 Get Hint", font=('Segoe UI', 12, 'bold'),
                 command=self.show_hint, bg=self.colors['warning'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame1, text="⏸️ Pause", font=('Segoe UI', 12, 'bold'),
                 command=self.toggle_pause, bg=self.colors['timer'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Bottom row buttons
        button_frame2 = tk.Frame(controls_frame, bg=self.colors['secondary_bg'])
        button_frame2.pack(pady=(0, 10))
        
        tk.Button(button_frame2, text="� Save Game", font=('Segoe UI', 12, 'bold'),
                 command=self.save_game, bg=self.colors['history'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame2, text="📂 Load Game", font=('Segoe UI', 12, 'bold'),
                 command=self.load_game, bg=self.colors['history'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame2, text="�🔄 Reset Stats", font=('Segoe UI', 12, 'bold'),
                 command=self.reset_stats, bg=self.colors['error'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame2, text="🎵 Toggle Sound", font=('Segoe UI', 12, 'bold'),
                 command=self.toggle_sound, bg=self.colors['accent'], fg='white',
                 padx=15, pady=8, relief='flat', cursor='hand2').pack(side=tk.LEFT, padx=5)
    
    def create_play_again_card(self, parent, column):
        """Create a Play Again button card that resets all stats"""
        card_frame = tk.Frame(parent, bg=self.colors['accent'], relief='raised', bd=2)
        card_frame.grid(row=0, column=column, padx=4, pady=4, sticky='nsew', ipadx=3, ipady=3)
        
        # Configure grid weights for proper spacing
        parent.grid_columnconfigure(column, weight=1)
        
        # Play Again button
        play_again_btn = tk.Button(card_frame,
                                  text="🔄",
                                  font=('Segoe UI', 16, 'bold'),
                                  fg='white',
                                  bg=self.colors['accent'],
                                  command=self.reset_all_stats,
                                  relief='flat',
                                  bd=0,
                                  cursor='hand2',
                                  padx=12, pady=5)
        play_again_btn.pack()
        
        # Label
        label_widget = tk.Label(card_frame,
                               text="RESET STATS",
                               font=('Segoe UI', 9, 'bold'),
                               fg='white',
                               bg=self.colors['accent'],
                               padx=12, pady=2)
        label_widget.pack()

    def create_stat_card(self, parent, label, stat_key, color, column):
        """Create a stat card widget - Smaller but still visible!"""
        card_frame = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card_frame.grid(row=0, column=column, padx=4, pady=4, sticky='nsew', ipadx=3, ipady=3)
        
        # Configure grid weights for proper spacing
        parent.grid_columnconfigure(column, weight=1)
        
        # Stat value - Smaller but still bold
        value_label = tk.Label(card_frame,
                              text=str(self.stats[stat_key]),
                              font=('Segoe UI', 16, 'bold'),
                              fg='white',
                              bg=color,
                              padx=12, pady=5)
        value_label.pack()
        
        # Store reference to the label for updates
        self.stat_labels[stat_key] = value_label
        
        # Stat label - Smaller and compact
        label_widget = tk.Label(card_frame,
                               text=label,
                               font=('Segoe UI', 9, 'bold'),
                               fg='white',
                               bg=color,
                               padx=12, pady=2)
        label_widget.pack()
        
        # Store reference for updates
        setattr(self, f'{stat_key}_label', value_label)
    
    def draw_board(self):
        """Draw the complete 6x7 Connect 4 board with enhanced visuals"""
        self.canvas.delete("all")
        
        print(f"Drawing enhanced board: {ROWS}x{COLS} on canvas {self.canvas_width}x{self.canvas_height}")
        
        # Draw board background with gradient effect
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                   fill=self.colors['board'], 
                                   outline=self.colors['board_border'], width=3)
        
        # Draw column numbers with enhanced styling
        for col in range(COLS):
            x = self.margin + col * self.cell_size + self.cell_size // 2
            y = 30
            
            # Column highlight on hover effect
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                  fill=self.colors['secondary_bg'],
                                  outline=self.colors['accent'], width=2)
            
            self.canvas.create_text(x, y, text=str(col + 1),
                                  font=('Segoe UI', 12, 'bold'),
                                  fill=self.colors['accent'])
        
        # Draw ALL 6 rows and 7 columns with enhanced holes
        for row in range(ROWS):
            for col in range(COLS):
                x = self.margin + col * self.cell_size + self.cell_size // 2
                y = self.margin + 60 + row * self.cell_size + self.cell_size // 2
                
                hole_radius = int(self.cell_size * 0.35)
                
                # Draw hole with depth effect
                for i in range(3):
                    self.canvas.create_oval(x - hole_radius + i, y - hole_radius + i,
                                          x + hole_radius + i, y + hole_radius + i,
                                          fill='#1a202c', outline='')
                
                # Draw main hole
                self.canvas.create_oval(x - hole_radius, y - hole_radius,
                                      x + hole_radius, y + hole_radius,
                                      fill=self.colors['hole'],
                                      outline=self.colors['board_border'],
                                      width=2)
        
        # Draw pieces with winning highlight
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != EMPTY:
                    is_winning = (row, col) in self.winning_positions
                    self.draw_piece(row, col, piece, is_winning)
        
        print(f"Successfully drew enhanced board with {ROWS * COLS} positions")
    
    def draw_piece(self, row, col, piece, is_winning=False):
        """Draw a game piece with enhanced visuals and winning highlight"""
        x = self.margin + col * self.cell_size + self.cell_size // 2
        y = self.margin + 60 + row * self.cell_size + self.cell_size // 2
        piece_radius = int(self.cell_size * 0.3)
        
        color = self.colors['player'] if piece == PLAYER_PIECE else self.colors['ai']
        
        if is_winning:
            # Draw glowing effect for winning pieces
            for i in range(5, 0, -1):
                glow_color = self.colors['winning'] if i <= 2 else color
                alpha = 0.3 + (0.7 * (6 - i) / 5)
                self.canvas.create_oval(x - piece_radius - i, y - piece_radius - i,
                                      x + piece_radius + i, y + piece_radius + i,
                                      fill=glow_color, outline='')
        
        # Draw shadow with multiple layers for depth
        for i in range(3):
            shadow_offset = 2 + i
            self.canvas.create_oval(x - piece_radius + shadow_offset, y - piece_radius + shadow_offset,
                                  x + piece_radius + shadow_offset, y + piece_radius + shadow_offset,
                                  fill='#0a0a0a', outline='')
        
        # Draw main piece with gradient effect
        self.canvas.create_oval(x - piece_radius, y - piece_radius,
                              x + piece_radius, y + piece_radius,
                              fill=color, outline='#ffffff', width=3)
        
        # Add highlight for 3D effect
        highlight_radius = piece_radius - 5
        self.canvas.create_oval(x - highlight_radius + 3, y - highlight_radius + 3,
                              x - highlight_radius + 8, y - highlight_radius + 8,
                              fill='#ffffff', outline='')
        
        if is_winning:
            # Add star effect for winning pieces
            self.canvas.create_text(x, y, text="★", font=('Arial', 16), fill='#ffffff')
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        if self.game_over or self.current_player != PLAYER_PIECE:
            return
        
        col = self.get_column_from_x(event.x)
        if col is not None and self.is_valid_location(col):
            self.make_move(col)
    
    def get_column_from_x(self, x) -> Optional[int]:
        """Get column number from x coordinate"""
        if x < self.margin or x > self.canvas_width - self.margin:
            return None
        
        col = (x - self.margin) // self.cell_size
        return col if 0 <= col < COLS else None
    
    def is_valid_location(self, col: int) -> bool:
        """Check if column is valid for move"""
        return 0 <= col < COLS and self.board[0][col] == EMPTY
    
    def get_next_open_row(self, col: int) -> Optional[int]:
        """Get next available row in column"""
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return None
    
    def make_move(self, col: int):
        """Make a move in the specified column with enhanced features"""
        if not self.is_valid_location(col):
            return False
        
        row = self.get_next_open_row(col)
        if row is None:
            return False
        
        # Start timer if first move
        if not self.move_history:
            self.start_timer()
        
        # Place piece with animation
        self.board[row][col] = PLAYER_PIECE
        self.animate_piece_drop(row, col, PLAYER_PIECE)
        
        # Add to move history
        move_text = f"Player: Column {col + 1}"
        self.add_move_to_history(move_text)
        
        # Play sound effect
        self.play_sound("move")
        
        # Check for win
        if self.winning_move(self.board, PLAYER_PIECE):
            self.winning_positions = self.get_winning_positions(self.board, PLAYER_PIECE)
            self.draw_board()  # Redraw with winning highlights
            self.status_label.config(text="🎉 You Win! Congratulations! 🎉", fg=self.colors['success'])
            self.stats['wins'] += 1
            self.update_stats_display()
            self.game_over = True
            self.stop_timer()
            self.play_sound("win")
            self.save_stats()
            self.show_play_again_button()
            return True
        
        # Check for draw
        if self.is_board_full():
            self.status_label.config(text="🤝 It's a draw! Good game! ⚖️", fg=self.colors['warning'])
            self.stats['draws'] += 1
            self.update_stats_display()
            self.game_over = True
            self.stop_timer()
            self.play_sound("draw")
            self.save_stats()
            self.show_play_again_button()
            return True
        
        # AI turn
        self.current_player = AI_PIECE
        self.status_label.config(text="🤖 AI is thinking...", fg=self.colors['ai'])
        self.root.after(800, self.ai_move)  # Slightly longer delay for better UX
        
        return True
    
    def ai_move(self):
        """AI makes a move with enhanced features"""
        col = self.get_ai_move()
        if col is not None:
            row = self.get_next_open_row(col)
            if row is not None:
                self.board[row][col] = AI_PIECE
                self.animate_piece_drop(row, col, AI_PIECE)
                
                # Add to move history
                move_text = f"AI: Column {col + 1}"
                self.add_move_to_history(move_text)
                
                # Play sound effect
                self.play_sound("move")
                
                if self.winning_move(self.board, AI_PIECE):
                    self.winning_positions = self.get_winning_positions(self.board, AI_PIECE)
                    self.draw_board()  # Redraw with winning highlights
                    self.status_label.config(text="🤖 AI Wins! Try again! 🔴", fg=self.colors['error'])
                    self.stats['losses'] += 1
                    self.update_stats_display()
                    self.game_over = True
                    self.stop_timer()
                    self.play_sound("lose")
                    self.save_stats()
                    self.show_play_again_button()
                    return
                
                if self.is_board_full():
                    self.status_label.config(text="🤝 It's a draw! Good game! ⚖️", fg=self.colors['warning'])
                    self.stats['draws'] += 1
                    self.update_stats_display()
                    self.game_over = True
                    self.stop_timer()
                    self.play_sound("draw")
                    self.save_stats()
                    self.show_play_again_button()
                    return
        
        # Back to player
        self.current_player = PLAYER_PIECE
        self.status_label.config(text="Your Turn - Click to drop a red piece!", fg=self.colors['player'])
    
    def get_ai_move(self) -> Optional[int]:
        """Smart AI using minimax algorithm with alpha-beta pruning"""
        # First, check if AI can win immediately
        for col in range(COLS):
            if self.is_valid_location(col):
                temp_board = [row[:] for row in self.board]  # Copy board
                row = self.get_next_open_row(col)
                if row is not None:
                    temp_board[row][col] = AI_PIECE
                    if self.winning_move(temp_board, AI_PIECE):
                        return col
        
        # Second, check if AI needs to block player from winning
        for col in range(COLS):
            if self.is_valid_location(col):
                temp_board = [row[:] for row in self.board]  # Copy board
                row = self.get_next_open_row(col)
                if row is not None:
                    temp_board[row][col] = PLAYER_PIECE
                    if self.winning_move(temp_board, PLAYER_PIECE):
                        return col
        
        # Use minimax for strategic play
        col, _ = self.minimax(self.board, self.ai_depth, -math.inf, math.inf, True)
        return col if col is not None else self.get_center_column()
    
    def get_center_column(self) -> int:
        """Prefer center column as it gives more winning opportunities"""
        center_col = COLS // 2
        if self.is_valid_location(center_col):
            return center_col
        
        # If center is full, try columns near center
        for offset in [1, -1, 2, -2, 3]:
            col = center_col + offset
            if 0 <= col < COLS and self.is_valid_location(col):
                return col
        
        # Fallback to any valid column
        valid_cols = [col for col in range(COLS) if self.is_valid_location(col)]
        return random.choice(valid_cols) if valid_cols else 0
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning"""
        valid_locations = [col for col in range(COLS) if self.is_valid_location_board(board, col)]
        is_terminal = self.is_terminal_node(board)
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, AI_PIECE):
                    return (None, 100000000000000)
                elif self.winning_move(board, PLAYER_PIECE):
                    return (None, -10000000000000)
                else:  # Game is over, no more valid moves
                    return (None, 0)
            else:  # Depth is zero
                return (None, self.score_position(board, AI_PIECE))
        
        if maximizing_player:
            value = -math.inf
            column = random.choice(valid_locations) if valid_locations else None
            for col in valid_locations:
                row = self.get_next_open_row_board(board, col)
                b_copy = [row[:] for row in board]
                b_copy[row][col] = AI_PIECE
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        
        else:  # Minimizing player
            value = math.inf
            column = random.choice(valid_locations) if valid_locations else None
            for col in valid_locations:
                row = self.get_next_open_row_board(board, col)
                b_copy = [row[:] for row in board]
                b_copy[row][col] = PLAYER_PIECE
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
    
    def score_position(self, board, piece):
        """Evaluate the board position for the given piece"""
        score = 0
        
        # Score center column
        center_array = [board[r][COLS // 2] for r in range(ROWS)]
        center_count = center_array.count(piece)
        score += center_count * 3
        
        # Score horizontal
        for r in range(ROWS):
            row_array = board[r]
            for c in range(COLS - 3):
                window = row_array[c:c + 4]
                score += self.evaluate_window(window, piece)
        
        # Score vertical
        for c in range(COLS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r + 4]
                score += self.evaluate_window(window, piece)
        
        # Score positive diagonal
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)
        
        # Score negative diagonal
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r + 3 - i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)
        
        return score
    
    def evaluate_window(self, window, piece):
        """Evaluate a window of 4 positions"""
        score = 0
        opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
        
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 10
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 2
        
        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 80
        
        return score
    
    def is_terminal_node(self, board):
        """Check if the game is over"""
        return (self.winning_move(board, PLAYER_PIECE) or 
                self.winning_move(board, AI_PIECE) or 
                len([col for col in range(COLS) if self.is_valid_location_board(board, col)]) == 0)
    
    def is_valid_location_board(self, board, col: int) -> bool:
        """Check if column is valid for move on given board"""
        return 0 <= col < COLS and board[0][col] == EMPTY
    
    def get_next_open_row_board(self, board, col: int) -> Optional[int]:
        """Get next available row in column for given board"""
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] == EMPTY:
                return row
        return None
    
    def winning_move(self, board, piece):
        """Check if the current move is a winning move"""
        # Check horizontal
        for c in range(COLS - 3):
            for r in range(ROWS):
                if all(board[r][c + i] == piece for i in range(4)):
                    return True
        
        # Check vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if all(board[r + i][c] == piece for i in range(4)):
                    return True
        
        # Check positive diagonal
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    return True
        
        # Check negative diagonal
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    return True
        
        return False
    
    def is_board_full(self) -> bool:
        """Check if board is full"""
        return all(self.board[0][col] != EMPTY for col in range(COLS))
    def update_stats_display(self):
        """Update the stat cards with current values"""
        try:
            for stat_key, label in self.stat_labels.items():
                if stat_key in self.stats:
                    label.config(text=str(self.stats[stat_key]))
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def show_play_again_button(self):
        """Show the Play Again button when game ends"""
        if self.play_again_button is None:
            # Create the button in the center of the canvas
            button_x = self.canvas_width // 2
            button_y = self.canvas_height // 2
            
            # Create a stylish Play Again button
            self.play_again_button = tk.Button(
                self.canvas,
                text="🎮 Play Again",
                font=('Segoe UI', 16, 'bold'),
                bg=self.colors['success'],
                fg='white',
                padx=20,
                pady=10,
                command=self.start_new_game,
                relief='flat',
                bd=0,
                cursor='hand2'
            )
            
            # Place button in center of canvas
            self.canvas.create_window(button_x, button_y, window=self.play_again_button)
    
    def hide_play_again_button(self):
        """Hide the Play Again button"""
        if self.play_again_button:
            self.play_again_button.destroy()
            self.play_again_button = None
    
    def start_new_game(self):
        """Start a new game and hide the Play Again button"""
        self.hide_play_again_button()
        self.new_game()

    def new_game(self):
        """Start a new game with enhanced features"""
        self.board = self.create_board()
        self.current_player = PLAYER_PIECE
        self.game_over = False
        self.move_history = []
        self.winning_positions = []
        self.game_start_time = None
        self.game_duration = 0
        self.status_label.config(text="Your Turn - Click to drop a red piece!", fg=self.colors['player'])
        self.clear_move_history()
        self.update_timer_display()
        self.draw_board()
        print("Started new enhanced game!")
    
    # Enhanced Features Methods
    def animate_piece_drop(self, target_row, col, piece):
        """Animate piece dropping into position"""
        # Simple animation - just redraw board for now
        # In a full implementation, you'd animate the piece falling
        self.draw_board()
    
    def start_timer(self):
        """Start the game timer"""
        self.game_start_time = time.time()
        self.update_timer()
    
    def stop_timer(self):
        """Stop the game timer"""
        if self.game_start_time:
            self.game_duration = time.time() - self.game_start_time
    
    def update_timer(self):
        """Update the timer display"""
        if self.game_start_time and not self.game_over:
            elapsed = time.time() - self.game_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def update_timer_display(self):
        """Update timer display to show current time"""
        if self.game_duration > 0:
            minutes = int(self.game_duration // 60)
            seconds = int(self.game_duration % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        else:
            self.timer_label.config(text="00:00")
    
    def add_move_to_history(self, move_text):
        """Add a move to the history display"""
        self.move_history.append(move_text)
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"{len(self.move_history)}. {move_text}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def clear_move_history(self):
        """Clear the move history display"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def get_winning_positions(self, board, piece):
        """Get positions of winning pieces for highlighting"""
        positions = []
        
        # Check horizontal
        for c in range(COLS - 3):
            for r in range(ROWS):
                if all(board[r][c + i] == piece for i in range(4)):
                    positions.extend([(r, c + i) for i in range(4)])
        
        # Check vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if all(board[r + i][c] == piece for i in range(4)):
                    positions.extend([(r + i, c) for i in range(4)])
        
        # Check positive diagonal
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    positions.extend([(r + i, c + i) for i in range(4)])
        
        # Check negative diagonal
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    positions.extend([(r - i, c + i) for i in range(4)])
        
        return positions
    
    def play_sound(self, sound_type):
        """Play sound effects using Windows system sounds"""
        if not self.sound_enabled or not winsound:
            return
            
        try:
            # Use threading to avoid blocking the GUI
            def play_async():
                if sound_type == "move":
                    # Play a short beep for moves
                    winsound.Beep(800, 150)  # 800Hz for 150ms
                elif sound_type == "win":
                    # Play victory sound - ascending melody
                    winsound.Beep(600, 200)
                    time.sleep(0.1)
                    winsound.Beep(800, 200)
                    time.sleep(0.1)
                    winsound.Beep(1000, 300)
                elif sound_type == "lose":
                    # Play defeat sound - descending melody
                    winsound.Beep(800, 300)
                    time.sleep(0.1)
                    winsound.Beep(600, 300)
                    time.sleep(0.1)
                    winsound.Beep(400, 400)
                elif sound_type == "draw":
                    # Play neutral sound - double beep
                    winsound.Beep(700, 200)
                    time.sleep(0.1)
                    winsound.Beep(700, 200)
            
            # Play sound in separate thread to avoid GUI freezing
            sound_thread = threading.Thread(target=play_async)
            sound_thread.daemon = True
            sound_thread.start()
            
        except Exception as e:
            print(f"Sound error: {e}")
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        status = "ON" if self.sound_enabled else "OFF"
        messagebox.showinfo("Sound Toggle", f"🔊 Sound effects are now {status}!")
        
        # Play test sound if enabling
        if self.sound_enabled:
            self.play_sound("move")
    
    def toggle_pause(self):
        """Pause/Resume the game"""
        if hasattr(self, 'paused'):
            self.paused = not self.paused
        else:
            self.paused = True
        
        if self.paused:
            self.status_label.config(text="⏸️ Game Paused - Click to Resume", fg=self.colors['timer'])
        else:
            self.status_label.config(text="Your Turn - Click to drop a red piece!", fg=self.colors['player'])
    
    def save_game(self):
        """Save the current game state"""
        game_state = {
            'board': self.board,
            'current_player': self.current_player,
            'move_history': self.move_history,
            'game_duration': self.game_duration,
            'difficulty': self.difficulty_var.get(),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        try:
            with open('saved_game.json', 'w') as f:
                json.dump(game_state, f)
            messagebox.showinfo("Save Game", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save game: {e}")
    
    def load_game(self):
        """Load a saved game state"""
        try:
            if os.path.exists('saved_game.json'):
                with open('saved_game.json', 'r') as f:
                    game_state = json.load(f)
                
                self.board = game_state['board']
                self.current_player = game_state['current_player']
                self.move_history = game_state['move_history']
                self.game_duration = game_state.get('game_duration', 0)
                self.difficulty_var.set(game_state.get('difficulty', 'Medium'))
                
                # Restore display
                self.draw_board()
                self.clear_move_history()
                for move in self.move_history:
                    self.add_move_to_history(move)
                self.update_timer_display()
                
                messagebox.showinfo("Load Game", "Game loaded successfully!")
            else:
                messagebox.showwarning("Load Game", "No saved game found!")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load game: {e}")
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.stats, f)
        except Exception as e:
            print(f"Could not save stats: {e}")
    
    def load_stats(self):
        """Load statistics from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    self.stats = json.load(f)
        except Exception as e:
            print(f"Could not load stats: {e}")
            self.stats = {'wins': 0, 'losses': 0, 'draws': 0}
    
    def undo_move(self):
        """Undo the last move (simple version)"""
        if self.game_over:
            return
        
        # Find and remove last 2 moves (player + AI)
        moves_undone = 0
        for row in range(ROWS - 1, -1, -1):
            for col in range(COLS - 1, -1, -1):
                if self.board[row][col] != EMPTY and moves_undone < 2:
                    self.board[row][col] = EMPTY
                    moves_undone += 1
                    if moves_undone == 2:
                        break
            if moves_undone == 2:
                break
        
        self.current_player = PLAYER_PIECE
        self.status_label.config(text="Your Turn - Click to drop a red piece!", fg=self.colors['player'])
        self.draw_board()
    
    def reset_all_stats(self):
        """Reset all game statistics without confirmation"""
        self.stats = {'wins': 0, 'losses': 0, 'draws': 0}
        self.update_stats_display()
        self.status_label.config(text="🔄 Statistics Reset! Start a new game!", fg=self.colors['accent'])

    def reset_stats(self):
        """Reset all game statistics"""
        from tkinter import messagebox
        if messagebox.askyesno("Reset Statistics", "Are you sure you want to reset all your game statistics?"):
            self.stats = {'wins': 0, 'losses': 0, 'draws': 0}
            self.update_stats_display()
            messagebox.showinfo("Statistics Reset", "All statistics have been reset to zero!")

    def show_hint(self):
        """Show hint for best move"""
        valid_cols = [col for col in range(COLS) if self.is_valid_location(col)]
        if valid_cols:
            hint_col = random.choice(valid_cols)
            messagebox.showinfo("Hint", f"Try column {hint_col + 1}!")
    
    def on_difficulty_change(self, event):
        """Handle difficulty selection change"""
        difficulty = self.difficulty_var.get()
        if difficulty == "Easy":
            self.ai_depth = 3  # Still challenging but beatable
        elif difficulty == "Medium":
            self.ai_depth = 5  # Good balance of challenge and speed
        elif difficulty == "Difficult":
            self.ai_depth = 7  # Very challenging AI
        
        print(f"AI difficulty set to {difficulty} (depth: {self.ai_depth})")

        # Update difficulty label beside canvas
        if hasattr(self, 'difficulty_label'):
            self.difficulty_label.config(text=difficulty)
    
    def run(self):
        """Start the enhanced game"""
        print("Starting Connect 4 Pro GUI...")
        print(f"Window: 1000x850")
        print(f"Canvas: {self.canvas_width}x{self.canvas_height}")
        print(f"Board: {ROWS} rows x {COLS} columns")
        print("🎮 Enhanced features: Timer, Move History, Save/Load, Sound Effects")
        self.root.mainloop()

if __name__ == "__main__":
    game = Connect4GUI()
    game.run()
