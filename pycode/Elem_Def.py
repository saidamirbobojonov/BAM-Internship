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
                cleaned_line = line.strip()
                if cleaned_line:  # Ensure the line is not empty
                    numbers = cleaned_line.split(',')
                    index = numbers[0].strip()
                    data = [str(int(num.strip()) + (node_number - 1)) for num in numbers[1:]]
                    node_data[index] = data

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred while importing node indices: {e}")

    return node_data
def write_element_def(node_data, element_polygon, output_file, model_type):
    element_def_path = f'{output_file}/Elem_Def.dat'
    try:
        with open(element_def_path, 'w') as outfile:
            cycle_count = 1
            for elset, numbers in element_polygon.items():
                if model_type == 'Voxel':
                    outfile.write(f"Et,{cycle_count},SOLID186\n")
                elif model_type == 'Voronoi':
                    outfile.write(f"Et,{cycle_count},SOLID187\n")
                outfile.write(f"Mat,{cycle_count}\n")
                outfile.write(f"Type,{cycle_count}\n")

                for num in numbers:
                    if num in node_data:
                        row_values = node_data[num]
                        row_values_stripped = [str(value).strip() for value in row_values]
                        values_string = ','.join(row_values_stripped)
                        values_list = values_string.split(',')
                        chunks = [values_list[i:i + 8] for i in range(0, len(values_list), 8)]
                        outfile.write(f"EN,{num},{','.join(chunks[0])}\n")
                        for chunk in chunks[1:]:
                            outfile.write(f"EMORE,{','.join(chunk)}\n")
                cycle_count += 1
        print("File 'Elem_Def.dat' has been saved")
    except IOError as e:
        print(f"An error occurred while writing to the file '{output_file}': {e}")
def element_def(input_file, output_file, node_number, model_type):
    element_polygon = import_element_polygon(input_file)
    node_data = import_nodes_element(input_file, node_number)
    write_element_def(node_data, element_polygon, output_file, model_type)

