########################################################################################################################################################################
import importlib

while True:
    # Prompt for the name of the config file to import
    module_name = input("Enter the name of the config file to import (e.g., Config_Voxel): ")
    full_module_path = f"cnfg.{module_name}"

    try:
        # Dynamically import the specified module
        c = importlib.import_module(full_module_path)
        print(f"Successfully imported module '{full_module_path}'")
        # Exit the loop if import is successful
        break
    except ModuleNotFoundError:
        print(f"Module '{full_module_path}' not found. Make sure the file exists in the 'cnfg' directory.")
    except Exception as e:
        print(f"An error occurred while importing: {e}")



import os
from pycode.Node_def import node_def
from pycode.Set_Def import set_def
from pycode.Elem_Def import element_def
from pycode.Interface_Def import interface_def
from pycode.CE_def import CE_def
from pycode.CP_def import CP_def
from pycode.Orientation import orientation
from pycode.Ansys_Input import ansys_input_file
from pycode.Voxel_SE import voxel_surface_element
from pycode.Voronoi_SE import voronoi_surface_element

########################################################################################################################################################################

from cnfg import Config_Ansys_Input as ac

########################################################################################################################################################################

if __name__ == "__main__":

    if c.Node_Def:
        if os.path.isfile(c.output_file):
            print('')
        else:
            os.makedirs(c.output_file, exist_ok=True)
        node_def(c.input_file, c.output_file, c.node_number, c.nodes_length_type)
    if c.Elem_Def:
        if os.path.isfile(c.output_file):
            print('')
        else:
            os.makedirs(c.output_file, exist_ok=True)
        element_def(c.input_file, c.output_file, c.node_number, c.model_type)
    if c.Set_Def:
        if os.path.isfile(c.output_file):
            print('')
        else:
            os.makedirs(c.output_file, exist_ok=True)
        set_def(c.input_file, c.output_file, c.node_number)
    if c.Interface:
        if c.model_type == 'Voronoi':
            if os.path.isfile(c.output_file):
                print('')
            else:
                os.makedirs(c.output_file, exist_ok=True)
            interface_def(c.model_type, c.Interface, c.output_file, c.number_of_grains)
    if c.CE_Def:
        if c.model_type == 'Voxel':
            if os.path.isfile(c.output_file):
                print('')
            else:
                os.makedirs(c.output_file, exist_ok=True)
            CE_def(c.output_file, c.input_file, c.node_number)
    if c.CP_Def:
        if c.model_type == 'Voronoi':
            interfaces = 'True'
            if os.path.isfile(c.output_file):
                print('')
            else:
                os.makedirs(c.output_file, exist_ok=True)
            CP_def(c.output_file)
    if c.Orientation:
        if os.path.isfile(c.output_file):
            print('')
        else:
            os.makedirs(c.output_file, exist_ok=True)
        orientation(c.input_orientation_file, c.grain_index, c.start_index, c.output_file, c.input_orientation_filename, c.output_orientation_filename, c.number_of_grains, c.orientation_header, c.read_order_orientation, c.output_order_orientation)
    if c.Surf_Elem:
        if os.path.isfile(c.output_file):
            print('')
        else:
            os.makedirs(ac.output_file, exist_ok=True)
        if c.model_type == 'Voronoi':
            voronoi_surface_element(c.surface_local_index, c.surface_index, c.output_file, c.Interface, c.mat_ID_index)
        if c.model_type == 'Voxel':
            voxel_surface_element(c.surface_local_index, c.surface_index, c.output_file, c.mat_ID_index)
    if c.Ansys_Input:
        if os.path.isfile(c.output_file):
            print('')
        else:
            os.makedirs(c.output_file_ansys, exist_ok=True)
        ansys_input_file(c.input_file_ansys, ac.target_words, ac.replacement_words, ac.sign_delete, c.output_file_ansys)


########################################################################################################################################################################
