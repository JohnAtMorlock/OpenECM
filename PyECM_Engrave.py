import cv2
import numpy

Work_Piece_Dimensions = [40, 50] #Dimensions of the tool piece in mm (X, Y)
Electrode_Diameter = 0.23 #Diameter of the electrode in mm
File = 'Nathan2.JPG' #The name of the file to be used as a source
GCode_Output_File = 'Output_GCode.gcode' #The name of the file to be used for the resulting gcode
XYZ_Offset = [65, 20, 24] #XYZ Offsets for the workpiece. This is the distance between the origin of the machine and the origin of the work piece.
Start_Location = [80, 50, 30]
Regular_Acceleration = 500 #The acceleration used for moves
Regular_Feedrate = 5000 #The speed used for moves (mm/min)
Regular_Z_Feedrate = 500 #The spped of used for moving the z axis (mm/min)
Move_Height = 10 #The height above the workpiece the tool will move during move commands
Engraving_Acceleration = 10000 #The acceleration while engraving 
Engraving_Constant = -4.5 #Min = -4.7
Inter_Electrode_Gap = 0.2 #The added distance betwen the toolpiece and the electrode (mm)

Start_GCode = """
//Start gcode
M107 S0
G90
G21
G28
M102 X500 Y500
G1 F500
// End of Start gcode"""

Electrode_On_Command = """M106 P0 S255"""

Electrode_Off_Command = """M106 P0 S0"""

End_GCode = """
//End gcode//
M106 P0 S0
M106 P1 S0
G1 F500
G1 Z40
//End"""

def Create_GCode_File():
    #This function creates a gcode file that is used throughout the process.
    global GCode_File
    GCode_File = open("GCode_"+str(File)+".gcode", "a")
    GCode_File.seek(0) #Go to the begining of the file
    GCode_File.truncate() #Clear text that may already be there if the file already exists

def GCode_File_Write_Line(Command):
    GCode_File.write("\n " + str(Command))

def Synthesize_Array_From_Image(File):
    #This function converts a color image into a python array with x dimensions of y elements. 
    #It first converts the iamge into a black and white image, then resizes it to the dimensions of the work piece.
    global Array
    global Dimensions
    Dimensions = (int(Work_Piece_Dimensions[0]/Electrode_Diameter), int(Work_Piece_Dimensions[1]/Electrode_Diameter)) #The dimensions of the resized image are calculated using the resolution and wor piece dimensions
    Img = cv2.imread(File, cv2.IMREAD_GRAYSCALE)
    Img = cv2.bitwise_not(Img)
    Img = cv2.resize(Img, Dimensions)
    cv2.imshow(File, Img)
    Array = numpy.asarray(Img)
    
def Starting_Data():
    #This functions prints important information about the file and array in ther terminal
    print("Now Processing: " + str(File))
    print("Dimensions of Array for Engraving: " + str(Dimensions[0]) + " by " + str(Dimensions[1]))
    print("Resolution: " + str(Electrode_Diameter))
    print("Array Shape: " + str(Array.shape))

def Create_Array_File():
    #This function creates a text file that is used to print out the array made from an image.
    global Array_File
    Array_File = open("Array_" + str(File) + ".txt", "a") #Creates a file with a specific name
    Array_File.seek(0) #Go to the begining of the file
    Array_File.truncate() #Clear text that may already be there if the file already exists

def Record_Array():
    #This functions records the array in the text file created in the Create_Array_File()
    Row = 1  
    for i in range(Dimensions[0]):
        Array_File.write("\n" + "Row: " + str(Row))
        X_Value = Row + 1
        Array_File.write(str(Array[i]))

def Electrode_On():
    global Electrode_Status
    if Electrode_Status == False:
        GCode_File_Write_Line(Electrode_On_Command)
        Electrode_Status = True

def Electrode_Off():
    global Electrode_Status
    if Electrode_Status == True:
        GCode_File_Write_Line(Electrode_Off_Command)
        Electrode_Status = False

def Move_To_Start(Coordinates):
    GCode_File_Write_Line("M102 X"+str(Regular_Acceleration) + " Y"+str(Regular_Acceleration) + " Z"+str(Regular_Acceleration))
    GCode_File_Write_Line("G1 F"+str(Regular_Feedrate) + " X"+str(Start_Location[0]) + " Y"+str(Start_Location[1]))
    GCode_File_Write_Line("G1 "+" Z"+str(Start_Location[2]))
    GCode_File_Write_Line("G4 S1")
def Check_Row_Sum(Row):
    global Row_Status
    Array_Row_Sum = numpy.sum(Array, 1) #Takes the sum of the rows in the array. This will be used to find if there is any work to be done in this row in the raster (if the sum of the row is greater than zero)
    Current_Row_Sum = Array_Row_Sum[Row]
    if Current_Row_Sum == 0: 
        Row_Status = False
    else:
        Row_Status = True

