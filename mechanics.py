import time
import random

#Maze:

MAZE_SIZE = 10
MAZE_COOLDOWN = 0.18

moves = {
    "u": (-1, 0),
    "d": (1, 0),
    "l": (0, -1),
    "r": (0, 1)}

def reset_maze():
    global maze
    global maze_last_move
    maze_last_move = 0.0
    maze = [
        ['W','W','W','W','W','W','W','W','W','W'],
        ['W','C','C','C','C','X','C','C','C','W'],
        ['W','C','.','C','.','.','.','.','C','W'],
        ['W','C','.','C','C','C','C','.','C','W'],
        ['W','.','.','.','.','.','C','.','C','W'],
        ['W','.','C','C','C','.','.','.','C','W'],
        ['W','.','.','C','C','C','C','C','.','W'],
        ['W','C','.','.','.','.','.','.','.','W'],
        ['W','C','C','C','P','C','C','C','C','W'],
        ['W','W','W','W','W','W','W','W','W','W']]

reset_maze()

def maze_ready():
    global maze_last_move
    now = time.time()
    if now - maze_last_move < MAZE_COOLDOWN:
        return False
    maze_last_move = now
    return True

def find_p():
    for y in range(MAZE_SIZE):
        for x in range(MAZE_SIZE):
            if maze[y][x] == "P":
                return y, x
    return None

def move_player(direction):
    if direction not in moves:
        return "invalid"
    position = find_p()
    if position is None:
        return "error"
    y, x = position
    dy, dx = moves[direction]
    new_y = y + dy
    new_x = x + dx
    if not (0 <= new_y < MAZE_SIZE and 0 <= new_x < MAZE_SIZE):
        return "boundary"
    if maze[new_y][new_x] == "W":
        return "wall"
    if maze[new_y][new_x] == "C":
        return "cobweb"
    if maze[new_y][new_x] == "X":
        maze[y][x] = "."
        maze[new_y][new_x] = "P"
        return "win"
    maze[y][x] = "."
    maze[new_y][new_x] = "P"
    return "move"

def get_maze():
    return maze

#QTE (ogre fight):

QTE_PLAYER_HP = 3
QTE_OGRE_HP = 5
QTE_START_TIME = 2.5     # seconds allowed in round 1
QTE_SPEEDUP = 0.93       # each round's limit is multiplied by this
QTE_MIN_TIME = 0.8       # never faster than this

QTE_KEYS = {
    1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h", 9: "i",
    10: "j", 11: "k", 12: "l", 13: "m", 14: "n", 15: "o", 16: "p", 17: "q",
    18: "r", 19: "s", 20: "t", 21: "u", 22: "v", 23: "w", 24: "x", 25: "y",
    26: "z"}

def reset_qte():
    global qte_round
    global qte_key
    global qte_mode
    global player_hp
    global ogre_hp
    qte_round = 0
    qte_key = ""
    qte_mode = "dodge"
    player_hp = QTE_PLAYER_HP
    ogre_hp = QTE_OGRE_HP

def get_qte_time():
    limit = QTE_START_TIME * (QTE_SPEEDUP ** qte_round)
    return max(limit, QTE_MIN_TIME)

def new_qte():
    # sets up the next round: alternates dodge/attack, random key that differs from last round
    global qte_key
    global qte_mode
    if qte_round % 2 == 0:
        qte_mode = "dodge"
    else:
        qte_mode = "attack"
    previous = qte_key
    key = previous
    while key == previous:
        key = QTE_KEYS[random.randint(1, 26)]
    qte_key = key
    return qte_key

def resolve_qte(player_input, start_time):
    # player_input is None on timeout. Returns "dodged", "hurt", "hit" or "missed"
    global qte_round
    global player_hp
    global ogre_hp
    success = False
    if player_input is not None:
        elapsed = time.time() - start_time
        success = elapsed <= get_qte_time() and player_input == qte_key
    if qte_mode == "dodge":
        if success:
            result = "dodged"
        else:
            player_hp -= 1
            result = "hurt"
    else:
        if success:
            ogre_hp -= 1
            result = "hit"
        else:
            result = "missed"
    qte_round += 1
    return result

def qte_state():
    if ogre_hp <= 0:
        return "win"
    if player_hp <= 0:
        return "lose"
    return "continue"

def get_qte_key():
    return qte_key

def get_qte_prompt():
    if qte_mode == "dodge":
        return "Dodge!"
    return "Attack!"

def get_player_hp():
    return player_hp

def get_ogre_hp():
    return ogre_hp

reset_qte()

#Whack a fox (Truly creative name XD)

FOX_TICK = 0.8
FOX_ROUND_TIME = 20
FOX_TARGET = 8

def reset_foxes():
    global fox_holes
    global fox_score
    fox_holes = [".", ".", ".",
                 ".", ".", ".",
                 ".", ".", "."]
    fox_score = 0

reset_foxes()

def fox_tick():
    for i in range(9):
        fox_holes[i] = "."
    spot = random.randint(0, 8)
    fox_holes[spot] = "F"
    return spot

def whack(x):
    global fox_score
    if fox_holes[x] == "F":
        fox_holes[x] = "."
        fox_score += 1
        return "hit"
    return "miss"

def check_foxes():
    win = fox_score >= FOX_TARGET
    return win

def get_foxes():
    return fox_holes

def get_fox_score():
    return fox_score