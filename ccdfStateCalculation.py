#For use with the ccdf calculations
"""CCDF State Copay Calculators
   Noah Fry 
   Calculates the total copay cost per state. 
"""
import pandas as pd

def ccdfAL(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    FTCopay = FTCopay*52
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
        
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

#####################################################################################################
def ccdfAK(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop*12
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList
    
def ccdfAZ(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop*(infNumDaysCare+childNumDaysCare)
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList
    
def ccdfAR(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*income
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfCA(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    infMonthsofCare, childMonthsofCare = 0, 0
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    infMonthsofCare = 12 * infNumDaysCare / (70+180)
    childMonthsofCare = 12 * childNumDaysCare / (0.5*(70+180))
    FTCopay = FTCopay * (infMonthsofCare + childMonthsofCare)
    print(FTCopay)
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

#####################################################################################################
def ccdfCO(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    df_ccdf = df_ccdf[df_ccdf['numkidsInCare'] == numKidsInCare]
    FTCopay = cop*income
    print(income, df_ccdf['ContinuousEligibility'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

###################################################################################################
def ccdfHI(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*income
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfIA(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    tmpdf = df_ccdf.copy()
    income = income #- (12 * tmpdf['IncomeDisregard'].iloc[0])
    for i in range(30):
        binColumn = f'Bin{i}Max'
        if binColumn in tmpdf.columns:
            tmpdf[binColumn] *= 12
    
    for i in range(30):
        # Finds the iteration with the correct income/copay bins
        bin_column = f"Bin{i}Max"
        copay_column = f"CopayBin{i}"
        
        if i == 0:
            continue
        elif bin_column not in tmpdf.columns:
            copay_column = f"CopayBin{i-1}"
            cop = tmpdf[copay_column].iloc[0]
            break
        else:
            if income >= tmpdf[bin_column].values[0]:
                continue
            else:
                cop = tmpdf[copay_column].iloc[0]
                break
            
    FTCopay = cop
    FTCopay = FTCopay * (infNumDaysCare + childNumDaysCare)
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    tmpdf = pd.DataFrame()
    ansList = [eligibility, FTCopay]
    return ansList

def ccdfMD(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    for i in range(123):
        #finds the iteration with the correct income/copay bins
        bin_column = f"Bin{i}Max"
        copay_column = f"CopayBin{i}_RegionBC"
        if i == 0: continue
        else:                        
            if bin_column not in df_ccdf.columns:
                copay_column = f"CopayBin{i-1}"
                cop = df_ccdf[copay_column].iloc[0]
                break
            
            if income > df_ccdf[bin_column].values[0]:
                continue
            
            else: 
                cop = df_ccdf[copay_column].values[0]
                break
                            
    FTCopay = cop
    FTCopay = FTCopay*52
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
        
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfMA(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    tmp = income - df_ccdf['Bin1Max'].iloc[0]
    FTCopay = FTCopay * tmp
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
        
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfMI(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop * numKidsInCare * 26
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfMN(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop * 26
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfMO(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    for i in range(123):
        #finds the iteration with the correct income/copay bins
        bin_column = f"Bin{i}Max"
        copay_column = f"CopayBin{i}_FT"
        if i == 0: continue
        else:                        
            if bin_column not in df_ccdf.columns:
                copay_column = f"CopayBin{i-1}"
                cop = df_ccdf[copay_column].iloc[0]
                break
            
            if income > df_ccdf[bin_column].values[0]:
                continue
            
            else: 
                cop = df_ccdf[copay_column].values[0]
                break
    FTCopay = cop*(infNumDaysCare+childNumDaysCare)
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfNV(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    # Implementation for NV
    print("made it here")

def ccdfNH(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*income
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

##################################################################################################
def ccdfNJ(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*12
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfNM(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    FTCopay = round(cop*numKidsInCare*12, 2)
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
        
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfNY(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    # Implementation for NY
    print("made it here")

def ccdfNC(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    # Implementation for NC
    print("made it here")

def ccdfND(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop*12*numKidsInCare
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfOH(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    for i in range(123):
        #finds the iteration with the correct income/copay bins
        bin_column = f"Bin{i}Max"
        copay_column = f"CopayBin{i}_FractionOfGrossIncome"
        if i == 0: continue
        else:                        
            if bin_column not in df_ccdf.columns:
                copay_column = f"CopayBin{i-1}"
                cop = df_ccdf[copay_column].iloc[0]
                break
            
            if income > df_ccdf[bin_column].values[0]:
                continue
            
            else: 
                cop = df_ccdf[copay_column].values[0]
                break
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*income
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList


def ccdfPA(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*52
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfSC(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*numKidsInCare*52
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfTN(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    # Implementation for TN
    print("made it here")

def ccdfTX(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    # Implementation for TX
    print("made it here")

###################################################
def ccdfUT(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    print(income, df_ccdf['ContinuousEligibility'].iloc[0])
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    FTCopay = FTCopay*12
    print(FTCopay)
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

def ccdfVT(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    for i in range(123):
        #finds the iteration with the correct income/copay bins
        bin_column = f"Bin{i}Max"
        copay_column = f"ShareofCost{i}"
        if i == 0: continue
        else:                        
            if bin_column not in df_ccdf.columns:
                copay_column = f"CopayBin{i-1}"
                cop = df_ccdf[copay_column].iloc[0]
                break
            
            if income > df_ccdf[bin_column].values[0]:
                continue
            
            else: 
                cop = df_ccdf[copay_column].values[0]
                break
    FTCopay = cop*(infNumDaysCare+childNumDaysCare)
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

####################################################################################################
def ccdfWI(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop*(infNumDaysCare+childNumDaysCare)*8
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList

#######################################################################################################
def ccdfWY(df_ccdf, famsize, cop, income, numKidsInCare, infNumDaysCare, childNumDaysCare):
    ansList = []
    FTCopay = cop*(infNumDaysCare+childNumDaysCare)
    income = income - (12 * df_ccdf['IncomeDisregard'].iloc[0])
    
    if income <= df_ccdf['ContinuousEligibility'].iloc[0]:
        eligibility = True
    else: 
        eligibility = False
    ansList.append(eligibility)
    ansList.append(FTCopay)
    return ansList
