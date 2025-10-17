import itertools
import numpy as np
from scipy.spatial import KDTree

def read_nodes_from_file(filename):
    nodes = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                node_id = int(parts[1].strip())
                x = float(parts[2].strip())
                y = float(parts[3].strip())
                z = float(parts[4].strip())
                nodes[node_id] = (x, y, z)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    except Exception as e:
        print(f"An error occurred while reading nodes: {e}")
    return nodes

def extract_list(set_def_path, start_keyword, end_keyword):
    capture_data = False
    data = []
    element_index = 0
    try:
        with open(set_def_path, 'r') as infile:
            lines = infile.readlines()
        for line in lines:
            if end_keyword in line:
                capture_data = False
            if 'SOLID187' in line:
                element_index += 1
            if '(8i10)' in line:
                continue

            if capture_data:
                cleaned_line = line.replace(',', '')
                numbers = cleaned_line.split()
                data.extend(numbers)

            if start_keyword in line:
                capture_data = True

    except FileNotFoundError:
        print(f"Error: The file '{set_def_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while extracting data: {e}")

    return data, element_index

def extract_surface_data(element_def_path):
    with open(element_def_path, 'r') as file:
        lines = file.readlines()

    formatted_data = []
    current_entry = []
    surface_data = {}  # Renamed from `list` to `surface_data`
    element_index = 0
    for line in lines:
        parts = line.strip().split(',')
        identifier = parts[0]
        if 'SOLID186' in line:
            element_index += 1
        if identifier == 'EN':
            if current_entry:
                # Add the current entry to the formatted data
                formatted_data.append(current_entry)
                current_entry = []
            current_entry.extend(parts[1:])
        elif identifier == 'EMORE':
            current_entry.extend(parts[1:])
        elif identifier == 'Et':
            if current_entry:
                # Add the current entry to the formatted data
                formatted_data.append(current_entry)
                current_entry = []
        elif identifier in ('Mat', 'Type'):
            continue  # Skip these lines

    # Add the last entry if not empty
    if current_entry:
        formatted_data.append(current_entry)

    # Convert formatted_data into a dictionary
    for entry in formatted_data:
        surface_id = entry[0]
        nodes = entry[1:]
        surface_data[surface_id] = nodes

    return surface_data

def find_group(surface_data, face, node_data):
    face_set = set(face)
    seen_surfaces = set()  # Set to track already processed surface IDs

    # Initialize a dictionary to store grouped data
    grouped_data = {}
    matching_surface_id_count = 0
    # Iterate through each surface_id in surface_data
    for surface_id, nodes in surface_data.items():
        # Convert nodes to integers and filter out any invalid entries
        try:
            nodes = list(map(int, nodes))
        except ValueError:
            continue  # Skip invalid entries

        # Skip if the surface node list is empty
        if not nodes:
            continue

        # Find the intersection of surface nodes with face nodes
        if len(nodes) >= 4:
            # Find the intersection of surface nodes with leftList nodes
            common_nodes = [node for node in nodes if node in face_set]

        # Check if the surface has exactly 8 common nodes and is not seen before
        if surface_id not in seen_surfaces and len(common_nodes) == 4:
            seen_surfaces.add(surface_id)
            matching_surface_id_count += 1

            # Append coordinates to the common_nodes in grouped_data
            grouped_data[surface_id] = [(node, node_data[node]) for node in common_nodes if node in node_data]

    # Return the grouped data
    return grouped_data

