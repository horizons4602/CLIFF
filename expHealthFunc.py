# Step 1
def calculate_exp_healthcare_employer(healthCareCSV, famSize):
    if famSize == 1:
        return healthCareCSV['Single_employee'] + healthCareCSV['Single_employer']
    elif famSize == 2:
        return healthCareCSV['Plusone_employee'] + healthCareCSV['Plusone_employer']
    elif famSize >= 3:
        return healthCareCSV['Family_employee'] + healthCareCSV['Family_employer']
    else:
        return 0

# Step 2
def calculate_exp_healthcare_employer_ALICE(healthCareCSV, famSize):
    if famSize == 1:
        return healthCareCSV['Single_employee'] + healthCareCSV['Single_employer']
    elif famSize == 2:
        return healthCareCSV['Plusone_employee'] + healthCareCSV['Plusone_employer']
    elif famSize >= 3:
        return healthCareCSV['Family_employee'] + healthCareCSV['Family_employer']
    else:
        return 0

# Step 3
def calculate_premium_employer(healthCareCSV, famSize):
    if famSize == 1:
        return healthCareCSV['Single_employee'] * 1.3
    elif famSize == 2:
        return healthCareCSV['Plusone_employee'] * 1.3
    elif famSize >= 3:
        return healthCareCSV['Family_employee'] * 1.3
    else:
        return 0

# Step 4
def calculate_premium_employer_ALICE(healthCareCSV, famSize):
    if famSize == 1:
        return healthCareCSV['Single_employee']
    elif famSize == 2:
        return healthCareCSV['Plusone_employee']
    elif famSize >= 3:
        return healthCareCSV['Family_employee']
    else:
        return 0