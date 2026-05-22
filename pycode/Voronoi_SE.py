import itertools
import math

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

    try:
        with open(set_def_path, 'r') as infile:
            lines = infile.readlines()

        for line in lines:
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

    except FileNotFoundError:
        print(f"Error: The file '{set_def_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while extracting data: {e}")

    return data

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

def extract_surface_data_sep(element_def_path):
    surface_data = {}
    used_lines = set()  # Track used lines
    element_index = 0
    try:
        with open(element_def_path, 'r') as file:
            lines = file.readlines()
            num_lines = len(lines)
            for line in lines:
                if 'SOLID186' in line:
                    element_index += 1
            i = 0
            while i < num_lines:
                # Ensure we're not reprocessing a used line
                if i in used_lines:
                    i += 1
                    continue

                line1 = lines[i].strip()
                line2 = lines[i + 1].strip() if i + 1 < num_lines else ""

                # Check if both lines are valid (containing only digits)
                valid_line1 = all(part.isdigit() for part in line1.split())
                valid_line2 = all(part.isdigit() for part in line2.split())

                if valid_line1 and valid_line2:
                    # Combine lines and split them
                    combined_line = f"{line1} {line2}"
                    combined_line_parts = combined_line.split()

                    # Ensure there are enough parts to avoid IndexError
                    if len(combined_line_parts) >= 12:
                        surface_id = combined_line_parts[10]
                        nodes = combined_line_parts[11:]
                        surface_data[surface_id] = nodes

                        # Mark these lines as used
                        used_lines.add(i)
                        used_lines.add(i + 1)
                    else:
                        print(f"Warning: Not enough parts in combined line to extract surface_id and nodes.")
                else:
                    # If the current line is invalid, mark it as used to avoid infinite loop
                    used_lines.add(i)

                # Move to the next line
                i += 1

    except FileNotFoundError:
        print(f"Error: The file '{element_def_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while extracting surface data: {e}")

    return surface_data

def find_group(surface_data, leftList, node_data):
    front_set = set(leftList)
    seen_surfaces = set()  # Set to track already processed surface IDs

    # Initialize a dictionary to store grouped data
    grouped_data = {}

    # Initialize a counter for matching surface IDs
    matching_surface_id_count = 0

    # Iterate through each surface_id in surface_data
    for surface_id, nodes in surface_data.items():
        # Convert nodes to integers
        try:
            nodes = list(map(int, nodes))
        except ValueError:
            continue  # Skip invalid entries

        # Skip empty node lists
        if not nodes:
            continue

        # Check if the surface has at least 6 nodes
        if len(nodes) >= 6:
            # Find the intersection of surface nodes with leftList nodes
            common_nodes = [node for node in nodes if node in front_set]

            # Check if this surface_id has not been seen before and has exactly 6 common nodes
            if surface_id not in seen_surfaces and len(common_nodes) == 6:
                seen_surfaces.add(surface_id)
                matching_surface_id_count += 1

                # Append coordinates to the common_nodes in grouped_data
                grouped_data[surface_id] = [(node, node_data[node]) for node in common_nodes if node in node_data]

    # Return the grouped data
    return grouped_data

def find_main_points(nodes):
    def calculate_area(x1, y1, x2, y2, x3, y3):
        return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0

    def calculate_2d_area(p1, p2, p3):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0

    max_triangles = {}

    for group_name, vertices in nodes.items():
        # Check if vertices is a list and convert it to a dictionary
        if isinstance(vertices, list):
            vertices_dict = {vertex[0]: vertex[1] for vertex in vertices}
        elif isinstance(vertices, dict):
            vertices_dict = vertices
        else:
            print(f"Skipping group {group_name} because its data is neither a list nor a dictionary: {vertices}")
            continue

        max_triangle = None
        max_area = 0

        # Validate that each vertex in vertices_dict is a tuple of 3 numbers
        valid_vertices = True
        for vertex_id, coords in vertices_dict.items():
            if not (isinstance(coords, tuple) and len(coords) == 3 and all(isinstance(c, (int, float)) for c in coords)):
                print(f"Invalid coordinates for vertex {vertex_id} in group {group_name}: {coords}")
                valid_vertices = False
                break

        if not valid_vertices:
            continue

        # Iterate over combinations of 3 vertices
        for (id1, (x1, y1, z1)), (id2, (x2, y2, z2)), (id3, (x3, y3, z3)) in itertools.combinations(vertices_dict.items(), 3):
            # Select appropriate coordinates for 2D area calculation
            if (x1 == 0.0 and x2 == 0.0 and x3 == 0.0) or (x1 == 1.0 and x2 == 1.0 and x3 == 1.0):
                # All x are zero, use y and z
                area = calculate_2d_area((y1, z1), (y2, z2), (y3, z3))
            elif (y1 == 0.0 and y2 == 0.0 and y3 == 0.0) or (y1 == 1.0 and y2 == 1.0 and y3 == 1.0):
                # All y are zero, use x and z
                area = calculate_2d_area((x1, z1), (x2, z2), (x3, z3))
            elif (z1 == 0.0 and z2 == 0.0 and z3 == 0.0) or (z1 == 1.0 and z2 == 1.0 and z3 == 1.0):
                # All z are zero, use x and y
                area = calculate_2d_area((x1, y1), (x2, y2), (x3, y3))
            else:
                # Default case, use all coordinates
                area = calculate_area(x1, y1, x2, y2, x3, y3)

            if area > max_area:
                max_triangle = {
                    'vertices': (id1, id2, id3),
                    'coords': [(x1, y1), (x2, y2), (x3, y3)],
                }
                max_area = area

        if max_triangle:
            max_triangles[group_name] = max_triangle
        else:
            print(f"No valid triangles found for group {group_name}")

    return max_triangles

