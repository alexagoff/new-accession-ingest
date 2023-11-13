import json 
import csv
import os 
import functions
import sys
from datetime import date 

#first_arg = sys.argv[1]
#print(first_arg)
# filename.csv

s = open('login_materials/current_sess.txt', 'r')
curSession = s.read()

functions.accessions_exist()

# edit line below to manually enter a .csv 
#csvInFilePath2 = './in_out/input/shelfread_input_test_data.csv' 
csvInFilePath = sys.argv[1]
errorOutFilePath = './in_out/output/errorLog.txt'
logOutFilePath = './in_out/output/appLog.txt'
csvOutPath = "./in_out/output/shelfReadOutput.csv"
csvErrorsPath = "./in_out/output/Errors.csv"

# for final report
invalid_bar = 0
invalid_shelf = 0
correct_loc = 0
updated_loc = 0
oldcsv = 0
newcsv = 0


# for getting the day, month, year for csv
todays_date = date.today() 
str_date = str(todays_date.month) + '/' + str(todays_date.day) + '/' + str(todays_date.year)
 
print("\n\nn\n\n\n\n")

with open(csvInFilePath, 'r') as file: 
    with open(csvOutPath, 'w') as file2: # new csv with updated locations     
        errors_file = open(errorOutFilePath, "w")
        app_log = open(logOutFilePath, "w")
        errors_csv = open(csvErrorsPath, 'w')
        writer = csv.writer(file2)
        err_writer = csv.writer(errors_csv)
        
        data = file.read()
        dataArray = data.split('\n')
        oldcsv = len(dataArray)
        firs_row = dataArray[0].split(",")
        writer.writerow(firs_row) 
        err_writer.writerow(firs_row)
        
        date_loc = firs_row.index("Date")
        type_loc = firs_row.index("Type (Shelf Read or Move)")
        desc_loc = firs_row.index("Description")

        errors_file.write("line #'s are referring to input csv lines.\n\n")
        app_log.write("line #'s are referring to input csv lines.\n\n")
        
        # just for "working...✅" visuals
        dots = "."
        nspace = int(len(dataArray)/15)-2

        # looping through each line of the input CSV
        for i in range(1, (len(dataArray))):
            # for time passing visuals 
            if i%15 == 0:
                print("working"+dots+(nspace*" ")+"✅")
                dots+="."
                nspace-=1
            
            row = dataArray[i]
            if len(row) == 0: # if nothing in line
                oldcsv-=1
                continue

            match = row.split(',')
            shelfBar = match[0] # shelf barcode
            itemBar = match[1] # item barcodes

            shelfcode = functions.get_shelf(itemBar, curSession)
            shelf_exist = functions.shelf_exists(shelfBar, curSession)
            
            # if barcode doesn't exist
            if shelfcode == 0:
                errors_file.write(("LINE "+str((i+1))+" item barcode "+itemBar+" does not exist in Aspace.\n"))
                app_log.write(("LINE "+str((i+1))+" removed.\n"))
                match[desc_loc] = "Barcode does not exist"
                match[date_loc] = str_date
                err_writer.writerow(match)
                invalid_bar+=1
            
            # if shelfcode doesn't exist
            elif not shelf_exist:
                errors_file.write(("LINE " + str((i+1))+" shelf barcode "+shelfBar+" does not exist in Aspace.\n"))
                app_log.write(("LINE "+str((i+1))+" removed.\n"))
                match[desc_loc] = "Shelfcode does not exist"
                match[date_loc] = str_date
                err_writer.writerow(match)
                invalid_shelf+=1

            # if barcode and shelfcode exist
            else:
                # Shelf Read
                if shelfcode == shelfBar:
                    correct_loc+=1
                    match[type_loc] = "Shelf Read"

                # Move
                else:
                    #functions.change_shelf(itemBar, shelfBar, curSession)
                    errors_file.write(("LINE "+str((i+1))+" wrong shelfcode. item barcode "+itemBar+" is not at shelf "+shelfBar+".\n"))
                    app_log.write(("LINE "+str((i+1))+" "+itemBar+"'s location updated to "+shelfBar+".\n"))
                    match[type_loc] = "Move"
                    updated_loc+=1

                match[date_loc] = str_date
                writer.writerow(match)
                newcsv+=1


print("\n\n")
print("****************************************************")
print("                        REPORT   ")
print("")
print(" locations updated: ", updated_loc)
print(" locations confirmed (correct shelf&bar codes): ", correct_loc)
print("\n", invalid_bar+invalid_shelf, "codes removed")
print(" old length:", oldcsv-1, "    new length:", newcsv)
print("\n                        errors                        ")
print("")
print(" invalid barcodes (not in Aspace): ", invalid_bar)
print(" invalid shelfcodes (not in Aspace): ", invalid_shelf)
print("****************************************************")
print("\n\n")

s.close()
errors_file.close()
errors_csv.close()
app_log.close()


# if the shelfcode doesn't exist, then I can just pass it through like normal, and then
# try to change the barcode to the shelfcode and if that doesn't work, I will determine
# that the shelf doesn't exist (because it could exist and have 0 items).
# this theory only works if by posting on a invalid shelf it doesn't work.