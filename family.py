"""
Title: Family.py
Author: Noah Fry, Max Meadowcroft
Brief: Holds variables and functions for handling the family class heirarchy
"""

import pandas as pd
from adult import Adult
from child import Child
import re

from flask import Flask, render_template, request, redirect, url_for, session

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.subplots as sp
import plotly.offline as pyo
import json
 
app = Flask(__name__)


us_state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
}


"""with open('data/json/county_state.json', 'r') as f:
    county_state_dict = json.load(f)"""

class Family():
    def __init__(self, curr_year, state, county, houseStatus, file_status, ccdfEligible):
        self.curr_year = curr_year
        self.state = state
        self.county = county
        self.adults = []
        self.children = []
        self.houseStatus = houseStatus
        self.aliceType = 'survival'
        self.total_earned_income = 0
        self.inflationRate = 0.02
        self.utilities = []
        
        
        TaxCSV = pd.read_csv('data/csv/_fedinctaxData.csv')
        self.TaxCSV = TaxCSV[TaxCSV["FilingStatus"] == file_status]
        self.foodcostCSV = pd.read_csv('data/csv/exp.foodData.USDA.csv', low_memory=False)
        self.foodcostCSV = self.foodcostCSV.loc[(self.foodcostCSV["State"] == self.state) & (self.foodcostCSV["County_State"].str.contains(self.county, case=False))]
        self.foodcostCSV = self.foodcostCSV[self.foodcostCSV["yearofdata"] == self.foodcostCSV["yearofdata"].max()]
        
        self.stateFIPS = self.foodcostCSV['stateFIPS'].iloc[0]
        self.countyFIPS = self.foodcostCSV['stcountyfips2010'].iloc[0]        
        
        mealCSV = pd.read_csv('data/csv/exp.foodData.schoolMeals.csv', low_memory=False)
        tmp = '0'
        if self.state == 'AK' or self.state == 'HI':
            tmp = '1'
        else: None
        mealCSV = mealCSV[mealCSV['AKorHI'] == tmp]
        mealCSV = mealCSV[mealCSV["yearofdata"] == mealCSV["yearofdata"].max()]
        self.mealCSV = mealCSV.drop(columns=['AKorHI'])

        rentCSV = pd.read_csv('data/csv/exp.housingData.csv', low_memory=False)
        dropList = ['ExpenseName', 'stateFIPS', 'countyFIPS', 'townFIPS', 'countyortownpop', 'GEOID','stcountyfips2010']
        rentCSV = rentCSV.drop(columns=dropList)
        rentCSV = rentCSV[rentCSV["stateAbbrev"] == self.state]
        rentCSV = rentCSV[rentCSV["countyortownName"].str.contains(self.county, case=False)]
        self.rentCSV = rentCSV[rentCSV["yearofdata"] == rentCSV["yearofdata"].max()]
        
        self.expChildCareAlice = []
        self.expChildCare = []
        childCSV = pd.read_csv('data/csv/exp.childcareData.ALICE.csv', low_memory=False)
        childCSV = childCSV[childCSV['stcountyfips2010'] == self.countyFIPS]
        self.childCSV = childCSV[childCSV["yearofdata"] == childCSV["yearofdata"].max()]
        
        
        techCSV = pd.read_csv('data/csv/exp.techData.ALICE.csv')
        self.techCSV = techCSV[techCSV['yearofdata'] == techCSV["yearofdata"].max()]
       
        transCSV = pd.read_csv('data/csv/exp.transportationData.ALICE.csv', low_memory=False)
        self.transCSV = transCSV[transCSV['stcountyfips2010'] == self.countyFIPS]
        
        healthCareCSV = pd.read_csv('data/csv/exp.healthcareData.ALICE.csv', low_memory=False)
        self.healthCareCSV = healthCareCSV[healthCareCSV['stcountyfips2010'] == self.countyFIPS]
        
        self.expHealthFamilyALICE, self.expHealthCareEmployer, self.premiumEmployer, self.premiumMedicare, self.oopNotmedicare, self.oopMedicare, self.oopAdd_for_elderlyordisabled = [], [], [], [], [], [], []
        
        medCSV = pd.read_csv('data/csv/exp.healthcareData.Medicaid.csv', low_memory=False)
        self.medCSV = medCSV[medCSV['stateFIPS'] == float(self.stateFIPS)]
        
        slcsmedCSV = pd.read_csv('data/csv/exp.healthcareData.healthexchange.csv', low_memory=False)
        self.slcsmedCSV = slcsmedCSV[slcsmedCSV['stateFIPS'] == float(self.stateFIPS)]
        
        
        tanCSV = pd.read_csv('data/csv/_tanfData.csv')
        tanCSV = tanCSV[tanCSV['stateFIPS'] == self.stateFIPS]
        if str(self.houseStatus) == 'R':
            self.tanCSV = tanCSV[tanCSV['ownorrent'] == 'rent']
        if str(self.houseStatus) == 'O':
            self.tanCSV = tanCSV[tanCSV['ownorrent'] == 'own']
        
        
        self.minimum_wage = {"AK": 10.85, "AR": 11.00, "AZ": 13.85, "CA": 15.50, "CO": 13.65, "CT": 14.00, "DC": 16.50, "DE": 11.75, "FL": 11.00, "HI": 12.00, "IL": 13.00, "MA": 15.00, "MD": 13.25, "ME": 13.80,"MI": 10.10,"MN": 10.59,"MO": 12.00,"MT": 9.95,"NE": 10.50,"NJ": 14.13,"NM": 12.00,"NV": 10.50,  "NY": 14.20,"OH": 10.10,"OR": 13.50,"PR": 8.50,  "RI": 13.00,"SD": 10.80,"VA": 12.00,"VT": 13.18,"WA": 15.74,"WV": 8.75,"VI": 10.50,  "GU": 9.25,  "AL": 7.25,  "GA": 7.25,"LA": 7.25,"IA": 7.25,"MS": 7.25,"ID": 7.25,"SC": 7.25,"IN": 7.25,"TN": 7.25,"KS": 7.25,"KY": 7.25,"NC": 7.25,"ND": 7.25,"NH": 7.25,"OK": 7.25,"PA": 7.25,"TX": 7.25,"UT": 7.25,"WI": 7.25,"WY": 7.25}
        self.year_work_hours = 2_080 # Average full time job hours a year
        self.df_ccdf = pd.read_csv(f'data/csv/_ccdfData_{self.state}.csv')
        self.df_tuition = pd.read_csv('data/csv/jobs/tuition_cost.csv')
        self.ccdfEligible = ccdfEligible
        if "countyortownName" in self.df_ccdf.columns:
            self.df_ccdf = self.df_ccdf[self.df_ccdf["countyortownName"].str.contains(self.county, case=False)]
        
    # Add a adult to the family
    def add_adult(self, adult):
        if isinstance(adult, Adult):
            self.adults.append(adult)

    # Add a child to the family
    def add_child(self, child):
        if isinstance(child, Child):
            self.children.append(child)
        
    # Calculate pay based on minimum wage and 40 hours a week by default
    def calculate_pay_minimum(self):
        return self.minimum_wage[str(self.state)] * self.year_work_hours
    
    def taxRate(self):
        for i in range(100):
            #finds the iteration with the correct income/copay bins
            bin_column = f"IncomeBin{i}Max"
            tax_column = f"TaxRate{i}"
            
            if i == 0: continue
            else:
                if self.total_earned_income > self.TaxCSV[bin_column].values[0]:continue
                
                else:
                    keep = ['ruleYear', bin_column, tax_column, "baseAmount_SSDI", "SSDI_taxable_test", "Standard"]
                    self.TaxCSV = self.TaxCSV[keep]
                    break
                
    @staticmethod
    def getThriftBin(age):
        """Will find the bin list for the given age of the family member
           For use with the food cost function.
        
        Args:
            age (int): The age of the family member

        Returns:
            str: The correct bin string for the csv and the given age
        """
        if age == 1:
            return "Age_1_year_Thrifty"
        elif 2 <= age <= 3:
            return "Age_2to3_years_Thrifty"
        elif 4 <= age <= 5:
            return "Age_4to5_years_Thrifty"
        elif 6 <= age <= 8:
            return "Age_6to8_years_Thrifty"
        elif 9 <= age <= 11:
            return "Age_9to11_years_Thrifty"
        elif 12 <= age <= 13:
            return "Age_12to13_years_Thrifty"
        elif 14 <= age <= 19:
            return "Age_14to19_years_Thrifty"
        elif 20 <= age <= 50:
            return "Age_20to50_years_Thrifty"
        elif 51 <= age <= 70:
            return "Age_51to70_years_Thrifty"
        else:
            return "Age_71plus_Thrifty"  
    
    @staticmethod
    def getModBin(age):
        """Will find the bin list for the given age of the family member
           For use with the food cost function.
        
        Args:
            age (int): The age of the family member

        Returns:
            str: The correct bin string for the csv and the given age
        """
        if age == 1:
            return "Age_1_year_Moderate"
        elif 2 <= age <= 3:
            return "Age_2to3_years_Moderate"
        elif 4 <= age <= 5:
            return "Age_4to5_years_Moderate"
        elif 6 <= age <= 8:
            return "Age_6to8_years_Moderate"
        elif 9 <= age <= 11:
            return "Age_9to11_years_Moderate"
        elif 12 <= age <= 13:
            return "Age_12to13_years_Moderate"
        elif 14 <= age <= 19:
            return "Age_14to19_years_Moderate"
        elif 20 <= age <= 50:
            return "Age_20to50_years_Moderate"
        elif 51 <= age <= 70:
            return "Age_51to70_years_Moderate"
        else:
            return "Age_71plus_Moderate"
    
    def getLowBin(self, size):
        if size == 1:
            return self.foodCostCSV['Thrifty_reference_family'].iloc[0]/4 * 1.2
        if size == 2:
            return self.foodCostCSV['Thrifty_reference_family'].iloc[0]/4 * 1.1
        if size == 3:
            return self.foodCostCSV['Thrifty_reference_family'].iloc[0]/4 * 1.05
        if size == 4: 
            return self.foodCostCSV['Thrifty_reference_family'].iloc[0]/4
        if size == 5 or size == 6:
            return self.foodCostCSV['Thrifty_reference_family'].iloc[0]/4 * 0.95
        else: 
            return self.foodCostCSV['Thrifty_reference_family'].iloc[0]/4 * 0.9
    
    def food_cost(self, year):
        """Will return the total food cost for the family for 1 year based on their age. 

        Returns:
            int: totalFoodCost
        
        ToDo:
            Implement tax data and find calculate the total cost for life based on their age. 
            Possibly have a loop in the main function that will calculate based on the age we send.
            Add the CLD % adjusted cost as listed in the CLD Documentation. 
        """
        familyList = self.adults + self.children
        
        self.foodcostCSV["famsize"] == len(familyList)
        yearofData = self.foodcostCSV["yearofdata"].iloc[0]
        #setup the df for easy reading and manipulation
        #We are using the standard minimum food cost values for each individual, as this was how the CLD was being used
        #Calculates the "thrifty" cost for each individual's age range for the year (*12)
        binList = []
        totalFoodCost = 0
        
        if self.aliceType == 'survival': 
            for i in range(len(familyList)):
                binList.append(self.getThriftBin(familyList[i].age))
            for bin in binList:
                tmp = self.foodcostCSV[bin].iloc[0]
                totalFoodCost += tmp
                
        if self.aliceType == 'stability':
            for i in range(len(familyList)):
                binList.append(self.getModBin(familyList[i].age))
            for bin in binList:
                tmp = self.foodcostCSV[bin].iloc[0]
                totalFoodCost += tmp
            
        if self.aliceType == 'survivalforcliff':
            totalFoodCost = self.foodcostCSV[self.getLowBin(len(familyList))]
            totalFoodCost *= len(familyList)
            
        totalFoodCost = totalFoodCost * (1 + self.inflationRate) ** (year - yearofData)
        return round(totalFoodCost, 3)
        
    def school_meal_cost(self, year):
        """ These functions are used in the CLD Manual for calculating all monthly expenses. 
            I believed that these were necessary to calculate the total benefit, though the PRD states to only use certain functions. 
            These new functions are included and used, I just didn't feel the need to delete these.

        Returns:
            int: schoolmealcost for children
        ToDo:
            Add in inflation rate for final value. This is the total for 1 year instance with the given age
            In the main.py function we need to have an iterator that will iterate each child's age. 
        """
        yearofData = self.foodcostCSV["yearofdata"].iloc[0]
        schoolMealCostPerDay = self.mealCSV['dailyvalue.schoolLunch'].iloc[0] + self.mealCSV['dailyvalue.schoolBreakfast'].iloc[0]
        #The CLD follows that all children start preK at 4
        numSchoolDays = 180 #average across nation
        numEl = len([child for child in self.children if child.age in range(4, 18)])
        schoolMealCostPerYear = schoolMealCostPerDay * numSchoolDays * numEl
        
        if self.aliceType == "survival" or self.aliceType =="stability":
            schoolMealCostPerYear = schoolMealCostPerYear * (1 + (.055-self.inflationRate)) ** (year - yearofData)
        elif self.aliceType == "survivalforcliff":
            schoolMealCostPerYear = schoolMealCostPerYear * (1 + self.inflationRate) ** (year - yearofData)
        
        return round(schoolMealCostPerYear, 2)
    
    def rent_cost(self, year):
        """Will find the total rent cost for the given year based on the averages from the csv file

        Args:
            year (int): year of the data to be found

        Returns:
            int: the total amount of housing cost for the year
        """ 
        self.rentCSV = self.rentCSV.loc[(self.rentCSV["numkids"] == len(self.children)) & (self.rentCSV["numadults"] == len(self.adults))]
        yearofData = self.rentCSV['yearofdata'].iloc[0]
        #we take the rent - utlities
        housing = self.rentCSV['expense.rent'] 
        rent = self.rentCSV['expense.rent'] #- self.rentCSV['expense.utilities']
        utilities = self.rentCSV['expense.utilities']
        rentStability =  self.rentCSV['expense.rent.stability'] #- self.rentCSV['expense.utilities']
        
        if self.aliceType == 'survival': 
            rent = rent * (1 + (0.032 - self.inflationRate)) ** (year - yearofData)
            utilities = utilities * (1 + (0.032 - self.inflationRate)) ** (year - yearofData)
            
        if self.aliceType == 'stability':
            rent = rentStability * (1 + (0.032 - self.inflationRate)) ** (year - yearofData)
            utilities = utilities * (1 + (0.032 - self.inflationRate)) ** (year - yearofData)
            
        if self.aliceType == 'survivalforcliff':
            rent = rent * (1 + (self.inflationRate)) ** (year - yearofData)
            utilities = utilities * (1 + (self.inflationRate)) ** (year - yearofData)
            
        self.utilities.append(int(utilities.iloc[0]))
        rent = float(rent.iloc[0])
        return round(rent, 2)
    
    def childcareExp_ALICE(self, year):
        """This function will find the total amount of childcare estimated to be spent. 

        Args:
            data (idk): idk
            schoolagesummercare (str): FT

        Returns:
            int: total amount of childcare to be spent
            
        """
        yearofdata = self.childCSV["yearofdata"].iloc[0]
        toddler, preschooler, child = 0, 0, 0
        
        #We assume that schoolagesummercare is always going to be ft for the summer regardless of childs age.
        
        # Determine Expense based on Age of Children
        if self.aliceType == "survival" or self.aliceType == "survivalforcliff":
            expInfant = self.childCSV['familyChildCare.infant.ftdailyrate'].iloc[0] * (70 + 180)
            expPre = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * (70 + 180)
            expKid = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * 70 * 1 + self.childCSV['licensedChildcare.4yr.ftdailyrate'].iloc[0] * 0.5 * 180
            
            for kid in self.children:
                if kid.age in range(0, 3):
                    toddler += 1
                    kid.childcareExp = self.childCSV['familyChildCare.infant.ftdailyrate'].iloc[0] * (70 + 180)
                    kid.childcareExp = kid.childcareExp * (1 + self.inflationRate) ** (year - yearofdata)
                    kid.netChildCareExp = kid.childcareExp * (1 + self.inflationRate) ** (year - yearofdata)
                elif kid.age in range(3, 5):
                    preschooler += 1
                    kid.childcareExp = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * (70 + 180)
                    kid.childcareExp = kid.childcareExp * (1 + self.inflationRate) ** (year - yearofdata)
                    kid.netChildCareExp = kid.childcareExp * (1 + self.inflationRate) ** (year - yearofdata)
                elif kid.age in range(5, 13):
                    child += 1
                    kid.childcareExp = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * 70 * 1 + self.childCSV['licensedChildcare.4yr.ftdailyrate'].iloc[0] * 0.5 * 180
                    kid.childcareExp = kid.childcareExp * (1 + self.inflationRate) ** (year - yearofdata)
                    kid.netChildCareExp = kid.childcareExp * (1 + self.inflationRate) ** (year - yearofdata)
            
            expKidAlice = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * (70 + 180) * (3 / 8)
            expChildCare = expInfant + expPre + expKid
            expChildCareAlice = expInfant + expPre + expKidAlice
            expChildCareAlice = expChildCareAlice*(1+(.021-self.inflationRate))**(year-yearofdata)
            expChildCare = expChildCare*(1+(.021-self.inflationRate))**(year-yearofdata)  

        # Formula for stability
        if self.aliceType == "stability":
            expInfant = self.childCSV['familyChildCare.infant.ftdailyrate'].iloc[0] * (70 + 180)
            expPre = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * (70 + 180)
            expKidAlice = self.childCSV['familyChildCare.4yr.old.ftdailyrate'].iloc[0] * (70 + 180) * (3 / 8)
            
            expKid = self.childCSV['licensedChildcare.4yr.ftdailyrate'].iloc[0] * 70 * 1 + self.childCSV['licensedChildcare.4yr.ftdailyrate'].iloc[0] * 0.5 * 180
            expChildCare = expInfant + expPre + expKid
            expChildCareAlice = expInfant + expPre + expKidAlice

        retVar = expInfant * toddler + expPre * preschooler + expKidAlice * child
        retVar = float(retVar)
        # Calculate Total ALICE Childcare across all ages
        self.expChildCareAlice.append(retVar)
        self.expChildCare.append(expInfant * toddler + expPre * preschooler + expKid * child)


        return round(retVar, 2)
    
    def techExp_ALICE(self, year):
        """Will generate the total amount spent on tech for the given year

        Args:
            year (int): given year to be used

        Returns:
            int: total amount spent on tech for the given year
        """
        yearofdata = self.techCSV['yearofdata'].iloc[0]
        self.techCSV = self.techCSV[self.techCSV['numadults'] == len(self.adults)]
        
        if self.aliceType == 'survival' or self.aliceType == 'survivalforcliff':
            expTech = self.techCSV['expense.smartphone'].iloc[0]
            
        if self.aliceType == 'stability':
            expTech = self.techCSV['expense.smartphone'].iloc[0] - self.techCSV['expense.broadband'].iloc[0]
            
            
        if self.aliceType == 'survival' or self.aliceType == 'stability':
            expTech = expTech * (1 + (0 - self.inflationRate)) ** (year - yearofdata)
        
        if self.aliceType == 'survivalforcliff':
            expTech = expTech * (1 + self.inflationRate) ** (year - yearofdata)
            
        return round(float(expTech), 2)
    
    def transExp_ALICE(self, year, pub):
        """Generates the total amount spent on transportation by the age range and the alice determinations

        Args:
            year (int): the year to be used
            pub (bool): whether the family uses public transportation or not

        Returns:
            int: the total estimated cost of all transportation for the given year
        """
        famlist = self.adults + self.children
        self.transCSV = self.transCSV[self.transCSV['famsize'] == (len(famlist))]
        yearofdata = self.transCSV['yearofdata'].iloc[0]
        
        numKid, numAdult, numOld, numPublic = 0, 0, 0, 0
        for person in famlist:
            if person.age in range(0, 19):
                numKid += 1
            if person.age in range(19, 65):
                numAdult += 1
            if person.age >= 65:
                numOld += 1
                
        for person in famlist:
            if person.age > 5:
                numPublic += 1
                
        expCar, expTransportation = 0, 0
        if self.aliceType == 'survival':
            expCar = ((self.transCSV['miles.adult'].iloc[0] * numAdult) + (self.transCSV['miles.kids'].iloc[0] * numKid) + (self.transCSV['miles.senior'].iloc[0] * numOld)) * self.transCSV['car.permile.survival'].iloc[0] + self.transCSV['car.expense.survival'].iloc[0]
            if pub:
                expTransportation = (self.transCSV['miles.adult'].iloc[0] * numPublic)
            else:
                expTransportation = expCar    
        if self.aliceType == 'stability':
            expCar = ((self.transCSV['miles.adult'].iloc[0] * numAdult) + (self.transCSV['miles.kids'].iloc[0] * numKid) + (self.transCSV['miles.senior'].iloc[0] * numOld)) * self.transCSV['car.permile.stability'].iloc[0] + self.transCSV['car.expense.stability'].iloc[0]
            if pub:
                expTransportation = (self.transCSV['miles.adult'].iloc[0] * numPublic) + (expCar * 1/3)
            else:
                expTransportation = expCar   
                
        if self.aliceType == 'survivalforcliff':
            expCar = ((self.transCSV['miles.adult'].iloc[0] * numAdult) + (self.transCSV['miles.kids'].iloc[0] * numKid) + (self.transCSV['miles.senior'].iloc[0] * numOld)) * self.transCSV['car.permile.survival'].iloc[0] + self.transCSV['car.expense.survival'].iloc[0]
            if pub:
                expTransportation = (self.transCSV['public.trans'].iloc[0] * numPublic)
            else:
                expTransportation = expCar   
            
        if self.aliceType == 'survival' or self.aliceType == 'stability':      
            expTransportation = expTransportation*(1 + (0.022 - self.inflationRate)**(year - yearofdata))
            
        if self.aliceType == 'survivalforcliff':
            expTransportation = expTransportation*(1 + (self.inflationRate)**(year - yearofdata))
        
        return round(float(expTransportation), 2)
    
    def wicExp(self, year):
        wicCSV = pd.read_csv("data/csv/exp.foodData.WIC.csv")
        
        infNum, kidNum, mom = 0, 0, 0
        for i in self.children:
            if i.age == 0:
                infNum += 1
            if 1 <= i.age < 5:
                kidNum += 1
            
        if infNum > 1 or kidNum > 1:
            mom = 1
            
        expWic = (wicCSV['value.infant'].iloc[0] * infNum) + (wicCSV['value.kidsage1to4'].iloc[0] * kidNum) + (wicCSV['value.women'].iloc[0] * mom)
        
        if self.aliceType == 'survival' or self.aliceType == 'stability':      
            expWic = expWic*(1 + (0.055 - self.inflationRate)**(year - wicCSV['yearofdata'].iloc[0]))
            
        if self.aliceType == 'survivalforcliff':
            expWic = expWic*(1 + self.inflationRate)**(year - wicCSV['yearofdata'].iloc[0])
            
        expWic = round(float(expWic*12), 2)
        return expWic
                
    def expHealthCareData(self, year):
        yearofdata = self.healthCareCSV['yearofdata'].max()
        old = 0
        for adult in self.adults:
            if adult.age > 65:
                old += 1
        famSize = len(self.adults) + len(self.children)
        adult = len(self.adults) - old
        famsizeALICE = len(self.adults) - old
        
        import expHealthFunc
        #Steps 1-4
        expHealthCareEmployer = expHealthFunc.calculate_exp_healthcare_employer(self.healthCareCSV, famSize)
        expHealthCareEmployerALICE = expHealthFunc.calculate_exp_healthcare_employer_ALICE(self.healthCareCSV, famSize)
        premiumEmployer = expHealthFunc.calculate_premium_employer(self.healthCareCSV, famSize)
        premiumEmployerALICE = expHealthFunc.calculate_premium_employer_ALICE(self.healthCareCSV, famSize)
        
        # Step 5
        premiumMedicare = self.healthCareCSV['annual_premium_partB']

        # Step 6
        oopNotmedicare = self.healthCareCSV['annualOOP_survival']
        oopStability = self.healthCareCSV['annualOOP_stability']
        
        oopMedicare = self.healthCareCSV['annualOOP_partB']
        oopAdd_for_elderlyordisabled = self.healthCareCSV['annualOOP.chronicconditions']
        
        if self.aliceType == 'survival' or self.aliceType == 'survivalforcliff':
            healthFamliyALICE = (adult * oopNotmedicare) + old * (oopMedicare + oopAdd_for_elderlyordisabled + premiumMedicare)
            expHealthFamilyALICE = premiumEmployerALICE * 1.3 + healthFamliyALICE
        
        if self.aliceType == 'stability':
            healthFamliyALICE = (adult * oopStability) + old * (oopMedicare + oopAdd_for_elderlyordisabled + premiumMedicare)
            expHealthFamilyALICE = premiumEmployerALICE + healthFamliyALICE
        
        # Step 7: Adjust for inflation
        if self.aliceType in ['survival', 'stability']:
            self.expHealthFamilyALICE.append(float(expHealthFamilyALICE.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.expHealthCareEmployer.append(float(expHealthCareEmployer.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.premiumEmployer.append(float(premiumEmployer.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.premiumMedicare.append(float(premiumMedicare.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.oopNotmedicare.append(float(oopNotmedicare.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.oopMedicare.append(float(oopMedicare.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.oopAdd_for_elderlyordisabled.append(float(oopAdd_for_elderlyordisabled.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
        
        if self.aliceType == 'survivalforcliff':
            self.expHealthFamilyALICE.append(float(expHealthFamilyALICE.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.expHealthCareEmployer.append(float(expHealthCareEmployer.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.premiumEmployer.append(float(premiumEmployer.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.premiumMedicare.append(float(premiumMedicare.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.oopNotmedicare.append(float(oopNotmedicare.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.oopMedicare.append(float(oopMedicare.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))
            self.oopAdd_for_elderlyordisabled.append(float(oopAdd_for_elderlyordisabled.iloc[0] * (1 + (self.inflationRate)) ** (year - yearofdata)))

    def expHealthCareMedicaid(self, year):
        yearofdata = self.medCSV['yearofdata'].iloc[0]
        medAdult = self.medCSV['expense.medicaidAdults'].iloc[0]
        medKid = self.medCSV['expense.medicaidChildren'].iloc[0]
        
        medAdult = medAdult*(1 + (0.033 - self.inflationRate))**(year - yearofdata)
        medKid = medKid*(1+ (0.033 - self.inflationRate)) ** (year - yearofdata)
        
        for adult in self.adults:
            adult.setMed(medAdult)
            
        for kid in self.children:
            kid.setMed(medKid)
        
    def expHealthCareSLCS(self, year):
        yearofdata = self.slcsmedCSV['yearofdata'].iloc[0]
        fam = self.children + self.adults
        expslcs = 0
        for person in fam:
            if person.age in range(0, 15):
                expslcs += self.slcsmedCSV['age.0-14'].iloc[0]
            if person.age in range(15, 64):
                expslcs += self.slcsmedCSV[f'age.{int(person.age)}'].iloc[0]
            else:
                expslcs += self.slcsmedCSV['age.64+'].iloc[0]
                
        if self.aliceType == 'survival' or self.aliceType == 'stability':
            expslcs = expslcs * (1 + (0.033 - self.inflationRate))**(year - yearofdata)
        
        if self.aliceType == 'survivalforcliff':
            expslcs = expslcs * (1 + (self.inflationRate))**(year - yearofdata)
        expslcs = float(expslcs)
        return round(expslcs, 2)
        
    @staticmethod
    def calulate_pay(salary, hours, weeks):
        return salary * hours * weeks
    
    def qualify_ccdf(self):
        famsize = len(self.adults) + len(self.children)
        income = self.calculate_pay_minimum()
        
        family_size_df = self.df_ccdf[self.df_ccdf['famsize'] == famsize]

        initial_eligibility = family_size_df['InitialEligibility'].values[0]
        
        if income <= initial_eligibility:
            return True
        else:
            return False
   
    def calculateHeadStarts(earlyHeadStart, kid, ftorpt):
        """
        Calculate the total value of Head Start and Early Head Start for each child.
        This will be used to find the netexpChildcare to be used for ccdf and further. 
        """
        None
        
    def calculatePreK(kid, ftorpt):
        None
         
    def calculateFATESCCDFF(netExpChildCare):
        None
    
    def calculateValCCDF(self, netExpChildCare):
        famsize = len(self.adults) + len(self.children)
        self.df_ccdf = self.df_ccdf[self.df_ccdf['famsize'] == famsize]
        self.df_ccdf = self.df_ccdf[self.df_ccdf['ruleYear'] == self.df_ccdf['ruleYear'].max()]
        df_ccdf = self.df_ccdf.copy()
        inf, child, childcareInf, childcareChild = 0, 0, 0, 0
        netChildCareInf, netChildCareChild = 0, 0
        
        for kid in self.children:
            if kid.age in range(0, 5) and kid.childcareExp != 0:
                inf += 1
                netChildCareInf += kid.netChildCareExp
                childcareInf += kid.childcareExp
                
            if kid.age in range(5, 13) and kid.childcareExp != 0:
                child += 1
                netChildCareChild += kid.netChildCareExp
                childcareChild += kid.childcareExp

        childNumDaysCare, infNumDaysCare = 0, 0
        if inf > 0:
            infNumDaysCare = netChildCareInf / childcareInf * (70 + 180)

        if child > 0:
            childNumDaysCare = netChildCareChild / childcareChild * (0.5 * (70 + 180))
        kidsInCare = inf+child
        
        try:
            df_ccdf = df_ccdf[df_ccdf['numkidsInCare'] == kidsInCare]
        except:
            pass
        
        income = self.total_earned_income
        cop = 0
        if kidsInCare > 0: 
            if self.state == 'VT':
                import ccdfStateCalculation as cc
                netVal = []   
                netVal = cc.ccdfVT(df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                self.ccdfEligible = netVal[0]
                totCopay = netVal[1]
                return totCopay
            
            if self.state == 'OH':
                import ccdfStateCalculation as cc
                netVal = []   
                netVal = cc.ccdfOH(df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                self.ccdfEligible = netVal[0]
                totCopay = netVal[1]
                return totCopay
            
            if self.state == 'MO':
                import ccdfStateCalculation as cc
                netVal = []   
                netVal = cc.ccdfMO(df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                self.ccdfEligible = netVal[0]
                totCopay = netVal[1]
                return totCopay
            
            if self.state == 'MD':
                import ccdfStateCalculation as cc
                netVal = []   
                netVal = cc.ccdfMD(df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                self.ccdfEligible = netVal[0]
                totCopay = netVal[1]
                return totCopay
            
            if self.state == 'IA':
                import ccdfStateCalculation as cc
                netVal = []   
                netVal = cc.ccdfIA(df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                self.ccdfEligible = netVal[0]
                totCopay = netVal[1]
                return totCopay
            
            else:
                for i in range(123):
                    #finds the iteration with the correct income/copay bins
                    bin_column = f"Bin{i}Max"
                    copay_column = f"CopayBin{i}"
                    if i == 0: continue
                    else:                        
                        if bin_column not in self.df_ccdf.columns:
                            copay_column = f"CopayBin{i-1}"
                           
                            cop = self.df_ccdf[copay_column].iloc[0]
                            
                            import ccdfStateCalculation as cc
                            # Create a dictionary mapping state abbreviations to None
                            state_function_map = {
                                "AL": cc.ccdfAL, "AK":  cc.ccdfAK, "AZ":  cc.ccdfAZ, "AR":  cc.ccdfAR, "CA":  cc.ccdfCA,
                                "CO":  cc.ccdfAR, "CT":  cc.ccdfAR, "DE":  cc.ccdfAR, "FL":  cc.ccdfAZ, "GA":  cc.ccdfAR,
                                "HI":  cc.ccdfAR, "ID":  cc.ccdfAK, "IL":  cc.ccdfCA, "IN":  cc.ccdfIN, "IA":  cc.ccdfIA,
                                "KS":  cc.ccdfAK, "KY":  cc.ccdfKY, "LA":  cc.ccdfAZ, "ME":  cc.ccdfAR, "MD":  cc.ccdfMD,
                                "MA":  cc.ccdfMA, "MI":  cc.ccdfMI, "MN":  cc.ccdfMN, "MS":  cc.ccdfAK, "MO":  cc.ccdfMO,
                                "MT":  cc.ccdfAR, "NE":  cc.ccdfAR, "NV":  cc.ccdfNV, "NH":  cc.ccdfAR, "NJ":  cc.ccdfAK,
                                "NM":  cc.ccdfNM, "NY":  cc.ccdfNY, "NC":  cc.ccdfNC, "ND":  cc.ccdfND, "OH":  cc.ccdfOH,
                                "OK":  cc.ccdfAK, "OR":  cc.ccdfAK, "PA":  cc.ccdfPA, "RI":  cc.ccdfAR, "SC":  cc.ccdfSC,
                                "SD":  cc.ccdfAK, "TN":  cc.ccdfTN, "TX":  cc.ccdfTX, "UT":  cc.ccdfUT, "VT":  cc.ccdfVT,
                                "VA":  cc.ccdfAR, "WA":  cc.ccdfAK, "WV":  cc.ccdfAZ, "WI":  cc.ccdfWI, "WY":  cc.ccdfWY
                            }
                            netVal = []
                            
                            if self.state in state_function_map:
                                func = state_function_map[self.state]
                                netVal = func(self.df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                                
                                self.ccdfEligible = netVal[0]
                                totCopay = netVal[1]
                                return totCopay
                            
                        else:
                            try:
                                if income > self.df_ccdf[bin_column].values[0]:
                                    continue
                                
                                else: 
                                    cop = self.df_ccdf[copay_column].values[0]
                                    import ccdfStateCalculation as cc    
                                    # Create a dictionary mapping state abbreviations to None
                                    state_function_map = {
                                        "AL": cc.ccdfAL, "AK":  cc.ccdfAK, "AZ":  cc.ccdfAZ, "AR":  cc.ccdfAR, "CA":  cc.ccdfCA,
                                        "CO":  cc.ccdfAR, "CT":  cc.ccdfAR, "DE":  cc.ccdfAR, "FL":  cc.ccdfAZ, "GA":  cc.ccdfAR,
                                        "HI":  cc.ccdfAR, "ID":  cc.ccdfAK, "IL":  cc.ccdfCA, "IN":  cc.ccdfAR, "IA":  cc.ccdfIA,
                                        "KS":  cc.ccdfAK, "KY":  cc.ccdfAZ, "LA":  cc.ccdfAZ, "ME":  cc.ccdfAR, "MD":  cc.ccdfMD,
                                        "MA":  cc.ccdfMA, "MI":  cc.ccdfMI, "MN":  cc.ccdfMN, "MS":  cc.ccdfAK, "MO":  cc.ccdfMO,
                                        "MT":  cc.ccdfAR, "NE":  cc.ccdfAR, "NV":  cc.ccdfNV, "NH":  cc.ccdfAR, "NJ":  cc.ccdfAK,
                                        "NM":  cc.ccdfNM, "NY":  cc.ccdfNY, "NC":  cc.ccdfNC, "ND":  cc.ccdfND, "OH":  cc.ccdfOH,
                                        "OK":  cc.ccdfAK, "OR":  cc.ccdfAK, "PA":  cc.ccdfPA, "RI":  cc.ccdfAR, "SC":  cc.ccdfSC,
                                        "SD":  cc.ccdfAK, "TN":  cc.ccdfTN, "TX":  cc.ccdfTX, "UT":  cc.ccdfUT, "VT":  cc.ccdfVT,
                                        "VA":  cc.ccdfAR, "WA":  cc.ccdfAK, "WV":  cc.ccdfAZ, "WI":  cc.ccdfWI, "WY":  cc.ccdfWY
                                    }
                                    netVal = []
                                    
                                    if self.state in state_function_map:
                                        func = state_function_map[self.state]
                                        netVal = func(self.df_ccdf, famsize, cop, income, kidsInCare, infNumDaysCare, childNumDaysCare)
                                        self.ccdfEligible = netVal[0]
                                        totCopay = netVal[1]
                                        return totCopay
                                    
                            except:
                                self.ccdfEligible = False
                                return 0                       
        else: 
            self.ccdfEligible = False
            return 0 
        
    def calculate_childcare_for_ccdf(self, year, expChildCare, boolList):
        netExpChildCare = expChildCare
        netExpHeadStart = 0
        netExpEarlyHeadStart = 0
        
        #HeadStart
        for kid in self.children:
            if boolList[1] == False:
                None
            else:
                #EarlyHeadStart
                self.calculateHeadStarts(boolList[2], kid, ftorpt = "FT")
                netExpHeadStart += kid.valHeadStart
                netExpEarlyHeadStart += kid.valEarlyHeadStart
                kid.childcareExp = kid.childcareExp - kid.valHeadStart - kid.valEarlyHeadStart
        netExpChildCare = expChildCare - netExpHeadStart - netExpEarlyHeadStart
        
        netvalPreK = 0
        #PreK
        for kid in self.children:
            if boolList[0] == False:
                None
            else: 
                self.calculatePreK(kid, ftorpt = "FT")
                netvalPreK += kid.valPreK
                kid.childcareExp = kid.childcareExp - kid.valPreK
                
        #Now that the csv is ready, we can store some values we will need for the state call. 
        netExpChildCare = netExpChildCare - netvalPreK
        ccdf, remCosts = 0, 0
        
        if boolList[3] == False:
            None
        else:
            ccdf = self.calculateValCCDF(netExpChildCare)
            ccdf = round(netExpChildCare - ccdf, 2)
        netExpChildCare = round(netExpChildCare - ccdf)

        #Fates
        if boolList[4] == False: 
            None
        else: 
            netValFATES = self.calculateFATESCCDFF(netExpChildCare)
            netExpChildCare = netExpChildCare - netValFATES
            
        ansList = [netExpChildCare, ccdf]
        return ansList
        
    def tuition_calculate(self, school, scholarships=0, hrs_work=20):
        school_data = self.df_tuition[self.df_tuition['name'] == school]
        if not school_data.empty:
            if school_data['state_code'].values[0] == self.state:
                year_cost = school_data['in_state_total'].values[0]
            else:
                year_cost = school_data['out_of_state_total'].values[0]
                
            # Assume that the person works hrs_work in school year and 40 during summer break (9 wks)
            year_cost = year_cost - scholarships
            
            return year_cost
            
        else:
            return "School or state code not found."
        
    def tanfBenefit(self, year):
        famsize = (len(self.adults) + len(self.children))
        self.tanCSV = self.tanCSV[self.tanCSV['famsize'] == famsize]
        yearofdata = self.tanCSV['LatestYear'].max()
        return 0
        
    def qualify_snap(self, state1, income):
        famsize = len(self.adults) + len(self.children)
        gross_income = income
        
        # Assume net income is 80% of gross income. You can replace this with actual data if you have it.
        net_income = gross_income
        
        # Assume assets as a minimum value. Replace this with actual data if you have it.
        assets = 0
        
        # Check if there is a disabled person in the family from the children and adults
        for child in self.children:
            if child.disabled == True:
                is_elderly_or_disabled = True
                break
        for adult in self.adults:
            if adult.disabled == True:
                is_elderly_or_disabled = True
                break
            else:
                is_elderly_or_disabled = False

        state_data = self.df_snap[self.df_snap['stateName'] == state1]

        # Check based on family size
        family_data = state_data[state_data['famsize'] == famsize]
        
        # Check income eligibility
        income_eligibility_column = 'GrossIncomeEligibility'
        income_eligibility = family_data[income_eligibility_column].values[0]
        
        if net_income > income_eligibility:
            return False

        # # Check asset test
        # asset_test_column = 'AssetTestFed_Elder_Dis' if is_elderly_or_disabled else 'AssetTestFed_nonelddis'
        # asset_limit = family_data[asset_test_column].values[0]
        
        # if assets > asset_limit:
        #     return False
        
        # Further conditions can be checked as needed

        return True
        
    def calculate_snap_benefit(self, state1, num_adults, num_children):
        family_size = num_adults + num_children
        state_benefits = self.df_snap[(self.df_snap['stateName'] == state1) & (self.df_snap['famsize'] == family_size)]
        if not state_benefits.empty:
            return state_benefits['MaxBenefit'].iloc[0]
        else:
            return "No data available for the given state and family size"

    def get_schools_states(self):
        return self.df_tuition.loc[self.df_tuition['state_code'] == self.state, ['name', 'in_state_tuition']]
    
    def plot_snap_benefits(self, school, major, years=20):
        tuition = self.tuition_calculate(school=school)

        major_data = self.df_careers[self.df_careers['Undergraduate Major'] == major]

        # Get the Starting and Mid-Career Median Salaries
        start_salary = major_data['Starting Median Salary'].values[0]
        mid_salary = major_data['Mid-Career Median Salary'].values[0]

        # Remove the dollar sign and commas, and convert to float
        start_salary = float(start_salary.replace(',', '').replace('$', ''))
        mid_salary = float(mid_salary.replace(',', '').replace('$', ''))

        # Calculate annual growth rate based on start and mid salaries and 20 years difference
        annual_growth_rate = ((mid_salary/start_salary)**(1/20))-1

        # Calculate the projected salary for each year
        years_list = list(range(years+1)) # 0-20 years

        # Calculate the school year and summer break salaries
        school_year_salary = self.calculate_pay(self.minimum_wage[self.state], 20, 52-9)
        summer_break_salary = self.calculate_pay(self.minimum_wage[self.state], 40, 9)
        part_time_salary = school_year_salary + summer_break_salary

        salaries = [part_time_salary if year < 4 else start_salary*(1+annual_growth_rate)**(year-4) for year in years_list]
        salaries_minimum_wage = [self.calculate_pay_minimum() for _ in years_list]  # repeat the same value for each year

        children = []
        adults = []

        for year in range(0, years + 1):
            num_adults = len(self.adults) 
            num_children = len(self.children) - sum(child.age + year >= 18 for child in self.children)

            children.append(num_children)
            adults.append(num_adults)

        # Check each year if the person is eligible for SNAP benefits
        for x in range(0, years+1):
            if self.qualify_snap(self.state, salaries[x]):
                salaries[x] = self.calculate_snap_benefit(state1=self.state, num_adults=adults[x], num_children=children[x])
            else:
                salaries[x] = 0

            if self.qualify_snap(self.state, salaries_minimum_wage[x]):
                salaries_minimum_wage[x] = self.calculate_snap_benefit(state1=self.state, num_adults=adults[x], num_children=children[x])
            else:
                salaries_minimum_wage[x] = 0
            
        fig = sp.make_subplots(rows=1, cols=2)

        fig.add_trace(go.Scatter(x=years_list, y=salaries,
                            mode='lines+markers',
                            name='Major Salary'), row=1, col=1)

        fig.update_xaxes(title_text='Years', row=1, col=1)
        fig.update_yaxes(title_text='SNAP Benefits', row=1, col=1)

        fig.update_layout(title=f'Projected SNAP Benefits for {major} at {school} Over 20 Years vs Minimum Wage')

        # Add the second chart
        fig.add_trace(go.Scatter(x=years_list, y=salaries_minimum_wage,
                            mode='lines+markers',
                            name='Minimum Wage Benefits'), row=1, col=2)

        fig.update_xaxes(title_text='Years', row=1, col=2)
        fig.update_yaxes(title_text='Minimum Wage Benefits', row=1, col=2)

        graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
        return graph_html

    def benefitsplot(self, expFood, expSchoolMeal, expYearRent, family_utilities, childList, expTech, expWic, netExpChildCare, yearList):
        """
        Plot the provided lists against the yearList and save plots as image files.
        
        Args:
        expFood (list): List of expenses for food.
        expSchoolMeal (list): List of expenses for school meals.
        expYearRent (list): List of expenses for yearly rent.
        family_utilities (list): List of family utilities expenses.
        childList (list): List of child expenses.
        expTech (list): List of expenses for technology.
        expWic (list): List of expenses for WIC.
        netExpChildCare (list): List of net expenses for child care.
        yearList (list): List of years.
        """
        data_lists = [expFood, expSchoolMeal, expYearRent, family_utilities, childList, expTech, expWic, netExpChildCare]
        variable_names = ["expFood", "expSchoolMeal", "expYearRent", "family.utilities", "childList", "expTech", "expWic", "netExpChildCare"]
        
        # Plot all data together
        plt.figure(figsize=(10, 6))
        for data, name in zip(data_lists, variable_names):
            plt.plot(yearList, data, label=name)
        plt.xlabel("Year")
        plt.ylabel("Value")
        plt.legend()
        plt.title("Combined Benefit Plots")
        plt.savefig("result/combined_benefit_plots.png")  # Save the plot as an image
        plt.close()
        
        # Plot individual data
        for data, name in zip(data_lists, variable_names):
            plt.figure(figsize=(6, 4))
            plt.plot(yearList, data)
            plt.xlabel("Year")
            plt.ylabel("Value")
            plt.title(f"{name} Plot")
            plt.savefig(f"result/{name}_plot.png")  # Save the plot as an image
            plt.close()
    
    # A flask app to work as a GUI for the user to interact with the model with 
    @app.route('/')
    def home():
        return render_template('index.html', states=county_state_dict, schools=df_schools.to_dict('records'), majors=df_majors['Undergraduate Major'])

    @app.route('/result', methods=['POST'])
    def result():
        # Get form data
        form_data = request.form

        # Initialize a dictionary to store the results
        result_dict = {}
        family_dict = {}

        # Loop through each item in the form data
        for key, value in form_data.items():
            # Check if the item is a family member field
            if key.startswith('member'):
                # Get the field name and index
                field = key.rstrip('0123456789')
                index = ''.join(filter(str.isdigit, key))

                # Check if the family member index is already in the result dict
                if index not in family_dict:
                    # If not, add it
                    family_dict[index] = {}

                # Add the field and value to the family member's dictionary
                family_dict[index][field] = value
            else:
                # If it's not a family member field, just add it to the result dict
                result_dict[key] = value
        
        # Adding family members into result_dict
        result_dict['family_members'] = family_dict

        # Do something with the data
        print(result_dict)


        fam = Family(state = us_state_abbrev[result_dict['state']], county = result_dict['county'], programs = result_dict['program'])
        for item in result_dict['family_members']:
            if result_dict['family_members'][item]['memberType'] == 'adult':
                adult = Adult(age = int(result_dict['family_members'][item]['memberAge']), disabled = True if result_dict['family_members'][item]['memberDisabled'] == 'yes' else False)
                fam.add_adult(adult)
            else:
                child = Child(age = int(result_dict['family_members'][item]['memberAge']), disabled = True if result_dict['family_members'][item]['memberDisabled'] == 'yes' else False)
                fam.add_child(child)


        # Get the school and major
        school = result_dict['school']
        major = result_dict['major']

        salary_graph = fam.salary_plot(school, major)
        snap_graph = fam.plot_snap_benefits(school, major)

        # Pass the graph data to a new route for display
        return redirect(url_for('graph_display', salary_graph=salary_graph, snap_graph=snap_graph))

    @app.route('/graph-display')
    def graph_display():
        # Get the graph data from the URL parameters
        salary_graph = request.args.get('salary_graph')
        snap_graph = request.args.get('snap_graph')

        # Render the template and pass the graph data
        return render_template('graph_display.html', salary_graph=salary_graph, snap_graph=snap_graph)

    if __name__ == '__main__':
        app.run(debug=True)
