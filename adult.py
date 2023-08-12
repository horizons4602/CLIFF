"""
Title: Adult.py
Author: Noah Fry
"""
print("")

class Adult():
    def __init__(self, age, disability, childsup, income, applicant=False, industry=None, job=None, school=None):
        self.age = age
        self.applicant = applicant
        self.disability = disability
        self.childsup = childsup
        self.income = income
        self.married = 0
        self.medAdult = []
        self.valHeadStart = 0
    
        self.ssi = False
        
        if applicant:
            self.industry = industry
            self.job = job
            self.school = school
            
    def setMed(self, medAdult):
        self.medAdult.append(medAdult)
        
        
    