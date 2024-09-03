import matplotlib.pyplot as plt

def read_file(filename):
    res = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.endswith('µs'):
                # Extract the number and convert it from microseconds to milliseconds
                number_str = line[:-2]  # Remove 'us'
                number = float(number_str) / 1000
            elif line.endswith('ms'):
                # Extract the number and convert it from milliseconds
                number_str = line[:-2]  # Remove 'ms'
                number = float(number_str)
            else:
                # Handle unexpected line formats
                print(f"Unexpected line format: {line}")
                continue
            # Print the result (or you can store it in a list or process it further)
            res.append(number)
    return res

def read_file_autotune(filename):
    numtasks2 = []
    runtimes2 = []
    with open(filename, 'r') as file:
        for line in file:
            # Split the line by the comma
            parts = line.strip().split(', ')

            # Convert the first part to an int and the second to a float
            int_value = int(parts[0].strip())
            float_value = float(parts[1].strip())

            # Append the values to the respective lists
            numtasks2.append(int_value)
            runtimes2.append(float_value)
    return numtasks2, runtimes2

# Data for CAPS-only
numtask1 = ['16', '32', '64', '128', '192', '256', ]
# α(0.08, 0.15, 0.6)
runtime1_1 = read_file("../eval_only_caps/result_threshold_0")
# α(0.15, 0.25, 0.8)
runtime1_2 = read_file("../eval_only_caps/result_threshold_1")
# α(0.25, 0.3, 0.9)
runtime1_3 = read_file("../eval_only_caps/result_threshold_2")

# Data for auto-tuning
numtasks2, runtimes2 = read_file_autotune("../eval_autotune/result")

# Colors for the figure
c1 = (255, 208, 111)
c2 = (255, 230, 183)
c3 = (170, 220, 224)
c4 = (82, 143, 173)
c5 = (231, 98, 84)
c_light = (255, 230, 183)
c1 = tuple([x/255.0 for x in c1])
c2 = tuple([x/255.0 for x in c2])
c3 = tuple([x/255.0 for x in c3])
c4 = tuple([x/255.0 for x in c4])
c5 = tuple([x/255.0 for x in c4])
c_light = tuple([x/255.0 for x in c_light])

# Plot the figure
fig, ax = plt.subplots(1, 2, figsize=(5.5, 2))

ax[0].plot(numtask1, runtime1_1, zorder=1, color='goldenrod')
ax[0].scatter(numtask1, runtime1_1, s=45, facecolors='black', marker='x', label='α(0.08, 0.15, 0.6)', zorder=2)
ax[0].plot(numtask1, runtime1_2, zorder=1, color='goldenrod')
ax[0].scatter(numtask1, runtime1_2, s=45, facecolors='none', edgecolors='black', marker='^', label='α(0.15, 0.25, 0.8)', zorder=2)
ax[0].plot(numtask1, runtime1_3, zorder=1, color='goldenrod')
ax[0].scatter(numtask1, runtime1_3, s=40, facecolors='none', edgecolors='black', marker='o', label='α(0.25, 0.3, 0.9)', zorder=2)
ax[0].set_ylabel("Runtime (ms)", fontsize=12)
ax[0].set_xlabel("Number of tasks", fontsize=12)
ax[0].set_title("(a) CAPSys runtime", fontsize=12)
ax[0].legend(loc='upper left', fontsize=8)

ax[1].scatter(numtasks2, runtimes2, marker='.')
ax[1].set_ylabel("Runtime (s)", fontsize=12)
ax[1].set_xlabel("Number of tasks", fontsize=12)
ax[1].set_title("(b) Auto-tuning runtime", fontsize=12)
ax[1].set_xscale('log')

plt.tight_layout()
plt.subplots_adjust(top=0.86, bottom=0.25, left=0.1, right = 0.97)

# plt.show()
plt.savefig('6-4.png', dpi=300)
plt.close()