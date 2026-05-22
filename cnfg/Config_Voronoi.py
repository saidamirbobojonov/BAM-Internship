########################################################################################################################################################################
main_path = 'M:/RVE_Workflow/SaeedWorkflow/Python_Code' #main_path is directory where your programm directory, for giving location u need open directory with this programm and 
                                                        #copy location and paste here
########################################################################################################################################################################

filename = 'Voronoi_2nd.inp'        #Firsly you need know that your input_file should be in inp_file's directory and then write ypu input_filename here
output_file_name = 'Voronoi_2nd'      #All output data will saved in result directory, but you need new file there and here should be your name of your new directory for saving output file
model_type = 'Voronoi'              #based on your input_file's model you need choose Voronoi or Voxel

number_of_grains = 512
nodes_length_type= 'mm'               #If you input_file's nodes in macrometer you need write µm or if milimeter you need write mm

########################################################################################################################################################################

surface_index = 10817                  #Start_index for element_face in surf_154
surface_local_index = 12               #Local_index for faces in surf_154
mat_ID_index = 51

########################################################################################################################################################################

node_number = 3             #Start index for your input_file's nodes

########################################################################################################################################################################

Node_Def = ''              #If True node_def will run or blank

Elem_Def = ''           #If True elements_def will run or blank

Set_Def = ''               #If True sets_def will run or blank

Interface = ''             #If True interface_element_def will run or blank Only for Voronoi, for defining you need True nodes_def, element_def, sets_def

CE_Def = ''                #If True CE_def will run or blank Only for Voxel for defining CP_def you need True nodes_def

CP_Def = ''                #If True CP_def will run or blank,Only for Voronoi defining CP_def you need True nodes_def, element_def, sets_def, interfaces

Orientation = ''           #If True orientations_def will run or blank

Surf_Elem = 'True'               #If True surf_element will run or blank, for defining surf_154 for Voronoi you need True nodes_def, element_def, sets_def, interfaces or
                                #if you want define surf_154 for Votonoi without seperation True only nodes_def, element_def, sets_def
                                #if you need for Voxel you need True nodes_def, element_def, sets_def
                                #order for surf_elem will be x+ mat_ID_index, x- mat_ID_index+1, y+ mat_ID_index+2, y- mat_ID_index+3, z+ mat_ID_index+4, z- mat_ID_index+5


#IMPORTANT Before using ansys_input_file you need configurate it in Config_Ansys_Input.py and then run it
Ansys_Input = ''       #If True ansys_input will run and gnerated ansys_files or blank


########################################################################################################################################################################

input_orientation_filename = 'C_Sec_red_orient_Z_Tensile512_G.txt' #Firsly you need know that your input_file should be in inp_file's directory and then write you input_filename of orientation file
output_orientation_filename = 'C_Sec_red_orient_Z_Tensile512_G.dat' #Output filename of orientation file
read_order_orientation = 'zxz'          #It for reading phi order for orientation, for ordering using x, y, z
output_order_orientation = 'zxy'        #It for output phi order for orientation, for ordering using x, y, z
grain_index = 1    #Start index for grain in output file of orientation file
start_index = 12   #Start index for angles in output file of orientation file

#It will be your header for you output file of orientation you every rows gonna be new rows in output file, that why if you need new paragraph in output file you need write in new paragraph here too
orientation_header = '''        
/com    Crept Speciment  IN718 21283_Schaft(QS)_01(65x)
'''

########################################################################################################################################################################

#Default Parametr
output_file = f'{main_path}/result/{output_file_name}' #It directory for result and in the end {var} for your new directory name
input_file = f'{main_path}/inp_file/{filename}'        #It directory for inp_file and in the end {var} for your input filename
input_orientation_file = f'{main_path}/inp_file'       #It directory for inp_file, but only for orientation files

##########################################################################################################################