def Engrave_Pixel(Value, Coordinate):
    if Value == 0:  
        Electrode_Off()
        GCode_File_Write_Line("M102 X"+str(Regular_Acceleration) + "  Y"+str(Regular_Acceleration))
        GCode_File_Write_Line("G1 F"+str(Regular_Z_Feedrate) + " Z"+str(Inter_Electrode_Gap + XYZ_Offset[2]))
        GCode_File_Write_Line("G1 F"+str(Regular_Feedrate) + " X"+str(X_Coordinate))
    
    if Value > 0:
        GCode_File_Write_Line("Value is: " + str(Value))
        Custom_Feedrate = ((Value*Engraving_Constant)+1200)
        Electrode_On()
        GCode_File_Write_Line("M102 X"+str(Engraving_Acceleration) + "  Y"+str(Engraving_Acceleration))
        GCode_File_Write_Line("G1 F"+str(Regular_Z_Feedrate) + " Z"+str(Inter_Electrode_Gap + XYZ_Offset[2]))
        GCode_File_Write_Line("G1 F"+str(Custom_Feedrate) + " X"+str(X_Coordinate))
        GCode_File_Write_Line("M102 X"+str(Regular_Acceleration) + "  Y"+str(Regular_Acceleration))
        GCode_File_Write_Line("M203 X"+str(Regular_Feedrate) + " Y"+str(Regular_Feedrate))

def Engrave_Row(Current_Row):
    global X_Coordinate
    X_Coordinate = XYZ_Offset[0] #The left of a workpiece 
    Y_Coordinate = XYZ_Offset[1] + Work_Piece_Dimensions[1] - (Electrode_Diameter*Current_Row) #The top of the work peice
    Row_Values = Array[Current_Row] #Finds the values in the row to be rastered
    Current_Pixel = 0
    Current_Pixel_Value = Row_Values[Current_Pixel]
    Number_Of_Pixels_In_Row = int(Dimensions[0])
    GCode_File_Write_Line("\n Starting Row: " + str(Current_Row) + " At ("+str(X_Coordinate)+", "+str(Y_Coordinate)+")")

    Electrode_Off()
    GCode_File_Write_Line("G1 F"+str(Regular_Feedrate) + " Y"+str(Y_Coordinate))
    GCode_File_Write_Line("G1 F"+str(Regular_Feedrate) + " X"+str(XYZ_Offset[0]))


    for i in range(Number_Of_Pixels_In_Row):
        Current_Pixel_Value = Row_Values[Current_Pixel]
        Engrave_Pixel(Current_Pixel_Value, X_Coordinate)
        X_Coordinate = X_Coordinate + Electrode_Diameter
        Current_Pixel = Current_Pixel + 1
    
def Engraving_Loop():
    Number_Of_Rows = int(Dimensions[1]) #Finds the number of horizontal (y-axis) rows to be rastered
    Number_Of_Pixels_In_Row = int(Dimensions[0])
    print("Number of Rows: " + str(Number_Of_Rows))
    print("Number of Pixels in Row: " + str(Number_Of_Pixels_In_Row))
    global Current_Row
    Current_Row = 0
    Row_Values = Array[Current_Row] #Finds the values in the row to be rastered
    while True:
        #This loop looks for rows with data inside, and skips over rows with no data
        Check_Row_Sum(Current_Row)
        if Row_Status == True: 
            Engrave_Row(Current_Row)
            #Add function to move down the correct amount
            Current_Row = Current_Row + 1
        if Current_Row >= (Number_Of_Rows - 1):
            break
        if Row_Status == False: 
            Current_Row = Current_Row + 1
            #Add function to move down the correct amount

#First, create an array from an image. To do this, the image is resized to fit the size of the 
#workpiece. The size of the electrode dictates resolution of the array. The resulting array is a collection
#of the pixels in the image, organized into horizontal rows.
Synthesize_Array_From_Image(File)

#The next step is option. It creates a text file of the complete array generated in the previous step. This is 
#used for trouble shooting.
Create_Array_File()
Record_Array()

#Prints data about the array to the terminal
Starting_Data()

#This function creates a text file that is used for gcode recording. It is written to using the custom function
# "GCode_File_Write_Line".
Create_GCode_File()

#Prints the starting GCode to the gcode file.
GCode_File_Write_Line(Start_GCode)

#Ensures the electrode is turned off, and states that the electrode is so using a custom variable.
GCode_File_Write_Line(Electrode_Off_Command)
Electrode_Status = False

#Moves to start coordinates 
Move_To_Start(Start_Location)

#The main loop for engraving. It has several sub-functions: Check_Sum, Engrave_Row, and Engrave_Pixel
#The Check_Sum function checks to see if there is any data in a row. If there is none, then it skips it.
#The Engrave_Row function engraves every pixel in a horizontal row using the Engrave_Pixel function.
Engraving_Loop()

#Writes the ending GCode to the GCode file.
GCode_File_Write_Line(End_GCode)
GCode_File_Write_Line("Finished")
print(str("Finished"))
cv2.waitKey(0)
cv2.destroyAllWindows()