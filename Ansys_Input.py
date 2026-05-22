def ansys_input_file(input_file, target_words, replacement_word, sign_delete, output_file_path):
    with open(input_file, 'r') as infile:
        content = infile.readlines()

    for filenames, replacements in replacement_word.items():
        output_file = f'{output_file_path}/{filenames}.inp'
        with open(output_file, 'w') as outfile:
            for line in content:
                for name in sign_delete:
                    if name in line :
                        line = line.replace('!', '')

                for target, replacement in zip(target_words, replacements):
                    line = line.replace(target, replacement)

                outfile.write(line)
        print(f'File {filenames} has been saved')