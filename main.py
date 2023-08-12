"""
Title: main.py
Author: Noah Fry
Brief: Controls I/O operations and functions for CLIFF calculations. 
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os

from child import Child
from adult import Adult
from family import Family     
        

        
def main():
    curr_year = datetime.datetime.now().year
    year = curr_year
    #Here we will take in the user's username and password. Based on their username, we will check for preloaded csv file.
    uID = str(input("Please enter your username: "))
    csv_filename = f"result/pre_load{uID}.csv"

    if os.path.exists(csv_filename):
        pre = str(input("Would you like to use your preloaded data? (Y/N) - "))
        if pre == "y":
            userDF = pd.read_csv(csv_filename, index = False)
            
            
    #Here I want to include a user terminal to either: "run the calculator again",
       #"display previous results", "delete information", etc for the user
    
        if pre == "n":
            os.remove(csv_filename)
            state = str(input("What state do you live in? Please enter code ex AZ - "))
            county = str(input("What county do you live in? - "))
            adults = int(input("How many adults are in your family? - "))
            kids = int(input("How many kids are in your family? - "))
            houseStatus = str(input("Do you rent or own your home? (R or O) - "))
            file_status = int(input("Please enter your filing status: \n(1: single, 2: joint, 3: separate, 4: head of household) - "))
            ccdfEligible = int(input("Are you Eligible, or currently using CCDF Benefits? (1, 0) - "))
            family = Family(curr_year=curr_year, state=state, county=county, houseStatus=houseStatus, file_status=file_status, ccdfEligible = bool(ccdfEligible))
            
            family.headStart = False
            
            
            for i in range(adults):
                age = int(input(f"what is the age of adult {i}? - "))
                disability = bool(int(input(f"does adult {i} have any disability? - ")))
                gift = int(input(f"Has adult {i} received gift money? (if so type how much money) - "))
                childsup = int(input(f"Has the adult {i} received an amount for child sup? - "))
                income = family.calculate_pay_minimum() + gift + childsup
                adult = Adult(age=age, income=income, disability=disability, childsup=childsup)
                family.add_adult(adult) 
                
            for i in range(kids):
                age = int(input(f"what is the age of kid {i}? - "))
                disability = bool(int(input(f"does child {i} have any disability? - ")))
                kid = Child(age=age, disability=disability, blindness=0)
                family.add_child(kid)

            for i in range(len(family.adults)):
                family.total_earned_income += family.adults[i].income
            
            publicTrans = 0#int(input("Do you use public transportation (1 - yes, 0 - no)?\n>>> "))
            
            family.taxRate()
            ccdfRemain = []
            #This is for all childcare expenses and benefits calculations. 
            valCCDFCopay, netExpChildCare = [], []
            prek, headstart, earlyheadstart, fates = False, False, False, False
            
            expFood, expSchoolMeal, expYearRent, yearList, childList, expTrans, expTech, expWic, tanf, expHealthALICE, expslcs = [], [], [], [], [], [], [], [], [], [], []
            for i in range(18):
                yearList.append(year)
                expFood.append(family.food_cost(year))
                expSchoolMeal.append(family.school_meal_cost(year))
                childList.append(family.childcareExp_ALICE(year))
                expYearRent.append(family.rent_cost(year))
                expTech.append(family.techExp_ALICE(year))
                #we run as pub false, for family not using public transportation
                expTrans.append(family.transExp_ALICE(year, publicTrans))
                expWic.append(family.wicExp(year))
                tanf.append(family.tanfBenefit(year))
                family.expHealthCareData(year)
                family.expHealthCareMedicaid(year)
                expslcs.append(family.expHealthCareSLCS(year))

                boolList = [prek, headstart, earlyheadstart, family.ccdfEligible, fates]
                
                expChildCare = childList[i]
                valCCDFCopay = family.calculate_childcare_for_ccdf(year, expChildCare, boolList)
                netExpChildCare.append(valCCDFCopay[0])
                ccdfRemain.append(valCCDFCopay[1])
            
                #qualSnap = family.snapBenefit()
                for kid in family.children:
                    kid.age += 1
                for adult in family.adults:
                    adult.age += 1
                year += 1
                
            #ccdf is calculated as a remainder of the total expChildCare.
            print("\tFood: ", expFood)
            print("\n\tSchool Meals: ", expSchoolMeal) 
            print("\n\n\tTotal Food Cost: ")
            for i in range(len(expFood)):
                print(expFood[i] - expSchoolMeal[i])
            print("\n\n\tRent: ", expYearRent)
            print("\n\tUtilities: ", family.utilities)
            print("Total Cost of Housing: ")
            for i in range(len(family.utilities)):
                print(expYearRent[i] - family.utilities[i])
            print("\n\t6: ", expTrans)
            print("\n\t7: ", expTech)
            print("\n\t8: ", expWic)
            print("\n\t9: ", tanf)
            print("\n\tTotal Expense of ChildCare before benefits: ", childList)
            for i in range(len(ccdfRemain)):
                if ccdfRemain[i] <= 0:
                    ccdfRemain[i] = 0
            print("\n\texp = ", ccdfRemain)
            print('\n\tcop = ', netExpChildCare)
            
            family.benefitsplot(expFood, expSchoolMeal, expYearRent, family.utilities, childList, expTech, expWic, netExpChildCare, yearList)


            adult_data = []
            for adult_obj in family.adults:
                adult_data.append({
                    "age": adult_obj.age,
                    "applicant": adult_obj.applicant,
                    "disability": adult_obj.disability,
                    "childsup": adult_obj.childsup,
                    "income": adult_obj.income,
                    "married": adult_obj.married,
                    "medAdult": adult_obj.medAdult,
                    "valHeadStart": adult_obj.valHeadStart,
                    "ssi": adult_obj.ssi
                })

            child_data = []
            for child_obj in family.children:
                child_data.append({
                    "age": child_obj.age,
                    "disability": child_obj.disability,
                    "blindness": child_obj.blindness,
                    "medKid": child_obj.medKid,
                    "netChildCareExp": child_obj.netChildCareExp,
                    "childcareExp": child_obj.childcareExp,
                    "valHeadStart": child_obj.valHeadStart,
                    "valEarlyHeadStart": child_obj.valEarlyHeadStart,
                    "valPreK": child_obj.valPreK
                })
                
            data = {
                "state": state,
                "county": county,
                "adults": adult_data,
                "kids": child_data,
                "houseStatus": houseStatus,
                "file_status": file_status,
                "ccdfEligible": ccdfEligible,
                "expFood": expFood,
                "expSchoolMeal": expSchoolMeal,
                "expYearRent": expYearRent,
                "utilities": family.utilities,
                "expTrans": expTrans,
                "expTech": expTech,
                "expWic": expWic,
                "tanf": tanf,
                "childList": childList,
                "ccdfRemain": ccdfRemain,
                "netExpChildCare": netExpChildCare
            }

            df = pd.DataFrame(data)

            # Save the DataFrame to a CSV file
            csv_filename = f"result/pre_load{uID}.csv"
            df.to_csv(csv_filename, index=False)
    else: 
        state = str(input("What state do you live in? Please enter code ex AZ - "))
        county = str(input("What county do you live in? - "))
        adults = int(input("How many adults are in your family? - "))
        kids = int(input("How many kids are in your family? - "))
        houseStatus = str(input("Do you rent or own your home? (R or O) - "))
        file_status = int(input("Please enter your filing status: \n(1: single, 2: joint, 3: separate, 4: head of household) - "))
        ccdfEligible = int(input("Are you Eligible, or currently using CCDF Benefits? (1, 0) - "))
        family = Family(curr_year=curr_year, state=state, county=county, houseStatus=houseStatus, file_status=file_status, ccdfEligible = bool(ccdfEligible))
        
        family.headStart = False
        
        
        for i in range(adults):
            age = int(input(f"what is the age of adult {i}? - "))
            disability = bool(int(input(f"does adult {i} have any disability? - ")))
            gift = int(input(f"Has adult {i} received gift money? (if so type how much money) - "))
            childsup = int(input(f"Has the adult {i} received an amount for child sup? - "))
            income = family.calculate_pay_minimum() + gift + childsup
            adult = Adult(age=age, income=income, disability=disability, childsup=childsup)
            family.add_adult(adult) 
            
        for i in range(kids):
            age = int(input(f"what is the age of kid {i}? - "))
            disability = bool(int(input(f"does child {i} have any disability? - ")))
            kid = Child(age=age, disability=disability, blindness=0)
            family.add_child(kid)

        for i in range(len(family.adults)):
            family.total_earned_income += family.adults[i].income
        
        adult_data = []
        for adult_obj in family.adults:
            adult_data.append({
                "age": adult_obj.age,
                "applicant": adult_obj.applicant,
                "disability": adult_obj.disability,
                "childsup": adult_obj.childsup,
                "income": adult_obj.income,
                "married": adult_obj.married,
                "medAdult": adult_obj.medAdult,
                "valHeadStart": adult_obj.valHeadStart,
                "ssi": adult_obj.ssi
            })

        child_data = []
        for child_obj in family.children:
            child_data.append({
                "age": child_obj.age,
                "disability": child_obj.disability,
                "blindness": child_obj.blindness,
                "medKid": child_obj.medKid,
                "netChildCareExp": child_obj.netChildCareExp,
                "childcareExp": child_obj.childcareExp,
                "valHeadStart": child_obj.valHeadStart,
                "valEarlyHeadStart": child_obj.valEarlyHeadStart,
                "valPreK": child_obj.valPreK
            })
            
        # Create separate DataFrames for adult and child data
        adult_df = pd.DataFrame(adult_data)
        child_df = pd.DataFrame(child_data)

        # Save the DataFrames to separate CSV files
        adult_csv_filename = f"result/adult_data{uID}.csv"
        child_csv_filename = f"result/child_data{uID}.csv"

        adult_df.to_csv(adult_csv_filename, index=False)
        child_df.to_csv(child_csv_filename, index=False)
            
        
        publicTrans = 0#int(input("Do you use public transportation (1 - yes, 0 - no)?\n>>> "))
        
        family.taxRate()
        ccdfRemain = []
        #This is for all childcare expenses and benefits calculations. 
        valCCDFCopay, netExpChildCare = [], []
        prek, headstart, earlyheadstart, fates = False, False, False, False
        
        expFood, expSchoolMeal, expYearRent, yearList, childList, expTrans, expTech, expWic, tanf, expHealthALICE, expslcs = [], [], [], [], [], [], [], [], [], [], []
        for i in range(18):
            yearList.append(year)
            expFood.append(family.food_cost(year))
            expSchoolMeal.append(family.school_meal_cost(year))
            childList.append(family.childcareExp_ALICE(year))
            expYearRent.append(family.rent_cost(year))
            expTech.append(family.techExp_ALICE(year))
            #we run as pub false, for family not using public transportation
            expTrans.append(family.transExp_ALICE(year, publicTrans))
            expWic.append(family.wicExp(year))
            tanf.append(family.tanfBenefit(year))
            family.expHealthCareData(year)
            family.expHealthCareMedicaid(year)
            expslcs.append(family.expHealthCareSLCS(year))

            boolList = [prek, headstart, earlyheadstart, family.ccdfEligible, fates]
            
            expChildCare = childList[i]
            valCCDFCopay = family.calculate_childcare_for_ccdf(year, expChildCare, boolList)
            netExpChildCare.append(valCCDFCopay[0])
            ccdfRemain.append(valCCDFCopay[1])
        
            #qualSnap = family.snapBenefit()
            for kid in family.children:
                kid.age += 1
            for adult in family.adults:
                adult.age += 1
            year += 1
            
        #ccdf is calculated as a remainder of the total expChildCare.
        print("\tFood: ", expFood)
        print("\n\tSchool Meals: ", expSchoolMeal) 
        print("\n\n\tTotal Food Cost: ")
        for i in range(len(expFood)):
            print(expFood[i] - expSchoolMeal[i])
        print("\n\n\tRent: ", expYearRent)
        print("\n\tUtilities: ", family.utilities)
        print("Total Cost of Housing: ")
        for i in range(len(family.utilities)):
            print(expYearRent[i] - family.utilities[i])
        print("\n\t6: ", expTrans)
        print("\n\t7: ", expTech)
        print("\n\t8: ", expWic)
        print("\n\t9: ", tanf)
        print("\n\tTotal Expense of ChildCare before benefits: ", childList)
        for i in range(len(ccdfRemain)):
            if ccdfRemain[i] <= 0:
                ccdfRemain[i] = 0
        print("\n\texp = ", ccdfRemain)
        print('\n\tcop = ', netExpChildCare)
        
        family.benefitsplot(expFood, expSchoolMeal, expYearRent, family.utilities, childList, expTech, expWic, netExpChildCare, yearList)

       #############################################################
        #Preload csv data
        
        
        # Determine the maximum length among all the lists, including object lists
        max_length = max(
            len(expFood),
            len(expSchoolMeal),
            len(expYearRent),
            len(family.utilities),
            len(expTrans),
            len(expTech),
            len(expWic),
            len(tanf),
            len(childList),
            len(ccdfRemain),
            len(netExpChildCare)
        )
        
        # Fill shorter lists with "NA" to match the maximum length
        def fill_list(lst):
            return lst + ["NA"] * (max_length - len(lst))

        # Fill all lists within the data dictionary
        data = {
            "state": state,
            "county": county,
            # Include other top-level variables
            # Include your other lists and variables
            "expFood": fill_list(expFood),
            "expSchoolMeal": fill_list(expSchoolMeal),
            "expYearRent": fill_list(expYearRent),
            "utilities": fill_list(family.utilities),
            "expTrans": fill_list(expTrans),
            "expTech": fill_list(expTech),
            "expWic": fill_list(expWic),
            "tanf": fill_list(tanf),
            "childList": fill_list(childList),
            "ccdfRemain": fill_list(ccdfRemain),
            "netExpChildCare": fill_list(netExpChildCare),

            # Include other calculated variables
            # Include adult and child data as string representations
            
        }
        df = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        csv_filename = f"result/pre_load{uID}.csv"
        df.to_csv(csv_filename, index=False)
            
if __name__ == '__main__':
    main()