
from fltk import *
import socket
from threading import Thread
from queue import Queue

ROWS = 5
COLS = 5
BUTTON_SIZE = 200
MAX_SHIPS = 5

class Battlefield(Fl_Window):
    def __init__(self, x, y, w, h, title, is_client=False, host=None, port=None):
        super().__init__(x, y, w, h, title)
        self.my_grid = []  # Your grid
        self.ship_count = 0
        self.placing_ships = True
        self.ships_hit = 0
        self.game_over = False
        self.my_turn = is_client
        self.is_client = is_client

        self.pending_moves = Queue()

        # Networking setup
        self.conn = None
        if is_client:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, port))
        else:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((host, port))
            server.listen(1)
            self.conn, _ = server.accept()

        self.begin()
        self._create_grid()
        self.end()
        self.show()

        # Start network listener
        Thread(target=self.move_receive, daemon=True).start()

        Fl.add_timeout(0.05, self.check_moves)

    def _create_grid(self):
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                btn = Buttons(r, c, self)
                btn.position(c * BUTTON_SIZE, r * BUTTON_SIZE)
                row.append(btn)
            self.my_grid.append(row)

    def ship_counter(self):
        if self.ship_count < MAX_SHIPS:
            self.ship_count += 1
            print(f"{self.ship_count}/{MAX_SHIPS} ships placed")

    def placable_ship(self):
        return self.ship_count < MAX_SHIPS

    def move_send(self, row, col):
        try:
            self.conn.sendall(f"{row},{col}\n".encode())
            print("Move sent")
            self.my_turn = False
        except Exception as e:
            print(f"Error sending move: {e}")

    def move_receive(self):
        buffer = ""

        while True:
            try:
                data = self.conn.recv(1024).decode()
                # print("Recieved data:", repr(data))
                if not data:
                    print("Opponent disconnected.")
                    break

                print("Recieved data:", repr(data))
                buffer += data

                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)

                    if message == "WIN":
                        self.pending_moves.put(("WIN", None))
                    else:
                        row, col = map(int, data.split(","))
                        self.pending_moves.put((row, col))
                    #Fl.awake(lambda : self.click_opponent(row, col))
            except Exception as e:
                print(f"Error receiving move: {e}")
                break

    def click_opponent(self, row, col):
        if self.game_over:
            return

        #print("Processing opponent's move")
        btn = self.my_grid[row][col]

        if btn.ship_placed:
            print("Opponent hit your ship!")
            btn.image(Buttons.hit_image)
            btn.ship_placed = False
            self.ships_hit += 1
        else:
            print("Opponent missed!")
            btn.image(Buttons.miss_image)

        btn.redraw()

        if self.ships_hit == MAX_SHIPS:
            print("Game over! Opponent wins!")
            self.game_over = True
            self.my_turn = False
            self.conn.sendall(b"WIN\n")
        else:
            self.my_turn = True

    def check_moves(self, data=None):
        while not self.pending_moves.empty():
            row, col = self.pending_moves.get()

            if row == "WIN":
                self.game_over = True
                self.my_turn = False
                print("Game over! You win!")
            else:
                self.click_opponent(row, col)

        Fl.repeat_timeout(0.05, self.check_moves)


class Buttons(Fl_Button):
    og_image = Fl_PNG_Image("blank.png")
    og_ship_image = Fl_PNG_Image("ship.png")
    og_hit_image = Fl_PNG_Image("hit.png")
    og_miss_image = Fl_PNG_Image("miss.png")

    blank_image = og_image.copy(BUTTON_SIZE, BUTTON_SIZE)
    ship_image = og_ship_image.copy(BUTTON_SIZE, BUTTON_SIZE)
    hit_image = og_hit_image.copy(BUTTON_SIZE, BUTTON_SIZE)
    miss_image = og_miss_image.copy(BUTTON_SIZE, BUTTON_SIZE)

    def __init__(self, row, col, battlefield):
        super().__init__(0, 0, BUTTON_SIZE, BUTTON_SIZE)
        self.row = row
        self.col = col
        self.battlefield = battlefield
        self.ship_placed = False
        self.image(Buttons.blank_image)
        self.callback(self.on_click)
        self.placing_ships = True

    def on_click(self, wid):
        if self.battlefield.game_over:
            print("Game over!")
            return

        if self.battlefield.placing_ships:
            if self.ship_placed:
                print("Already placed a ship here. Choose another location.")

            elif self.battlefield.placable_ship():
                self.image(Buttons.ship_image)
                self.ship_placed = True
                self.battlefield.ship_counter()

                if self.battlefield.ship_count == MAX_SHIPS:
                    self.battlefield.placing_ships = False
                    print("Maximum ships placed!")
        else:
            #print("Is Client:", self.battlefield.is_client)
            #print("Current turn:", self.battlefield.my_turn)
            if self.battlefield.my_turn:
                self.battlefield.move_send(self.row, self.col)
            else:
                print("Not your turn!")
            


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--client", action="store_true")
    args = parser.parse_args()

    app = Battlefield(100, 100, BUTTON_SIZE * COLS, BUTTON_SIZE * ROWS, "Battleship Game", args.client, args.host, args.port)
    Fl.run()

