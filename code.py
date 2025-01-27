from adafruit_macropad import MacroPad
import random
import time

flash_interval = 0.5
flash_repetition = 5
player_colors = {"X":(0,255,0),"O":(255,0,0), "off":(0,0,0) }
digits = (0,1,2,3,4,5,6,7,8)
difficulty = 0
start_player_computer = False
blank_positions = ( ( 0,1,2 ),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(6,4,2) )
macropad = MacroPad()
screen_lines = macropad.display_text( title = "Macropad Tic-Tac-Toe" )
start_game_handled = False

def make_positions( board ):
    "create a list of posssible winning positions from the board list"
    positions=[ ( board[0], board[1], board[2] ),
                ( board[3], board[4], board[5] ),
                ( board[6], board[7], board[8] ),
                ( board[0], board[3], board[6] ),
                ( board[1], board[4], board[7] ),
                ( board[2], board[5], board[8] ),
                ( board[0], board[4], board[8] ),
                ( board[2], board[4], board[6] ) ]
    return positions

def count_pieces( position, player ):
    "Count the number of each piece type in a given position"
    digit_count = 0
    player_count = 0
    other_count = 0
    for counter in range(3) :
        board_space = position[counter]
        if board_space == player:
            player_count += 1
        if board_space in digits :
            digit_count += 1
    return (player_count, digit_count )

def can_win( positions, player ) :
    " Find a winning move for a given player, if one exists"
    move = None
    positions = make_positions( board )
    for test_position in positions:
        possible_win = count_pieces( test_position, player )
        if possible_win == (2,1) :
            for board_space in range(3) :
                if test_position[board_space] in digits :
                    move = test_position[board_space]
    return move

def split_move( positions, player ) :
    "Find a move that will create two winning positions, if one exists"
    move = None
    positions = make_positions( board )
    possible_splits = []
    for test_position in positions:
        possible_move = count_pieces( test_position, player)
        if possible_move == (1,2) :
            for column in range(3) :
                if test_position[column] in digits :
                    possible_splits.append( test_position[column] )
    possible_splits.sort()
    for count in range( len( possible_splits )-1 ):
        if possible_splits[count] == possible_splits[count+1] :
            move = possible_splits[count]
            break
    return move

def display_board( board, player ):
    "set LEDs to display board state. Player is green, computer is red, available is off"
    for LED in range(9):
        if board[LED] in digits:
            macropad.pixels[LED]=(0,0,0)
        elif board[LED] == player :
            macropad.pixels[LED] = (0,255,0)
        else:
            macropad.pixels[LED] = (255,0,0)
    return

def get_user_move( board ):
    "Get a move from the user"
    keypress = macropad.keys.events.get()
    while keypress :
        keypress = macropad.keys.events.get()
    while True:
        keypress = macropad.keys.events.get()
        if keypress :
            if keypress.pressed ==True :
                move = keypress.key_number
                if move < 9 :
                    if board[move] in digits :
                        break
    return move

def pick_corner( board ) :
    "randomly pick a corner square"
    corners = []
    move = None
    for corner_num in [0,2,6,8] :
        if board[ corner_num ] in digits :
            corners.append( corner_num )
    if len( corners ) > 0 :
        move = corners[ random.randint(0, len( corners)-1 ) ]
    return move

def pick_edge( board ) :
    "randomly pick an edge square"
    edges = []
    move = None
    for edge_num in [1,3,5,7 ] :
        if board[edge_num ] in digits :
            edges.append( edge_num )
    if len( edges ) > 0 :
        move = edges[ random.randint(0, len( edges)-1 ) ]
    return move

def game_over( board ):
    "Check for end of game"
    winning_move=[]
    remaining_moves = 0
    positions = make_positions( board )
    blank_positions = ( ( 0,1,2 ),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(6,4,2) )
    for count in range ( len( positions) ) :
        if  positions[ count ] == ( "X", "X", "X" ) or positions[ count ] == ( "O", "O", "O" ) :
            winning_move = blank_positions[count]
            break
        for testpos in positions[count] :
            if testpos in digits :
                remaining_moves = remaining_moves +1
    if  remaining_moves == 0 and not winning_move :
        winning_move = (9,9,9)
    return winning_move

