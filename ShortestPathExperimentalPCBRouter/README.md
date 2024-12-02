# Shortest Path Experimental PCB Router
Hi all! This is a very informal readme just so y'all know what I was thinking as we start to work on this. 
The main file we'll be running is PCBRouter.py. It contains a class that creates a matrix to resemble our PCB board. 

PCBRouter.py collects user input. You will be prompted to tell it what algorithm to use and also what points you want to connect. It uses the algorithm of choice to connect the first two locations and occupy those spaces within the matrices. Then, it iterates through this process until all the points are connected or until the remaining points can't be connected. 

It should return the path that was taken to connect each pair of points. 

As said before, PCBRouter.py runs a chosen algorithm. This means that we can create separate files with the other algorithms as functions and have them be compatible with PCBRouter.py. 

Some potential issues that I'm thinking about include:
What if we want a node to have multiple vertices? 
Do we need to scale this up, and if so, by how much? 
Is there a way we want to represent diagonals? 