def find_main_points(nodes):
    result_points = {}
    for group_name, vertices in nodes.items():
        # Convert vertices to a dictionary if it's a list
        if isinstance(vertices, list):
            vertices_dict = {vertex[0]: vertex[1] for vertex in vertices}
        elif isinstance(vertices, dict):
            vertices_dict = vertices
        else:
            print(f"Skipping group {group_name} because its data is neither a list nor a dictionary: {vertices}")
            continue

        # Validate that each vertex in vertices_dict is a tuple of 3 numbers
        valid_vertices = True
        for vertex_id, coords in vertices_dict.items():
            if not (isinstance(coords, tuple) and len(coords) == 3 and all(
                    isinstance(c, (int, float)) for c in coords)):
                print(f"Invalid coordinates for vertex {vertex_id} in group {group_name}: {coords}")
                valid_vertices = False
                break

        if not valid_vertices:
            continue

        # Limit to combinations of 8 vertices
        for comb in itertools.combinations(vertices_dict.items(), 4):
            for (id1, (x1, y1, z1)), (id2, (x2, y2, z2)), (id3, (x3, y3, z3)), (
            id4, (x4, y4, z4)) in itertools.combinations(comb, 4):

                if all(x == 0.0 for x, _, _ in
                       [vertices_dict[id1], vertices_dict[id2], vertices_dict[id3], vertices_dict[id4]]):
                    first_main_point = min(comb, key=lambda p: (p[1][2], -p[1][1]))  # Smallest z with biggest y
                    second_main_point = min(comb, key=lambda p: (p[1][2], p[1][1]))  # Smallest z with smallest y
                    third_main_point = max(comb, key=lambda p: (p[1][2], -p[1][1]))  # Biggest z with biggest y
                    fourth_main_point = next(
                        p for p in comb if p not in [first_main_point, second_main_point, third_main_point])

                elif all(x == 1.0 for x, _, _ in
                         [vertices_dict[id1], vertices_dict[id2], vertices_dict[id3], vertices_dict[id4]]):
                    first_main_point = min(comb, key=lambda p: (p[1][1], p[1][2]))  # Smallest y with smallest z
                    second_main_point = min(comb, key=lambda p: (-p[1][1], p[1][2]))  # Smallest y with biggest z
                    third_main_point = max(comb, key=lambda p: (p[1][1], p[1][2]))  # Biggest y with biggest z
                    fourth_main_point = next(
                        p for p in comb if p not in [first_main_point, second_main_point, third_main_point])

                elif all(y == 0.0 for _, y, _ in
                         [vertices_dict[id1], vertices_dict[id2], vertices_dict[id3], vertices_dict[id4]]):
                    first_main_point = min(comb, key=lambda p: (p[1][0], p[1][2]))  # Smallest x with biggest z
                    second_main_point = min(comb, key=lambda p: (-p[1][0], p[1][2]))  # Smallest x with smallest z
                    third_main_point = max(comb, key=lambda p: (p[1][0], p[1][2]))  # Biggest x with biggest z
                    fourth_main_point = next(
                        p for p in comb if p not in [first_main_point, second_main_point, third_main_point])

                elif all(y == 1.0 for _, y, _ in
                         [vertices_dict[id1], vertices_dict[id2], vertices_dict[id3], vertices_dict[id4]]):
                    first_main_point = min(comb, key=lambda p: (p[1][2], -p[1][0]))  # Smallest z with smallest x
                    second_main_point = min(comb, key=lambda p: (p[1][2], p[1][0]))  # Smallest z with biggest x
                    third_main_point = max(comb, key=lambda p: (p[1][2], -p[1][0]))  # Biggest z with biggest x
                    fourth_main_point = next(
                        p for p in comb if p not in [first_main_point, second_main_point, third_main_point])

                elif all(z == 0.0 for _, _, z in
                         [vertices_dict[id1], vertices_dict[id2], vertices_dict[id3], vertices_dict[id4]]):
                    first_main_point = min(comb, key=lambda p: (p[1][0], p[1][1]))  # Smallest x with biggest y
                    second_main_point = min(comb, key=lambda p: (p[1][0], -p[1][1]))  # Smallest x with smallest y
                    third_main_point = max(comb, key=lambda p: (p[1][0], p[1][1]))  # Biggest x with smallest y
                    fourth_main_point = next(
                        p for p in comb if p not in [first_main_point, second_main_point, third_main_point])

                elif all(z == 1.0 for _, _, z in
                         [vertices_dict[id1], vertices_dict[id2], vertices_dict[id3], vertices_dict[id4]]):
                    first_main_point = min(comb, key=lambda p: (p[1][1], p[1][0]))  # Smallest y with smallest x
                    second_main_point = min(comb, key=lambda p: (p[1][1], -p[1][0]))  # Smallest y with biggest x
                    third_main_point = max(comb, key=lambda p: (p[1][1], p[1][0]))  # Biggest y with biggest x
                    fourth_main_point = next(p for p in comb if p not in [first_main_point, second_main_point, third_main_point])

                result_points[group_name] = (first_main_point, second_main_point, third_main_point, fourth_main_point)
    return result_points