def find_mid_points(triangle, nodes):
    id1, id2, id3 = triangle['vertices']
    coords = {id1: triangle['coords'][0], id2: triangle['coords'][1], id3: triangle['coords'][2]}

    def midpoint(x1, y1, x2, y2):
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def find_nearest_node(midpoint, nodes):
        min_distance = float('inf')
        nearest_id = None
        mx, my = midpoint

        # Ensure nodes is a dictionary
        if isinstance(nodes, list):
            nodes_dict = {node[0]: node[1] for node in nodes}
        elif isinstance(nodes, dict):
            nodes_dict = nodes
        else:
            raise TypeError(f"Invalid type for nodes: {type(nodes)}")

        # Find the nearest node
        for node_id, (x, y, _) in nodes_dict.items():
            distance = math.sqrt((x - mx) ** 2 + (y - my) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_id = node_id

        return nearest_id

    midpoints = {
        (id1, id2): midpoint(*coords[id1], *coords[id2]),
        (id2, id3): midpoint(*coords[id2], *coords[id3]),
        (id1, id3): midpoint(*coords[id1], *coords[id3]),
    }

    nearest_nodes = {pair: find_nearest_node(midpoint, nodes) for pair, midpoint in midpoints.items()}

    return nearest_nodes

def surface_points_def(main_point, filtered_surface_data):
    surface_points = []
    for group, triangle in main_point.items():
        nearest_nodes = find_mid_points(triangle, filtered_surface_data[group])
        main_point_first, main_point_second, main_point_third = triangle['vertices']
        mid_point_first, mid_point_second, mid_point_third = [nearest_id for (_, nearest_id) in nearest_nodes.items()]

        values = [
           main_point_first, main_point_second, main_point_third, main_point_third,
            mid_point_first, mid_point_second, main_point_third, mid_point_third
        ]

        formatted_values = ''.join(f'{value:9d}' for value in values)
        surface_points.append(formatted_values)
    return surface_points

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

def voronoi_surface_element(surface_local_index, surface_index, output_file, Interfaces, mat_ID_index):
    # Example usage
    if Interfaces == 'True':
        node_data_path = f'{output_file}/Node_Sep_Def.dat'
        element_def_path = f'{output_file}/Elem_Sep_Def.dat'
        set_def_path = f'{output_file}/Set_Sep_Def.dat'
        surface_data = extract_surface_data_sep(element_def_path)
    else:
        node_data_path = f'{output_file}/Node_Def.dat'
        element_def_path = f'{output_file}/Elem_Def.dat'
        set_def_path = f'{output_file}/Set_Def.dat'
        surface_data = extract_surface_data(element_def_path)
    load_def = f'{output_file}/Load_Def.dat'
    backList = list(map(int, extract_list(set_def_path, "CMBLOCK,BACK,NODE,", "CMBLOCK,FRONT,NODE,")))
    frontList = list(map(int, extract_list(set_def_path, "CMBLOCK,FRONT,NODE,", "CMBLOCK,BOTTOM,NODE,")))
    bottomList = list(map(int, extract_list(set_def_path, "CMBLOCK,BOTTOM,NODE,", "CMBLOCK,TOP,NODE,")))
    topList = list(map(int, extract_list(set_def_path, "CMBLOCK,TOP,NODE,", "CMBLOCK,LEFT,NODE,")))
    leftList = list(map(int, extract_list(set_def_path, "CMBLOCK,LEFT,NODE,", "CMBLOCK,RIGHT,NODE,")))
    rightList = list(map(int, extract_list(set_def_path, "CMBLOCK,RIGHT,NODE,", "CMBLOCK,Bottom_left_back,NODE,")))
    faces = [rightList, leftList, topList, bottomList, frontList, backList]

    node_data = read_nodes_from_file(node_data_path)
    tol = calculate_lrve_and_tol(node_data)

    surface_element = []
    for face in faces:
        grouped_data = find_group(surface_data, face, node_data)
        main_point = find_main_points(grouped_data)
        surface_points = surface_points_def(main_point, grouped_data)
        surface_element.append(surface_points)

    header_of_load_def ='''/com,**** Set Direct FE , Displacements ****
D,Bottom_left_back,ux,0.
D,Bottom_left_back,uy,0.
D,Bottom_left_back,uz,0.

D,BOTTOM_RIGHT_BACK,uy,0.
D,BOTTOM_RIGHT_BACK,uz,0.

D,BOTTOM_LEFT_FRONT,uz,0.
D,BOTTOM_RIGHT_FRONT,uz,0.
nsel,all'''
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
    write_load_def(surface_element, load_def, surface_index, surface_local_index,mat_ID_index, footer_of_load_def, header_of_load_def)




