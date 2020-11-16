#   PyECM_Drill by John-Mark A. Phillips 
#   Version 0.0.1
#   The purpose of this program is to generate gcode for a 3-axis ECM machine running Marlin firmware for the drilling of holes.
#   To run this program, make sure to complete the start and end gcode sections
#   Start and End GCode 

#Custom name for the gcode file this program will create 
Custom_File_Name = "Test"

#XYZ Offsets for the workpiece. This is the distance between the origin of the machine and the origin of the work piece.
XYZ_Offset = [67, 130, 35.2]
#For 8 g stainless steel about Z17.7
#For 34 g needle about Z24

#The Z height at which the electrode will move between drilling
Move_Heigt = 25

#Speed/Feed Rate (mm/min) for horizontal movement
XY_Move_Feed_Rate = 500

#Speed/Feed Rate (mm/min) for vertical (Z) movement, not including drilling
Z_Move_Feed_Rate = 250

#Overshoot (mm): This is the distance the tool continues to cut past the instructed depth of the cut. This is to ensure that all 
#material under is removed for a complete drilling of a hole through a part. It should be greater than the inter-electrode gap (below)
Over_Shoot = 0.2

#Inter-electrode Gap (mm): This is the distance maintained between the tool and the workpiece.
Inter_Electrode_Gap = 0.2

Start_GCode = """
//Start gcode
M107 S0
G90
G21
G28
M102 X1000 Y1000
G1 F500
G1 X80 Y150 
G1 z50
// End of Start gcode"""

End_GCode = """
//End gcode//
M107 S0
G1 F500
G1 Z30"""

Electrode_On = """M106 I0 S255
M106 P1 S255"""

Electrode_Off = """M107 I0 S0
M107 P1 S0"""

#Creates a hole numebr reference to use later when labeling what gcode cooresponds to what hole. 
Hole_Number = 0

#Creates a virable that will be used to estimate the time required for the gcode to finish in minutes
Time_Estimate = 0 

#The following function creates a new file, and then pastes in the start gcode
def Create_New_GCode_File(Custom_File_Name): #Creates a function for creating the gcode file
    global GCode_File #Creates a global file variable that can be recognized outside this function
    GCode_File = open("ECM_Drilling_" + str(Custom_File_Name) +".gcode", "a") #Creates a file with a specific name
    GCode_File.seek(0) #Go to the begining of the file
    GCode_File.truncate() #Clear text that may already be there if the file already exists
    GCode_File.write(Start_GCode) #Pastes in the start gcode
    GCode_File.close()

#The following function creates gcode to drill a hole at an ordered pair, relative to the origin of the workpiece. It also 
#adjusts the coordinates using the XYZ offset, and saves the new gcode to the new gcode file.
def Drill_Hole(X_Coordinate, Y_Coordinate, Depth, Drilling_Feed_Rate): #Crears a function for drilling a specific hole
    global GCode_File #Uses global variable for this function
    global Hole_Number #Uses global varriable for this function
    global Time_Estimate #Uses global varriable for this function
    Hole_Number = Hole_Number + 1 #Adds one to the previous number of holes drilled. Note that is varriable starts at zero.
    GCode_File = open("ECM_Drilling_" + str(Custom_File_Name) +".gcode", "a") #Opens a file with a specific name
    GCode_File.write("\n") #Skips a line
    GCode_File.write("\n" + "Hole Number "+str(Hole_Number)) #labels gcode in gcode file with the hole number
    GCode_File.write("\n" + "G1 F"+str(XY_Move_Feed_Rate) + " G1" + " X"+str(X_Coordinate + XYZ_Offset[0]) + " Y"+str(Y_Coordinate + XYZ_Offset[1])) #Moves the tool head to the XY position
    GCode_File.write("\n" + "G1 F"+str(Z_Move_Feed_Rate) + " Z"+str(Inter_Electrode_Gap + XYZ_Offset[2])) #Moves the electrode to the correct position above the workpeice
    GCode_File.write("\n" + str(Electrode_On)) #Turns on electrode using "Electrode_On" gcode    
    GCode_File.write("\n" + "G1 F"+str(Drilling_Feed_Rate) + " Z"+str((Inter_Electrode_Gap + XYZ_Offset[2])-(Depth + Over_Shoot + Inter_Electrode_Gap))) #Drills a hole with a specific depth
    Time_Required_For_Drilling = ((1/Drilling_Feed_Rate)*(Depth + Over_Shoot))
    Time_Estimate = Time_Estimate + Time_Required_For_Drilling
    GCode_File.write("\n" + str(Electrode_Off)) #Turns electrode off using "Electrode_Off" gcode
    GCode_File.write("\n" + "G1 F"+str(Z_Move_Feed_Rate) + " Z"+str(Move_Heigt+XYZ_Offset[2])) #Moves the electrode back up

def Time_Estimate_Description():
    global GCode_File
    GCode_File = open("ECM_Drilling_" + str(Custom_File_Name) +".gcode", "a") #Opens a file with a specific name
    GCode_File.write("\n\n//Time Estated to Complete: " + str(Time_Estimate) + " Minutes") #Adds time estimate to bottom

Create_New_GCode_File(Custom_File_Name)
Drill_Hole(50, 12, 3, 0.54)
Drill_Hole(25, 12, 3, 0.44)
Drill_Hole(30, 12, 3, 0.46)
Drill_Hole(35, 12, 3, 0.48)
Drill_Hole(40, 12, 3, 0.50)
Drill_Hole(45, 12, 3, 0.52)

Drill_Hole(25, 17, 3, 0.56)
Drill_Hole(30, 17, 3, 0.58)
Drill_Hole(35, 17, 3, 0.60)
Drill_Hole(40, 17, 3, 0.62)
Drill_Hole(45, 17, 3, 0.64)
Drill_Hole(50, 17, 3, 0.66)


GCode_File.write("\n" + End_GCode)
GCode_File.close()
Time_Estimate_Description()