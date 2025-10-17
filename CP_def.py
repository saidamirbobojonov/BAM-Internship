import numpy as np
from scipy.spatial import distance_matrix
from datetime import datetime

def find_pairs(listT, nodes, tol):
    # Ensure listT is a list of lists
    if not all(isinstance(i, list) for i in listT):
        raise ValueError("listT should be a list of lists.")

    # Create a mapping from nodNum to index
    nodNum_to_index = {node[0]: index for index, node in enumerate(nodes)}

    # Initialize a set to store results
    groups = []
    visited = set()

    # Convert nodes to a numpy array for easier handling
    node_coords = np.array([node[1:] for node in nodes])

    # Loop through each list in listT
    for sublist in listT:
        for node_id in sublist:
            if node_id in visited or node_id not in nodNum_to_index:
                continue

            current_group = []
            index_i = nodNum_to_index[node_id]
            x1, y1, z1 = node_coords[index_i]

            for other_id in sublist:
                if other_id in visited or other_id not in nodNum_to_index:
                    continue

                index_j = nodNum_to_index[other_id]
                x2, y2, z2 = node_coords[index_j]

                # Check if coordinates are within tolerance
                if np.allclose([x1, y1, z1], [x2, y2, z2], atol=tol):
                    current_group.append(other_id)
                    visited.add(other_id)

            # Only add groups with more than one node
            if len(current_group) > 1:
                groups.append(sorted(current_group))

    # Remove duplicates
    unique_groups = []
    seen = set()
    for group in groups:
        tgroup = tuple(group)
        if tgroup not in seen:
            unique_groups.append(group)
            seen.add(tgroup)

    return unique_groups
def extract_list(set_def_path, start_keyword, end_keyword):
    capture_data = False
    current_keyword_name = None
    data = []

    with open(set_def_path, 'r') as infile:
        lines = infile.readlines()

    for line in lines:
        # Skip lines containing '*End Part'
        if end_keyword in line:
            capture_data = False
        if '(8i10)' in line:
            continue

        if capture_data:
            cleaned_line = line.replace(',', '')
            numbers = cleaned_line.split()
            data.extend(numbers)

        if start_keyword in line:
            capture_data = True
    return data
def import_nodes(node_def_path):
    nodes = []
    try:
        with open(node_def_path, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                nodNum = int(parts[1].strip())
                x = float(parts[2].strip())
                y = float(parts[3].strip())
                z = float(parts[4].strip())
                nodes.append([nodNum, x, y, z])
    except FileNotFoundError:
        print(f"Error: The file '{node_def_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while importing nodes: {e}")
    return nodes
def calculate_lrve_and_tol(nodes):
    if not nodes:
        raise ValueError("The nodes list is empty.")

    # Calculate the maximum y-coordinate
    lrve = max(node[2] for node in nodes)

    # Calculate the tolerance
    tol = lrve * 10 ** -4
    return lrve, tol
def write_cp_def_file(cpnodes, output_file):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    CP_def_path = f'{output_file}/CP_Def.dat'
    with open(CP_def_path, 'w') as out:
        out.write('/com ***************************************\n')
        out.write('/com CP Equation for Voronoi RVE 1224 G with Cohesive elements\n')
        out.write(f'/com Generated on {current_time} with Python\n')
        out.write('/com ***************************************\n')

        for node_group in cpnodes:
            nodeT1 = ", ".join(map(str, node_group))
            out.write("CP, next, all, " + nodeT1 + " \n")

    print(f"File 'CP_Def.dat' has been saved.")
def CP_def(output_file):

    set_def_path = f'{output_file}/Set_Sep_Def.dat'
    node_def_path = f'{output_file}/Node_Sep_Def.dat'
    backList = list(map(int, extract_list(set_def_path, "CMBLOCK,BACK,NODE,", "CMBLOCK,FRONT,NODE,")))
    frontList = list(map(int, extract_list(set_def_path, "CMBLOCK,FRONT,NODE,", "CMBLOCK,BOTTOM,NODE,")))
    bottomList = list(map(int, extract_list(set_def_path, "CMBLOCK,BOTTOM,NODE,", "CMBLOCK,TOP,NODE,")))
    topList = list(map(int, extract_list(set_def_path, "CMBLOCK,TOP,NODE,", "CMBLOCK,LEFT,NODE,")))
    leftList = list(map(int, extract_list(set_def_path, "CMBLOCK,LEFT,NODE,", "CMBLOCK,RIGHT,NODE,")))
    rightList = list(map(int, extract_list(set_def_path, "CMBLOCK,RIGHT,NODE,", "CMBLOCK,Bottom_left_back,NODE,")))
    nodes = import_nodes(node_def_path)
    lrve, tol = calculate_lrve_and_tol(nodes)
    listT = [backList, frontList, topList, bottomList, leftList, rightList]
    cpnodes = find_pairs(listT, nodes, tol)
    write_cp_def_file(cpnodes, output_file)


