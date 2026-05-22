import numpy as np
from scipy.spatial import distance_matrix
from datetime import datetime

def CE_def(output_file, input_file, node_number):
    def import_nodes(nodeDef):
        nodes = []
        node_data = {}
        try:
            with open(nodeDef, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    nodNum = int(parts[1].strip())
                    x = float(parts[2].strip())
                    y = float(parts[3].strip())
                    z = float(parts[4].strip())
                    nodes.append([nodNum, x, y, z])
                    node_data[nodNum] = (x, y, z)
        except FileNotFoundError:
            print(f"Error: The file '{nodeDef}' does not exist.")
        except Exception as e:
            print(f"An error occurred while importing nodes: {e}")

        return nodes, node_data

    def import_nodes_side(setDef, node_number):
        capture_data = False
        current_nset_name = None
        grouped_data = []

        try:
            with open(setDef, 'r') as infile:
                lines = infile.readlines()

            for line in lines:
                # Skip lines containing '*End Part'
                if '*End Part' in line:
                    continue

                if '*Nset' in line:
                    if current_nset_name:
                        grouped_data.append({'NsetName': current_nset_name, 'Data': current_data})

                    # Extract the name of the Nset
                    parts = line.split(',')
                    for part in parts:
                        if 'nset=' in part:
                            current_nset_name = part.split('=')[1].strip()
                            break

                    current_data = []
                    capture_data = True
                    continue

                if capture_data:
                    cleaned_line = line.replace(',', '')
                    numbers = cleaned_line.split()
                    current_data.extend(numbers)

            if current_nset_name:
                grouped_data.append({'NsetName': current_nset_name, 'Data': current_data})

        except FileNotFoundError:
            print(f"Error: The file '{setDef}' does not exist.")
        except Exception as e:
            print(f"An error occurred while importing node indices: {e}")
        for group in grouped_data:
            group['Data'] = [str(int(num) + (node_number - 1)) for num in group['Data']]
        return grouped_data

    def calculate_lrve_and_tol(node_data):
        nodes = list(node_data.values())
        if not nodes:
            raise ValueError("The nodes list is empty.")

            # Validate that each node is a tuple of length 3
        if not all(isinstance(node, tuple) and len(node) == 3 for node in nodes):
            raise TypeError("Each node must be a tuple with exactly 3 elements (x, y, z).")

            # Calculate the maximum y-coordinate
        l = max(node[1] for node in nodes)  # Adjusted to use the second element for y-coordinate

        # Calculate the tolerance
        tol = l * 10 ** -4
        return l, tol

    def create_massive_from_grouped_data(grouped_data):
        massive = []
        for group in grouped_data:
            massive.append(group['Data'])
        return massive

    def find_x_pairs(nodes, massive, tol):
        # Extract limits from the massive array
        x_plus = np.array(massive[0], dtype=int)
        x_minus = np.array(massive[1], dtype=int)

        # Create a mapping from nodNum to index
        nodNum_to_index = {node[0]: index for index, node in enumerate(nodes)}

        # Initialize lists to store results
        pairs_x = []
        used_nodes = set()  # Keep track of used node numbers

        # Loop through each node in x_plus and x_minus
        for numi in x_plus:
            if numi in nodNum_to_index:  # Ensure numi is valid
                index_i = nodNum_to_index[numi]
                x1, y1, z1 = nodes[index_i][1:4]  # Coordinates of node from x_plus

                for numj in x_minus:
                    if numj in nodNum_to_index:  # Ensure numj is valid
                        index_j = nodNum_to_index[numj]
                        x2, y2, z2 = nodes[index_j][1:4]  # Coordinates of node from x_minus

                        # Check if y and z coordinates are the same
                        if y1 == y2 and z1 == z2 or (y2 - tol <= y1 <= y2 + tol) and (z2 - tol <= z1 <= z2 + tol):
                            pairs_x.append((nodes[index_i][0], nodes[index_j][0]))  # Append the node numbers as a tuple
                            used_nodes.add(nodes[index_i][0])  # Mark node as used
                            used_nodes.add(nodes[index_j][0])  # Mark node as used

        # Create a new list of nodes excluding the used ones
        nodes_y = [node for node in nodes if node[0] not in used_nodes]

        return nodes_y, pairs_x  # Return the new nodes list

    def find_y_pairs(nodes_y, massive, tol):
        # Extract limits from the massive array
        y_plus = np.array(massive[2], dtype=int)
        y_minus = np.array(massive[3], dtype=int)

        # Create a mapping from nodNum to index
        nodNum_to_index = {node[0]: index for index, node in enumerate(nodes_y)}  # Use nodes_new

        # Initialize lists to store results
        pairs_y = []
        used_nodes = set()  # Track used node numbers

        # Loop through each node in y_plus and y_minus
        for numi in y_plus:
            if numi in nodNum_to_index:  # Ensure numi is valid
                index_i = nodNum_to_index[numi]
                x1, y1, z1 = nodes_y[index_i][1:4]  # Coordinates of node from y_plus

                for numj in y_minus:
                    if numj in nodNum_to_index:  # Ensure numj is valid
                        index_j = nodNum_to_index[numj]
                        x2, y2, z2 = nodes_y[index_j][1:4]  # Coordinates of node from y_minus

                        # Check if x and z coordinates are the same
                        if x1 == x2 and z1 == z2 or (x2 - tol <= x1 <= x2 + tol) and (z2 - tol <= z1 <= z2 + tol):
                            pairs_y.append(
                                (nodes_y[index_i][0], nodes_y[index_j][0]))  # Append the node numbers as a tuple
                            used_nodes.add(nodes_y[index_i][0])  # Mark node as used
                            used_nodes.add(nodes_y[index_j][0])  # Mark node as used

        # Create a new list of nodes excluding the used ones
        nodes_z = [node for node in nodes_y if node[0] not in used_nodes]

        return nodes_z, pairs_y  # Return the filtered nodes list

    def find_z_pairs(nodes_z, massive, tol):
        # Extract limits from the massive array
        z_plus = np.array(massive[4], dtype=int)
        z_minus = np.array(massive[5], dtype=int)

        # Create a mapping from nodNum to index
        nodNum_to_index = {node[0]: index for index, node in enumerate(nodes_z)}

        # Initialize lists to store results
        pairs_z = []
        used_nodes = set()
        # Loop through each node in x_plus and x_minus
        for numi in z_plus:
            if numi in nodNum_to_index:  # Ensure numi is valid
                index_i = nodNum_to_index[numi]
                x1, y1, z1 = nodes_z[index_i][1:4]  # Coordinates of node from x_plus

                for numj in z_minus:
                    if numj in nodNum_to_index:  # Ensure numj is valid
                        index_j = nodNum_to_index[numj]
                        x2, y2, z2 = nodes_z[index_j][1:4]  # Coordinates of node from x_minus

                        # Check if y and z coordinates are the same
                        if x1 == x2 and y1 == y2 or (x2 - tol <= x1 <= x2 + tol) and (y2 - tol <= y1 <= y2 + tol):
                            pairs_z.append((nodes_z[index_i][0],
                                            nodes_z[index_j][0]))
                            used_nodes.add(nodes_z[index_i][0])  # Mark node as used
                            used_nodes.add(nodes_z[index_j][0])
        nodes_x = [node for node in nodes_z if node[0] not in used_nodes]
        return pairs_z

    def write_pairs(pairs_x, pairs_y, pairs_z, output_file, l):
        CE_output_file = f'{output_file}/CE_Def.dat'
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Write pairs to a new file
        with open(CE_output_file, 'w') as out:
            out.write("/com *************************************** \n")
            out.write(f"/com Generated on {current_time}  with Python \n")
            out.write("/com *************************************** \n")
            out.write("/com **************** Face X node Pairs **************** \n")
            for pair in pairs_x:
                out.write(f"CE, next, 0, {pair[0]}, UX, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UX, -1 \n")
                out.write(f"CE, high, 0, 1, UX, {l} \n")
                out.write(f"CE, next, 0, {pair[0]}, UY, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UY, -1 \n")
                out.write(f"CE, high, 0, 2, UX, {l} \n")
                out.write(f"CE, next, 0, {pair[0]}, UZ, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UZ, -1 \n")
                out.write(f"CE, high, 0, 2, UZ, {l} \n")
            out.write("/com **************** Face Y node Pairs **************** \n")
            for pair in pairs_y:
                out.write(f"CE, next, 0, {pair[0]}, UX, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UX, -1 \n")
                out.write(f"CE, high, 0, 1, UX, {l} \n")
                out.write(f"CE, next, 0, {pair[0]}, UY, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UY, -1 \n")
                out.write(f"CE, high, 0, 2, UX, {l} \n")
                out.write(f"CE, next, 0, {pair[0]}, UZ, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UZ, -1 \n")
                out.write(f"CE, high, 0, 2, UZ, {l} \n")
            out.write("/com **************** Face Z node Pairs **************** \n")
            for pair in pairs_z:
                out.write(f"CE, next, 0, {pair[0]}, UX, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UX, -1 \n")
                out.write(f"CE, high, 0, 1, UX, {l} \n")
                out.write(f"CE, next, 0, {pair[0]}, UY, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UY, -1 \n")
                out.write(f"CE, high, 0, 2, UX, {l} \n")
                out.write(f"CE, next, 0, {pair[0]}, UZ, 1 \n")
                out.write(f"CE, high, 0, {pair[1]}, UZ, -1 \n")
                out.write(f"CE, high, 0, 2, UZ, {l} \n")
            out.write("/com **************** End CE Equiation ****************  \n")
        print("Pairs written to 'CE_Def.dat'")
        x = len(pairs_x)
        y = len(pairs_y)
        z = len(pairs_z)

    # Example usage
    nodes, node_data = import_nodes(f'{output_file}/Node_Def.dat')
    grouped_data = import_nodes_side(input_file, node_number)
    l,tol = calculate_lrve_and_tol(node_data)
    massive = create_massive_from_grouped_data(grouped_data)
    nodes_y, pairs_x = find_x_pairs(nodes, massive, tol)
    nodes_z, pairs_y = find_y_pairs(nodes_y, massive, tol)
    pairs_z = find_z_pairs(nodes_z, massive, tol)
    write_pairs(pairs_x, pairs_y, pairs_z, output_file, l)