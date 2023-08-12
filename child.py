"""
Title: Child.py
Author: Noah Fry
Brief: Contains the variables and functions to manipulate children objects within the CLIFF Calculator
"""

class Child:
   def __init__(self, age, disability, blindness):
      self.age = age
      self.disability = disability
      self.blindness = blindness
      self.medKid = []
      self.netChildCareExp = 0
      self.childcareExp = 0  
      self.valHeadStart = 0  
      self.valEarlyHeadStart = 0      
      self.valPreK = 0           

   def incAge(self):
      self.age += 1
      
   def setMed(self, medKid):
        self.medKid.append(medKid)