def calculate_lrve_and_tol(node_data):
    nodes = list(node_data.values())
    if not nodes:
        raise ValueError("The nodes list is empty.")

        # Validate that each node is a tuple of length 3
    if not all(isinstance(node, tuple) and len(node) == 3 for node in nodes):
        raise TypeError("Each node must be a tuple with exactly 3 elements (x, y, z).")

        # Calculate the maximum y-coordinate
    lrve = max(node[1] for node in nodes)  # Adjusted to use the second element for y-coordinate

    # Calculate the tolerance
    tol = lrve * 10 ** -4
    return tol

def find_midpoints(main_points, coordinates, tolerance):
    """Calculate the midpoints between main points and find the nearest nodes to these midpoints."""

    def distance(point1, point2):
        """Calculate the Euclidean distance between two points."""
        return np.linalg.norm(np.array(point1) - np.array(point2))

    def find_nearest_node(midpoint, kd_tree, node_ids, coordinates, tolerance):
        """Find the node ID closest to the midpoint within a tolerance using KD-Tree."""
        dist, index = kd_tree.query(midpoint)
        if dist <= tolerance:
            return node_ids[index]
        return None

    def find_midpoint(point1, point2):
        """Find the midpoint between two points."""
        return tuple((p1 + p2) / 2 for p1, p2 in zip(point1, point2))

    # Prepare coordinates for KD-Tree
    node_ids = list(coordinates.keys())
    coords_array = np.array(list(coordinates.values()))
    kd_tree = KDTree(coords_array)

    surafce_points = []
    for group_name, (first_main_point, second_main_point, third_main_point, fourth_main_point) in main_points.items():
        # Extract IDs from the main points
        ids = [point[0] for point in [first_main_point, second_main_point, third_main_point, fourth_main_point]]

        # Get the coordinates using node IDs
        if len(ids) != 4 or not all(id in coordinates for id in ids):
            print(f"Error: Some node IDs for group '{group_name}' are missing in coordinates.")
            continue

        first_coords = coordinates[ids[0]]
        second_coords = coordinates[ids[1]]
        third_coords = coordinates[ids[2]]
        fourth_coords = coordinates[ids[3]]

        # Calculate midpoints
        nearest_first_mid = find_midpoint(first_coords, second_coords)
        nearest_second_mid = find_midpoint(second_coords, third_coords)
        nearest_third_mid = find_midpoint(third_coords, fourth_coords)
        nearest_fourth_mid = find_midpoint(fourth_coords, first_coords)

        # Find nearest nodes to each midpoint
        first_mid_point = find_nearest_node(nearest_first_mid, kd_tree, node_ids, coordinates, tolerance)
        second_mid_point = find_nearest_node(nearest_second_mid, kd_tree, node_ids, coordinates, tolerance)
        third_mid_point = find_nearest_node(nearest_third_mid, kd_tree, node_ids, coordinates, tolerance)
        fourth_mid_point = find_nearest_node(nearest_fourth_mid, kd_tree, node_ids, coordinates, tolerance)

        values = [
            first_main_point[0], second_main_point[0], third_main_point[0], fourth_main_point[0],
            first_mid_point if first_mid_point is not None else 0,
            second_mid_point if second_mid_point is not None else 0,
            third_mid_point if third_mid_point is not None else 0,
            fourth_mid_point if fourth_mid_point is not None else 0
        ]
        formatted_values = ''.join(f'{value:9d}' for value in values)
        surafce_points.append(formatted_values)

    return surafce_points

