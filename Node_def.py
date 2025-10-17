def node_def(input_file, output_file, node_number, nodes_length_type):
    node_def_path = f'{output_file}/Node_Def.dat'
    # Function logic to process the file and modify node numbers
    new_first_number = []
    try:
        # Open input file and prepare to store filtered lines
        filtered_lines = []
        with open(input_file, 'r') as file:
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

                            # New block to convert coordinates from µm to mm
                            if nodes_length_type == 'µm':
                                for i in range(1, len(parts)):  # Start from index 1 to skip the first number
                                    try:
                                        coord_um = float(parts[i].strip())
                                        coord_mm = coord_um / 1000  # Convert from µm to mm
                                        parts[i] = str(coord_mm)
                                    except ValueError:
                                        # Handle case where conversion fails, e.g., non-numeric value
                                        pass

                            cleaned_parts = [part.strip() for part in parts]
                            cleaned_line = ','.join(cleaned_parts)
                            processed_line = f"N,{cleaned_line}"
                            filtered_lines.append(processed_line)
                        except ValueError:
                            pass

        with open(node_def_path, 'w') as file:
            for line in filtered_lines:
                file.write(line + '\n')
        print("File 'Node_Def.dat' has been saved")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        new_first_number = []

    return new_first_number

