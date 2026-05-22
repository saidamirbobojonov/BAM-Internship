import pandas as pd
import numpy as np


def nodes_corner(filename, node_number, dim_len=1.0, tol=1e-7):
    new_first_number = []
    try:
        # Open input file and prepare to store filtered lines
        nodes = []

        # Read data from the input file
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Process each line
        for line in lines:
            stripped_line = line.strip()
            parts = stripped_line.split(',')

            # Check if the line starts with an integer and contains a decimal number
            if parts[0].strip().isdigit():
                contains_decimal = False
                for part in parts[1:]:  # Skip the first part as it is the node number
                    try:
                        float_value = float(part.strip())
                        if '.' in part or 'e' in part.lower():
                            contains_decimal = True
                            break
                    except ValueError:
                        pass

                if contains_decimal:
                    # Add node_number to the first number in parts[0]
                    try:
                        first_number = float(parts[0].strip())
                        new_number = int(first_number + (node_number - 1))
                        new_first_number.append(new_number)
                        parts[0] = str(new_number)

                        # Remove extra spaces and indentation, retain commas
                        cleaned_parts = [part.strip() for part in parts]
                        cleaned_line = ','.join(cleaned_parts)
                        nodes.append(cleaned_parts[1:])  # Store coordinates only (skip node number)
                    except ValueError:
                        pass

        # Convert nodes to a numpy array
        nodes = np.array(nodes, dtype=float)

        # Identify the nodes at the corners
        bottom_left_back = np.where(
            (np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) &
            (np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) &
            (np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol))
        )[0]

        top_left_back = np.where(
            (np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) &
            (np.isclose(nodes[:, 1], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol))
        )[0]

        bottom_right_back = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) &
            (np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol))
        )[0]

        top_right_back = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 1], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 2], np.amin(nodes[:, 2]), atol=tol))
        )[0]

        bottom_left_front = np.where(
            (np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) &
            (np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) &
            (np.isclose(nodes[:, 2], dim_len, atol=tol))
        )[0]

        top_left_front = np.where(
            (np.isclose(nodes[:, 0], np.amin(nodes[:, 0]), atol=tol)) &
            (np.isclose(nodes[:, 1], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 2], dim_len, atol=tol))
        )[0]

        bottom_right_front = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 1], np.amin(nodes[:, 1]), atol=tol)) &
            (np.isclose(nodes[:, 2], dim_len, atol=tol))
        )[0]

        top_right_front = np.where(
            (np.isclose(nodes[:, 0], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 1], dim_len, atol=tol)) &
            (np.isclose(nodes[:, 2], dim_len, atol=tol))
        )[0]

        corners = [
            bottom_left_back, bottom_left_front, bottom_right_back, bottom_right_front, top_left_back, top_left_front,
            top_right_back, top_right_front]

        corners = [corner + node_number for corner in corners]
        return corners
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
def node_def(filename, node_number):
    # Function logic to process the file and modify node numbers
    new_first_number = []
    try:
        # Open input file and prepare to store filtered lines
        filtered_lines = []
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                stripped_line = line.strip()
                parts = stripped_line.split(',')
                if parts[0].strip().isdigit():
                    contains_decimal = False
                    for part in parts:
                        try:
                            float_value = float(part.strip())
                            if '.' in part or 'e' in part.lower():
                                contains_decimal = True
                                break
                        except ValueError:
                            pass
                    if contains_decimal:
                        try:
                            first_number = float(parts[0].strip())
                            new_number = int(first_number + (node_number - 1))
                            new_first_number.append(new_number)
                            parts[0] = str(new_number)
                            cleaned_parts = [part.strip() for part in parts]
                            cleaned_line = ','.join(cleaned_parts)
                            processed_line = f"N,{cleaned_line}"
                            filtered_lines.append(processed_line)
                        except ValueError:
                            pass
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        new_first_number = []
    return new_first_number
def import_element_polygon(input_file):
    capture_data = False
    current_elset_name = None
    element_polygon = {}

    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()

        for line in lines:
            # Skip lines containing '*End Part'
            if '*Nset' in line:
                break

            if '*Elset' in line:
                if current_elset_name:
                    # Append the current data to the corresponding Elset
                    element_polygon[current_elset_name] = current_data

                # Extract the name of the Elset
                parts = line.split(',')
                for part in parts:
                    if 'elset=' in part:
                        current_elset_name = part.split('=')[1].strip()
                        break

                current_data = []
                capture_data = True
                continue

            if capture_data:
                cleaned_line = line.replace(',', '')
                numbers = cleaned_line.split()
                current_data.extend(numbers)

        if current_elset_name:
            element_polygon[current_elset_name] = current_data

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred while importing element polygons: {e}")
    return element_polygon
def import_nodes_element(input_file, node_number):
    capture_data = False
    node_data = {}

    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()

        for line in lines:
            # Check if the line indicates the start of element data
            if '*Element' in line:
                capture_data = True
                continue  # Skip the line containing '*Element'

            # Stop capturing if the line indicates the start of Elset
            if '*Elset' in line:
                capture_data = False
                continue

            # Process lines while capturing data
            if capture_data:
                cleaned_line = line.strip().replace(',', '')
                numbers = cleaned_line.split()

                if numbers:  # Ensure the line is not empty
                    index = numbers[0]
                    data = data = [str(int(num) + (node_number - 1)) for num in numbers[1:]]
                    node_data[index] = data

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred while importing node indices: {e}")
    return node_data
