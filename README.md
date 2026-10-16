# Battleships
This is a battleships game for two players to compete on over a local network.

This program was written in python with a GUI made using pyFLTK.

## Screenshot of gameplay
<img width="1350" height="689" alt="battleships-game" src="https://github.com/user-attachments/assets/dcd9554b-dc47-4596-aced-30473b81ff02" />

## About Project:

I made this game while learning how TCP networking and sock streaming worked. I was quite interested in
understanding what was happening internally for two computers to be able to communicate with
each other.

Making this game gave me better insight into how data is sent and received over two devices. I also learned how to integrate networking into a GUI.

## How it works:

The client and server establish a connection and communicate using TCP sockets.

At the start of the game, each player places 5 boats on their grid and then take turns trying to bomb each other's ships until one player bombs all 5 of the other player's ships.

Timer checks every 0.5 secs for the player who's turn it is to make a move.

#### The program uses two threads -
- Main thread handles the GUI and game logic
- Networking thread listens for the end of an opponent's turn

When the network waits to receive information from the opponent during their turn, it will make the program wait until information is received, freezing the entire window and game. The separate thread places the move into a queue that doesn't interfere with the GUI, so the game window is still responsive while waiting on the other player's turn.

## Challenges:

My biggest challenges came from working on getting the client and server to communicate.

The game would work up until all ships had been placed. Afterwards, the server would not be able to properly receive any information sent from the client.

I checked for potential errors by adding several print statements in the program to track the flow of communication.

I found that the pyFLTK callback I was updating the GUI for the networking thread was no longer compatible with Python.

I added a new queue to store incoming moves and check if a new one had been added every 0.5 secs.

Building this taught me a lot about debugging networking errors, working with multiple threads, and the differences between local and global communication on a network.

## Future Improvements:

- Making whose turn it is more obvious
- Making the server and client window more distinguishable if being run on just one computer
- Including a clean way to exit to the program and break the network connection

## How to run it:

#### 1. Start the server
   python3 battleships.py

#### 2.1 (If on one computer) Join the game using a seperate terminal
  python3 battleships.py --client

#### 2.2 (If on a separate computer) Ensure second computer uses the server computer's local IP address

  Both programs will connect at 127.0.0.1 by default
  
#### 3. Gameplay
   Both players finish placing 5 ships
   Players take turns finding each other's ships
   Once one player bombs all of the other player's ships the game ends
   You can no longer continue the game once it is over

## Resources Used:

- Python
- PyFLTK
- TCP sockets
- Threads
