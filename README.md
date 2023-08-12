# CLIFF

"""
Notes on the CLIFF calculator
Noah Fry, Maximus Meadowcroft


- The general loop and app are started in main.py. This is where all user input should be taken. 
After the initial eligibility inputs, the datasets are processed. This is the longest loop as the datasets are hard to open and load. 
- As users are created and id's are processed, we can use specific datasets that are stored locally on the user's device or computer to make runtime even faster. 
- The more the app is used, the faster it will become. 

- Right now, the conclusion of main.py will save all of the graphs plotted from the data after printing out the data in readable list format. 
- As opposed to the Atlanta Reserve calculator, and similar, this CLIFF calculator uses quick list interpretation to speed up the program and store data. 
rather than using a dataset that is updated and manipulated in every function. This would've been incredibly slow. Python makes this happen in optimal linear time. 

- Most of our code is object oriented, and are variables are stored in the large family object. These functions will manipulate data from datasets in the family object 
so that we can access them quickly and preload information. child.py and adult.py are also objects that are individual to each person in the "family" object. Each of these 
are stored in their respective adult and child object lists that we use to manipulate individual person data/information. 


- The main loop starts with finding the total expense that the family is expected to pay based on each criteria (children, income, state, county, etc). 
- Once we know the expense that the family is expected to pay, we can apply benefits to find if the family will have to pay. This is tracked per year, with the 
yeardata being the newest year data that the respective csv file holds (if the newest data is from 2022, that is the data we use, no averaging data). 

- Each of these benefits relies on information from the other benefit. Some will track the total amount of tanf (for example) into the income calculation and sway the 
result of the next benefit to track. Because of this, we needed to start with ccdf. 

** Once ccdf is done, we can do fates, then ssi and ssdi, then tanf, then most of the state specific benefits (LIHeap, and RAP)

- We automated most of the state functions to work off of one ccdf function to reduce code bloating and complexity. 

- Once most of the functions are finished, we can clear more bloating as well. 


just run python main.py in the cliff directory
"""
