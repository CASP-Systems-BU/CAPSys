

# Define the path to the file
file_path = 'schedulercfg'

# Read the lines from the file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Modify each line
modified_lines = ['"' + line.strip() + '",\n' for line in lines]

# Write the modified lines back to the file
with open(file_path, 'w') as file:
    file.writelines(modified_lines)
