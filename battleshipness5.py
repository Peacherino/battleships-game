
from fltk import *
import socket
from threading import Thread

ROWS = 5
COLS = 5
BUTTON_SIZE = 200
MAX_SHIPS = 5

class Battlefield(Fl_Window):
    def __init__(self, x, y, w, h, title, is_client=False, host=None, port=None):
        super().__init__(x, y, w, h, title)
        self.my_grid = []  # Your grid
        self.ship_count = 0
        self.my_turn = is_client
        self.is_client = is_client

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
            self.conn.sendall(f"{row},{col}".encode())
            print("Move sent")
            self.my_turn = False
        except Exception as e:
            print(f"Error sending move: {e}")

    def move_receive(self):
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if data:
                    row, col = map(int, data.split(","))
                    Fl.run_in_main(self.click_opponent, row, col)
            except Exception as e:
                print(f"Error receiving move: {e}")
                break

    def click_opponent(self, row, col):
        btn = self.my_grid[row][col]
        if btn.ship_placed:
            print("Opponent hit your ship!")
            btn.image(Buttons.hit_image)
        else:
            print("Opponent missed!")
            btn.image(Buttons.miss_image)
        btn.redraw()
        self.my_turn = True


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

    def on_click(self, wid):
        if self.battlefield.my_turn:  # Only allow clicks when it's the player's turn
            if self.ship_placed:
                print("Already placed a ship here. Choose another location.")
            elif self.battlefield.placable_ship():
                self.image(Buttons.ship_image)
                self.ship_placed = True
                self.battlefield.ship_counter()
            else:
                print("Maximum ships placed!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--client", action="store_true")
    args = parser.parse_args()

    app = Battlefield(100, 100, BUTTON_SIZE * COLS, BUTTON_SIZE * ROWS, "Battleship Game", args.client, args.host, args.port)
    Fl.run()