def check_special_case_move( board ) :
    " check for special case of game starting with all moves in diagonal line "
    digit_count = 0
    move = None
    for square in range( len( board ) ) :
        if board[square] in digits :
            digit_count = digit_count +1
    if digit_count == 6 :
        positions = make_positions( board )
        if positions[6] == ("X","O","X") or positions[7] == ("X","O","X") :
            move = pick_edge( board )
    return move

def get_computer_move( board, difficulty, player, computer ) :
    positions = make_positions( board )
    move = None
    if difficulty > 0 :
        move = can_win( positions, computer )
    if move == None and difficulty > 0:
        move = can_win( positions, player )
    if move == None and difficulty >1:
        move = check_special_case_move( board )
    if move  == None  and difficulty >1 :
        move = split_move( positions, computer )
    if move == None and difficulty >1:
        move = split_move( positions, player )
    if move == None:
        if board[4] in digits :
            move = 4
    if move == None:
        move = pick_corner( board )
    if move  == None:
        move = pick_edge( board )
    return move

def display_instructions() :
    instructions =  "Turn knob for","game instructions"," ","The top nine keys","are the game board",\
                    "The bottom three","keys are for setup"," ","The left setup key",\
                    "sets the difficulty","The level is shown","by the key color","Green is 'easy'",\
                    "Yellow is 'hard'","Red is 'impossible'","Blue is 'two player'"," ",\
                    "The right setup key","shows which player","goes first.","The computer always",\
                    "plays the RED color"," ","The middle key clears","the board and starts","a new game"
    current_instruction = macropad.encoder% ( len( instructions )-2 )
    for count in range(3) :
        screen_lines[count].text = instructions[ current_instruction + count ]
    screen_lines.show()
    return

while True :
    while not start_game_handled :
        display_instructions()
        key_event = macropad.keys.events.get()
        if key_event :
            if key_event.pressed == True:
                if key_event.key_number == 9 :
                    difficulty +=1
                    if difficulty > 3 :
                        difficulty = 0
                if key_event.key_number == 10:
                    start_game_handled = True
                    macropad.pixels[10]=(0,255,0)
                if key_event.key_number == 11 :
                    start_player_computer = not start_player_computer
        if difficulty == 0:
            macropad.pixels[9] = (0,255,0)
        if difficulty ==1 :
            macropad.pixels[9] = (255,255,0)
        if difficulty == 2 :
            macropad.pixels[9] = ( 255,0,0)
        if difficulty == 3 :
            macropad.pixels[9] = (0,0,255)
        if start_player_computer :
            macropad.pixels[11]=(255,0,0)
        else :
            macropad.pixels[11]=(0,255,0)
        screen_lines.show()
    macropad.pixels[10]=(0,0,0)
    start_game_handled = False
    first_move = True
    board = [ 0, 1, 2, 3, 4, 5, 6, 7, 8 ]
    player = "X"
    computer = "O"
    display_board(board,player)
    while True :
        if not ( start_player_computer and first_move ) :
            user_move = get_user_move( board )
            board[ user_move ] = player
            display_board(board,player)
            winning_move = game_over(board)
            if winning_move :
                break
        first_move = False
        if difficulty == 3 :
            computer_move = get_user_move( board )
        else :
            computer_move = get_computer_move( board, difficulty, player, computer )
        board[ computer_move ] = computer
        display_board(board,player)
        winning_move = game_over(board)
        if winning_move :
            break
    if winning_move != (9,9,9) :
        color = player_colors[board[winning_move[0]] ]
        for count in range(flash_repetition) :
            for move_pixel in winning_move :
                macropad.pixels[ move_pixel] = (0,0,0)
            time.sleep(flash_interval)
            for move_pixel in winning_move :
                macropad.pixels[ move_pixel] = color
            time.sleep(flash_interval)
    else :
        playerX_list = []
        playerO_list = []
        for count in range( len( board ) ) :
            if board[ count] == "X" :
                playerX_list.append( count )
            if board[count] == "O" :
                playerO_list.append( count )
        for count in range(flash_repetition) :
            for square in playerX_list :
                macropad.pixels[square] = player_colors["off"]
            for square in  playerO_list :
                macropad.pixels[square] = player_colors["O"]
            time.sleep( flash_interval)
            for square in playerX_list :
                macropad.pixels[square] = player_colors["X"]
            for square in  playerO_list :
                macropad.pixels[square] = player_colors["off"]
            time.sleep( flash_interval )
    display_board( board , player )
