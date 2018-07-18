import pandas as pd
#Read the data set
df = pd.read_csv("patient_heart_rate.csv")
#Get the Weight column
weight = df['Weight']
 
for i in range (0 ,len(weight)):    
    x= str(weight[i])
    #Incase lbs is part of observation remove it
    if "lbs" in x[-3:]:
        #Remove the lbs from the value
        x = x[:-3:]
        #Convert string to float
        float_x = float(x)
        #Covert to kgs and store as int
        y =int(float_x/2.2) # CAN WE DO THIS WITH OCTAGONS??
        #Convert back to string
        y = str(y)+"kgs"
        weight[i]= y
print (df)