def extract_and_format_data(input_file):
    try:
        capture_data = False
        all_data = []
        formatted_data = []

        with open(input_file, 'r') as infile:
            lines = infile.readlines()

        for line in lines:
            if '*End Part' in line:
                continue
            if '*Nset' in line:
                if all_data:
                    # Format collected data
                    formatted_lines = []
                    num_count = 0
                    formatted_line = ''
                    for num in all_data:
                        formatted_line += f"{num:>10}"
                        num_count += 1
                        if num_count == 8:
                            formatted_lines.append(formatted_line)
                            formatted_line = ''
                            num_count = 0
                    if num_count > 0:
                        formatted_lines.append(formatted_line)

                    # Append formatted lines to list
                    formatted_data.append({'FormattedData': formatted_lines})

                    all_data = []
                capture_data = True
                continue

            if capture_data:
                cleaned_line = line.replace(',', '')
                numbers = cleaned_line.split()
                all_data.extend(numbers)

        if all_data:
            # Format the last collected data
            formatted_lines = []
            num_count = 0
            formatted_line = ''
            for num in all_data:
                formatted_line += f"{num:>10}"
                num_count += 1
                if num_count == 8:
                    formatted_lines.append(formatted_line)
                    formatted_line = ''
                    num_count = 0
            if num_count > 0:
                formatted_lines.append(formatted_line)

            # Append formatted lines to list
            formatted_data.append({'FormattedData': formatted_lines})

        return pd.DataFrame(formatted_data)

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()
def write_indices_to_file(new_first_number, element_polygon, output_file, node_number, df_set, corner):
    set_def_path = f'{output_file}/Set_Def.dat'
    try:
        # Convert numbers to integers and find the maximum number
        indices = [int(round(num)) for num in new_first_number]
        max_number = int(round(max(new_first_number)))

        # Create lines for writing to the file
        lines = []
        for i in range(0, len(indices), 8):
            line = ""
            for j in range(8):
                if i + j < len(indices):
                    # Format the number to occupy 10 characters
                    line += f"{indices[i + j]:>10}"
                else:
                    # Add empty space if there are no more numbers
                    line += " " * 10
            lines.append(line)

        # Write to the file
        with open(set_def_path, 'w') as file:
            file.write(f"CMBLOCK, ALL_NODES ,NODE,     {max_number}\n")
            file.write(f"(8i10)\n")
            for line in lines:
                file.write(line + "\n")

            # Write formatted data for df_set

            # Write CMBLOCK rows for element_polygon
            cycle_count = 1
            for elset, numbers in element_polygon.items():
                count_elem = len(numbers)
                file.write(f"CMBLOCK,Grain_{cycle_count},ELEM,   {count_elem}\n")
                file.write(f"(8i10)\n")

                # Writing numbers in 8i10 format
                indices = [int(round(int(num))) for num in numbers]
                for i in range(0, len(indices), 8):
                    line = ""
                    for j in range(8):
                        if i + j < len(indices):
                            # Format each number to occupy 10 characters
                            line += f"{indices[i + j]:>10}"
                        else:
                            # Add empty spaces if there are fewer than 8 numbers in the last line
                            line += " " * 10
                    file.write(line + "\n")

                cycle_count += 1
            name_cmb = ['BACK', 'FRONT', 'BOTTOM', 'TOP', 'LEFT', 'RIGHT']
            i = 0

            for index, row in df_set.iterrows():
                acc = 0  # Reset the accumulator for each group
                updated_numbers = []  # List to store all updated node numbers

                for formatted_line in row['FormattedData']:
                    node_numbers_faces = formatted_line.split()  # Assuming space-separated node numbers
                    updated_numbers.extend(
                        [int(node_number_face) + (node_number - 1) for node_number_face in
                         node_numbers_faces])  # Increment each number
                    acc += len(node_numbers_faces)  # Accumulate the count

                file.write(f"CMBLOCK,{name_cmb[i]},NODE,    {acc}\n")  # Write the accumulated count
                file.write(f"(8i10)\n")  # Write the format for node output

                # Write the updated numbers in (8i10) format
                for j in range(0, len(updated_numbers), 8):
                    line_numbers = updated_numbers[j:j + 8]  # Get up to 8 numbers for the current line
                    formatted_line = ''.join(
                        f"{num:>10}" for num in line_numbers)  # Format each number in a field of 10 characters
                    file.write(formatted_line + '\n')  # Write the formatted line

                i += 1
            corner_names = [
                "Bottom_left_back", "Bottom_left_front", "Bottom_right_back", "Bottom_right_front",
                "Top_left_back", "Top_left_front", "Top_right_back", "Top_right_front"
            ]

            # Write CMBLOCK rows for corners
            for name, corners_list in zip(corner_names, corner):
                file.write(f"CMBLOCK,{name},NODE,   {len(corners_list)}\n")
                file.write(f"(8i10)\n")
                # Write node indices for corners with formatting
                for i in range(0, len(corners_list), 8):
                    line = ""
                    for j in range(8):
                        if i + j < len(corners_list):
                            line += f"{int(corners_list[i + j]):>10}"
                        else:
                            line += " " * 10
                    file.write(line + "\n")

        print(f"File 'Set_Def.dat' has been saved")

    except FileNotFoundError:
        print(f"Error: The file '{set_def_path}' path does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def set_def(input_file, output_file, node_number):
    corner = nodes_corner(input_file, node_number, dim_len=1.0, tol=1e-7)
    new_first_number = node_def(input_file, node_number)
    element_polygon = import_element_polygon(input_file)
    node_data = import_nodes_element(input_file, node_number)
    df_set = extract_and_format_data(input_file)
    write_indices_to_file(new_first_number, element_polygon, output_file, node_number, df_set, corner)
            