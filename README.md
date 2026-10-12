This is a battleships game for two players to compete over a local network.

This program was written in python, with the GUI made using pyFLTK.

I made this while learning how TCP networking and sock streaming worked. I was really interested in the
what was happening internally over a local network for two computers to be able to communicate with
each other. This project gave me a lot of insight into that.

How it works:
The client and server communicate over a sock stream. Timer checks every 0.5 secs for the player who's turn
it is to make a move.

The network thread is seperated form the rest of the program because the program's rules themselves apply
to both players, so whoever's turn it is will then operate under the program's rules. It is two seperate
maneuvers. (have to word better)

Challenges:
My biggest issues were with getting the client and server to communicate. Things would work up until all
ships had been placed. Afterwards, the server would not be able to receive any information sent to it
from the client. I checked for the error by making a lot of print statements at separate parts in the
program to see when communication broke and then found the (FL_run_in_main had been removed a year ago?) idk.
I changed the communication to a constant checking loop to check for a changes since the server couldn't
get the client's info fast enough (I think?)

I learned a lot about debugging networking errors and a lot more about gloabal and local connections.

Some improvements I would like to make for this project are:
Making whose turn it is more clear
Making the server and client window more obvious if being run on just one computer
Including a clean exit to the program

How to run it:
Start the program using python3
Join the game with "python3 battleshipness5.py --client" on the client's side
Both players finish placing 5 ships
Players take turns finding each other's ships
Eventually one player wins and the game ends so you can no longer search for player's ships
