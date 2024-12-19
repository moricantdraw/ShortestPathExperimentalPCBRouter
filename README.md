Welcome to the experimental PCB router home repo!

Here you will find three folders, each containing relevant information to the project: 

#1 ShortestPathSimpleRouter 
While we were first designing our project, we created a simple grid-based router that plugs and plays different shortest path algorithms. 
It is able to solve some trivial PCB problems but cannot avoid crossing wires, wiring over components, or splitting into multiple layers. 
Developing this router revealed many of the problems that make autorouting so challenging and allowed us to tackle them in the new iterations. 

#2 Python graph theory functions
Once we knew what principles of graph theory we wanted to apply to our project, we studied the algorithms and wrote them out in Python. 
This process gave us the building blocks from which we could construct our pipeline. 

#3 Algos 
Our final algorithms were written with the intention of being used in the Tscircuits Autorouting repository: https://github.com/tscircuit/autorouting?tab=readme-ov-file
To test it, follow the setup instructions in their repository to run it locally on your device, then take our Astar folder or our Maxflow folder and drop it into their algos folder and run as expected. 
These algos were written in TypeScript to ensure compatibility with their host repository, and multiple modifications to each algorithm were made to allow for consistent flow and translation to TypeScript. 

Happy testing! 