def write_load_def(surface_element, load_def, surface_index, surface_local_index, mat_ID_index, footer_of_load_def, header_of_load_def):
    with open(load_def, 'w') as w:
        surface_index += 1
        w.write(header_of_load_def + '\n')
        for surface_points in surface_element:
            total_elements = len(surface_points)
            w.write('/com,*********** Define Force Using Surface Effect Elements ***********\n')
            w.write(f'local,{surface_local_index},0,0.,0.,0.,0.,0.,0.\n')
            w.write('csys,0\n')
            w.write(f'et,{mat_ID_index},154\n')
            w.write(f'mat,{mat_ID_index}\n')
            w.write(f'eblock,10,,,{total_elements}\n')
            w.write('(15i9)\n')

            for values in surface_points:
                indexes = [surface_index, mat_ID_index, mat_ID_index, mat_ID_index, surface_local_index]
                formatted_indexes = ''.join(f'{value:9d}' for value in indexes)
                w.write(f'{formatted_indexes}{values}\n')
                surface_index += 1

            w.write('-1\n')
            w.write(f'esel,s,type,,{mat_ID_index}\n')
            w.write(f'keyop,{mat_ID_index},2,1                ! Apply load in local coordinate system\n')
            w.write(f'keyop,{mat_ID_index},7,1                ! Use original area so load is constant in large deformation\n')
            w.write('esel,all\n')

            mat_ID_index += 1
            surface_local_index += 1
        w.write(footer_of_load_def)
    print(f"File 'Load_Def.dat' has been saved")

def voxel_surface_element(surface_local_index, surface_index, output_file, mat_ID_index):

    node_data_path = f'{output_file}/Node_Def.dat'
    element_def_path = f'{output_file}/Elem_Def.dat'
    set_def_path = f'{output_file}/Set_Def.dat'
    load_def = f'{output_file}/Load_Def.dat'
    backList, _ = extract_list(set_def_path, "CMBLOCK,BACK,NODE,", "CMBLOCK,FRONT,NODE,")
    backList = list(map(int, backList))

    leftList, _ = extract_list(set_def_path, "CMBLOCK,LEFT,NODE,", "CMBLOCK,RIGHT,NODE,")
    leftList = list(map(int, leftList))

    bottomList, _ = extract_list(set_def_path, "CMBLOCK,BOTTOM,NODE,", "CMBLOCK,TOP,NODE,")
    bottomList = list(map(int, bottomList))

    rightList, _ = extract_list(set_def_path, "CMBLOCK,RIGHT,NODE,", "CMBLOCK,Bottom_left_back,NODE,")
    rightList = list(map(int, rightList))

    topList, _ = extract_list(set_def_path, "CMBLOCK,TOP,NODE,", "CMBLOCK,LEFT,NODE,")
    topList = list(map(int, topList))

    frontList, _ = extract_list(set_def_path, "CMBLOCK,FRONT,NODE,", "CMBLOCK,BOTTOM,NODE,")
    frontList = list(map(int, frontList))

    faces = [frontList, backList, topList, bottomList, rightList, leftList]


    node_data = read_nodes_from_file(node_data_path)
    surface_data = extract_surface_data(element_def_path)
    tol = calculate_lrve_and_tol(node_data)

    surface_element = []
    for face in faces:
        grouped_data = find_group(surface_data, face, node_data)
        main_points = find_main_points(grouped_data)
        surface_points = find_midpoints(main_points, node_data, tol)
        surface_element.append(surface_points)

    header_of_load_def = '''/com,**** Set Direct FE , Displacements ****
D,Bottom_left_back,ux,0.
D,Bottom_left_back,uy,0.
D,Bottom_left_back,uz,0.

D,BOTTOM_RIGHT_BACK,uy,0.
D,BOTTOM_RIGHT_BACK,uz,0.

D,BOTTOM_LEFT_FRONT,uz,0.
D,BOTTOM_RIGHT_FRONT,uz,0.
nsel,all
    '''
    footer_of_load_def = '''
/com,******************* load Definition X Plus ****************
*DIM,_load_xplus_x,TABLE,3,1,1,TIME,
! Time values
_load_xplus_x(1,0,1) = 0.
_load_xplus_x(2,0,1) = 1.
_load_xplus_x(3,0,1) = end_time
! Load values
_load_xplus_x(1,1,1) = 0.
_load_xplus_x(2,1,1) = xplus_x
_load_xplus_x(3,1,1) = xplus_x

*DIM,_load_xplus_y,TABLE,3,1,1,TIME,
! Time values
_load_xplus_y(1,0,1) = 0.
_load_xplus_y(2,0,1) = 1.
_load_xplus_y(3,0,1) = end_time
! Load values
_load_xplus_y(1,1,1) = 0.
_load_xplus_y(2,1,1) = xplus_y
_load_xplus_y(3,1,1) = xplus_y

*DIM,_load_xplus_z,TABLE,3,1,1,TIME,
! Time values
_load_xplus_z(1,0,1) = 0.
_load_xplus_z(2,0,1) = 1.
_load_xplus_z(3,0,1) = end_time
! Load values
_load_xplus_z(1,1,1) = 0.
_load_xplus_z(2,1,1) = xplus_z
_load_xplus_z(3,1,1) = xplus_z

/com,******************* load Definition X Minus ****************
*DIM,_load_xminus_x,TABLE,3,1,1,TIME,
! Time values
_load_xminus_x(1,0,1) = 0.
_load_xminus_x(2,0,1) = 1.
_load_xminus_x(3,0,1) = end_time
! Load values
_load_xminus_x(1,1,1) = 0.
_load_xminus_x(2,1,1) = xminus_x
_load_xminus_x(3,1,1) = xminus_x

*DIM,_load_xminus_y,TABLE,3,1,1,TIME,
! Time values
_load_xminus_y(1,0,1) = 0.
_load_xminus_y(2,0,1) = 1.
_load_xminus_y(3,0,1) = end_time
! Load values
_load_xminus_y(1,1,1) = 0.
_load_xminus_y(2,1,1) = xminus_y
_load_xminus_y(3,1,1) = xminus_y

*DIM,_load_xminus_z,TABLE,3,1,1,TIME,
! Time values
_load_xminus_z(1,0,1) = 0.
_load_xminus_z(2,0,1) = 1.
_load_xminus_z(3,0,1) = end_time
! Load values
_load_xminus_z(1,1,1) = 0.
_load_xminus_z(2,1,1) = xminus_z
_load_xminus_z(3,1,1) = xminus_z


/com,******************* load Definition Y Plus ****************
*DIM,_load_yplus_x,TABLE,3,1,1,TIME,
! Time values
_load_yplus_x(1,0,1) = 0.
_load_yplus_x(2,0,1) = 1.
_load_yplus_x(3,0,1) = end_time
! Load values
_load_yplus_x(1,1,1) = 0.
_load_yplus_x(2,1,1) = yplus_x
_load_yplus_x(3,1,1) = yplus_x

*DIM,_load_yplus_y,TABLE,3,1,1,TIME,
! Time values
_load_yplus_y(1,0,1) = 0.
_load_yplus_y(2,0,1) = 1.
_load_yplus_y(3,0,1) = end_time
! Load values
_load_yplus_y(1,1,1) = 0.
_load_yplus_y(2,1,1) = yplus_y
_load_yplus_y(3,1,1) = yplus_y

*DIM,_load_yplus_z,TABLE,3,1,1,TIME,
! Time values
_load_yplus_z(1,0,1) = 0.
_load_yplus_z(2,0,1) = 1.
_load_yplus_z(3,0,1) = end_time
! Load values
_load_yplus_z(1,1,1) = 0.
_load_yplus_z(2,1,1) = yplus_z
_load_yplus_z(3,1,1) = yplus_z

/com,******************* load Definition Y Minus ****************
*DIM,_load_yminus_x,TABLE,3,1,1,TIME,
! Time values
_load_yminus_x(1,0,1) = 0.
_load_yminus_x(2,0,1) = 1.
_load_yminus_x(3,0,1) = end_time
! Load values
_load_yminus_x(1,1,1) = 0.
_load_yminus_x(2,1,1) = yminus_x
_load_yminus_x(3,1,1) = yminus_x

*DIM,_load_yminus_y,TABLE,3,1,1,TIME,
! Time values
_load_yminus_y(1,0,1) = 0.
_load_yminus_y(2,0,1) = 1.
_load_yminus_y(3,0,1) = end_time
! Load values
_load_yminus_y(1,1,1) = 0.
_load_yminus_y(2,1,1) = yminus_y
_load_yminus_y(3,1,1) = yminus_y

*DIM,_load_yminus_z,TABLE,3,1,1,TIME,
! Time values
_load_yminus_z(1,0,1) = 0.
_load_yminus_z(2,0,1) = 1.
_load_yminus_z(3,0,1) = end_time
! Load values
_load_yminus_z(1,1,1) = 0.
_load_yminus_z(2,1,1) = yminus_z
_load_yminus_z(3,1,1) = yminus_z


/com,******************* load Definition Z Plus ****************
*DIM,_load_zplus_x,TABLE,3,1,1,TIME,
! Time values
_load_zplus_x(1,0,1) = 0.
_load_zplus_x(2,0,1) = 1.
_load_zplus_x(3,0,1) = end_time
! Load values
_load_zplus_x(1,1,1) = 0.
_load_zplus_x(2,1,1) = zplus_x
_load_zplus_x(3,1,1) = zplus_x

*DIM,_load_zplus_y,TABLE,3,1,1,TIME,
! Time values
_load_zplus_y(1,0,1) = 0.
_load_zplus_y(2,0,1) = 1.
_load_zplus_y(3,0,1) = end_time
! Load values
_load_zplus_y(1,1,1) = 0.
_load_zplus_y(2,1,1) = zplus_y
_load_zplus_y(3,1,1) = zplus_y

*DIM,_load_zplus_z,TABLE,3,1,1,TIME,
! Time values
_load_zplus_z(1,0,1) = 0.
_load_zplus_z(2,0,1) = 1.
_load_zplus_z(3,0,1) = end_time
! Load values
_load_zplus_z(1,1,1) = 0.
_load_zplus_z(2,1,1) = zplus_z
_load_zplus_z(3,1,1) = zplus_z

/com,******************* load Definition Z Minus ****************
*DIM,_load_zminus_x,TABLE,3,1,1,TIME,
! Time values
_load_zminus_x(1,0,1) = 0.
_load_zminus_x(2,0,1) = 1.
_load_zminus_x(3,0,1) = end_time
! Load values
_load_zminus_x(1,1,1) = 0.
_load_zminus_x(2,1,1) = zminus_x
_load_zminus_x(3,1,1) = zminus_x

*DIM,_load_zminus_y,TABLE,3,1,1,TIME,
! Time values
_load_zminus_y(1,0,1) = 0.
_load_zminus_y(2,0,1) = 1.
_load_zminus_y(3,0,1) = end_time
! Load values
_load_zminus_y(1,1,1) = 0.
_load_zminus_y(2,1,1) = zminus_y
_load_zminus_y(3,1,1) = zminus_y

*DIM,_load_zminus_z,TABLE,3,1,1,TIME,
! Time values
_load_zminus_z(1,0,1) = 0.
_load_zminus_z(2,0,1) = 1.
_load_zminus_z(3,0,1) = end_time
! Load values
_load_zminus_z(1,1,1) = 0.
_load_zminus_z(2,1,1) = zminus_z
_load_zminus_z(3,1,1) = zminus_z
'''
    write_load_def(surface_element, load_def, surface_index, surface_local_index, mat_ID_index, footer_of_load_def, header_of_load_def)
