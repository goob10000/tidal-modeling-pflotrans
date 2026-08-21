import numpy as np
import re
import matplotlib.pyplot as plt

def read_tec_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Parse header
    variables = []
    I = J = K = None
    cell_centered_vars = []
    
    for line in lines:
        if 'VARIABLES' in line:
            variables = re.findall(r'"([^"]*)"', line)
        if 'ZONE' in line:
            I = int(re.search(r'I=(\d+)', line).group(1)) #type: ignore 
            J = int(re.search(r'J=(\d+)', line).group(1)) #type: ignore
            K = int(re.search(r'K=(\d+)', line).group(1)) #type: ignore
            
            varloc = re.search(r'VARLOCATION=\(\[([^\]]+)\]=CELLCENTERED\)', line)
            if varloc:
                var_range = varloc.group(1)
                start, end = map(int, var_range.split('-'))
                cell_centered_vars = list(range(start - 1, end))
    
    # Find data start
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('ZONE'):
            data_start = i + 1
            break
    
    # Extract numeric lines
    numeric_lines = []
    for i, line in enumerate(lines[data_start:], start=data_start):
        stripped = line.strip()
        if stripped and (stripped[0].isdigit() or stripped[0] in ['-', '+']):
            numeric_lines.append(line)
        elif stripped and not (stripped[0].isdigit() or stripped[0] in ['-', '+']):
            print(f"Skipping line {i}: {repr(line[:50])}")
    
    # print(f"Total numeric lines: {len(numeric_lines)}")
    # print(f"First few numeric lines:")
    # for i in range(min(3, len(numeric_lines))):
        # print(f"  Line {i}: {numeric_lines[i][:80]}")
    
    # Parse as flat 1D array instead
    all_values = []
    for line in numeric_lines:
        values = line.strip().split()
        all_values.extend([float(v) for v in values])
    
    flat_data = np.array(all_values)
    # print(f"Total values parsed: {len(flat_data)}")
    
    # Calculate expected sizes
    num_node_centered = I * J * K #type: ignore
    num_cell_centered = (I - 1) * (J - 1) * (K - 1) #type: ignore
    # print(f"Expected node-centered points: {num_node_centered}")
    # print(f"Expected cell-centered points: {num_cell_centered}")
    
    # Split into blocks
    data_dict = {}
    idx = 0
    
    for var_i, var_name in enumerate(variables):
        if var_i in cell_centered_vars:
            size = num_cell_centered
        else:
            size = num_node_centered
        
        # print(f"Variable {var_i} ({var_name}): indices {idx} to {idx + size}")
        data_dict[var_name] = flat_data[idx:idx + size]
        idx += size
    
    return {'variables': variables, 'dimensions': (I, J, K), 'data': data_dict}

# Run it
dir = "A15"
tec_data = [read_tec_file(f"{dir}/{dir}-{x:03}.tec") for x in range(11)]
vel_tec_data = [read_tec_file(f"{dir}/{dir}-vel-{x:03}.tec") for x in range(11)]

x = tec_data[0]["data"]["X [m]"]
z = tec_data[0]["data"]["Z [m]"]

xDim, yDim, zDim = tuple([(x-1) for x in tec_data[0]["dimensions"]])
dims = (zDim, yDim, xDim)

for data, data_vel in zip([tec_data[-1]], [vel_tec_data[-1]]):
# for data, data_vel in zip(tec_data, vel_tec_data):
    fig = plt.figure()
    temps = data["data"]["Temperature [C]"].reshape(dims)
    pressures = data["data"]['Liquid Pressure [Pa]'].reshape(dims)
    density = data["data"]["Liquid Density [kg/m^3]"].reshape(dims)
    xV = data_vel["data"]["qlx [m/yr]"].reshape((xDim, yDim, zDim))
    zV = data_vel["data"]["qlz [m/yr]"].reshape((xDim, yDim, zDim))

    ax1 = fig.add_subplot(221)
    ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest')
    ax1.set_xlabel("X-axis [m]")
    ax1.set_ylabel("Z-axis [m]")
    ax1.set_title("Temperature [C]")
    ax1.set_ylim(0, zDim)  # Set y-limits to match the data shape
    ax1.set_yticks(np.linspace(0, zDim, num=5))  # Set y-ticks to match the data shape
    ax1.set_yticklabels(np.linspace(z.min(), z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    ax1.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    ax1.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    ax2 = fig.add_subplot(222)
    ax2.imshow(pressures[:, 0, :], cmap='coolwarm', interpolation='nearest')
    ax2.set_xlabel("X-axis [m]")
    ax2.set_ylabel("Z-axis [m]")
    ax2.set_title("Liquid Pressure [Pa]")
    ax2.set_ylim(0, zDim)  # Set y-limits to match the data shape
    ax2.set_yticks(np.linspace(0, zDim, num=5))  # Set y-ticks to match the data shape
    ax2.set_yticklabels(np.linspace(z.min(), z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    ax2.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    ax2.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    ax3 = fig.add_subplot(223)
    ax3.imshow(density[:, 0, :], cmap='viridis', interpolation='nearest')
    ax3.set_xlabel("X-axis [m]")
    ax3.set_ylabel("Z-axis [m]")
    ax3.set_title("Liquid Density [kg/m^3]")
    ax3.set_ylim(0, zDim)  # Set y-limits to match the data shape
    ax3.set_yticks(np.linspace(0, zDim, num=5))  # Set y-ticks to match the data shape
    ax3.set_yticklabels(np.linspace(z.min(), z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    ax3.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    ax3.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    # if not(xV.min() == 0 and zV.min() == 0):
    X, Z = np.meshgrid(np.arange(xV.shape[0]), np.arange(xV.shape[2]))
    ax4 = fig.add_subplot(224)
    a = 29
    b = zDim//a
    c = 31
    d = xDim//c
    X_new = X.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    Z_new = Z.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    xV_new = (xV[:, 0, :] + 1e-15).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV_new = (zV[:, 0, :] + 1e-15).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    ax4.quiver(X_new, Z_new, xV_new, zV_new)
    ax4.set_xlabel("X-axis [m]")
    ax4.set_ylabel("Z-axis [m]")
    ax4.set_title("Velocity Field [m/yr]")
    ax4.set_ylim(0, zDim)  # Set y-limits to match the data shape
    ax4.set_yticks(np.linspace(0, zDim, num=5))  # Set y-ticks to match the data shape
    ax4.set_yticklabels(np.linspace(z.min(), z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    ax4.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    ax4.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    fig.colorbar(ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest'), ax=ax1, orientation='vertical', label='Temperature [C]')
    fig.colorbar(ax2.imshow(pressures[:, 0, :], cmap='coolwarm', interpolation='nearest'), ax=ax2, orientation='vertical', label='Liquid Pressure [Pa]')
    fig.colorbar(ax3.imshow(density[:, 0, :], cmap='viridis', interpolation='nearest'), ax=ax3, orientation='vertical', label='Liquid Density [kg/m^3]')
    # fig.suptitle("Simulation Data Visualization")
    plt.show()

dims

for data, data_vel in zip([tec_data[-1]], [vel_tec_data[-1]]):
# for data, data_vel in zip(tec_data, vel_tec_data):
    fig = plt.figure()
    xV = data_vel["data"]["qlx [m/yr]"].reshape((xDim, yDim, zDim))
    zV = data_vel["data"]["qlz [m/yr]"].reshape((xDim, yDim, zDim))

    # if not(xV.min() == 0 and zV.min() == 0):
    X, Z = np.meshgrid(np.arange(xV.shape[0]), np.arange(xV.shape[2]))
    ax4 = fig.add_subplot(111)
    a = 100
    b = zDim//a
    c = 25
    d = xDim//c
    X_new = X.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    Z_new = Z.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    xV_new = (xV[:, 0, :] + 1e-15).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV_new = (zV[:, 0, :] + 1e-15).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    ax4.quiver(X_new, Z_new, xV_new, zV_new)
    ax4.set_xlabel("X-axis [m]")
    ax4.set_ylabel("Z-axis [m]")
    ax4.set_title("Velocity Field [m/yr]")
    ax4.set_ylim(zDim-zDim/5, zDim)  # Set y-limits to match the data shape
    ax4.set_yticks(np.linspace(zDim-zDim/5, zDim, num=6))  # Set y-ticks to match the data shape
    ax4.set_yticklabels(np.linspace(zDim-zDim/5, z.max(), num=6).astype(int))  # Set y-tick labels to match the data range
    ax4.set_xticks(np.linspace(0, xDim, num=6))  # Set x-ticks to match the data shape
    ax4.set_xticklabels(np.linspace(x.min(), x.max(), num=6).astype(int))  # Set x-tick labels to match the data range

    # fig.colorbar(ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest'), ax=ax1, orientation='vertical', label='Temperature [C]')
    # fig.colorbar(ax2.imshow(pressures[:, 0, :], cmap='coolwarm', interpolation='nearest'), ax=ax2, orientation='vertical', label='Liquid Pressure [Pa]')
    # fig.colorbar(ax3.imshow(density[:, 0, :], cmap='viridis', interpolation='nearest'), ax=ax3, orientation='vertical', label='Liquid Density [kg/m^3]')
    # fig.suptitle("Simulation Data Visualization")
    plt.show()


for data, data_vel in zip([tec_data[-1]], [vel_tec_data[-1]]):
# for data, data_vel in zip(tec_data, vel_tec_data):
    fig = plt.figure()
    temps = data["data"]["Temperature [C]"].reshape(dims)

    ax1 = fig.add_subplot(111)
    ax1.pcolormesh(x, z, temps[:, 0, :], shading='auto', cmap='viridis')
    ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest')
    ax1.set_xlabel("X-axis [m]")
    ax1.set_ylabel("Z-axis [m]")
    ax1.set_title("Temperature [C]")
    ax1.set_ylim(zDim*9/10, zDim)  # Set y-limits to match the data shape
    ax1.set_yticks(np.linspace(zDim*9/10, zDim, num=5))  # Set y-ticks to match the data shape
    ax1.set_yticklabels(np.linspace(z.min()/10, z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    ax1.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    ax1.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    # fig.colorbar(ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest'), ax=ax1, orientation='vertical', label='Temperature [C]')
    plt.show()

zDim/5
z.min(), z.max()/5
4*zDim/5
zDim
# fig = plt.figure()
# temps = data["data"]["Temperature [C]"].reshape(tuple([(x-1) for x in data["dimensions"]]))
# pressures = data["data"]['Liquid Pressure [Pa]'].reshape(tuple([(x-1) for x in data["dimensions"]]))
# density = data["data"]["Liquid Density [kg/m^3]"].reshape(tuple([(x-1) for x in data["dimensions"]]))
# xV = data_vel["data"]["qlx [m/yr]"].reshape(tuple([(x-1) for x in data["dimensions"]]))
# zV = data_vel["data"]["qlz [m/yr]"].reshape(tuple([(x-1) for x in data["dimensions"]]))

# ax1 = fig.add_subplot(221)
# ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest')
# ax1.set_xlabel("X-axis [m]")
# ax1.set_ylabel("Z-axis [m]")
# ax1.set_title("Temperature [C]")

# ax2 = fig.add_subplot(222)
# ax2.imshow(pressures[:, 0, :], cmap='coolwarm', interpolation='nearest')
# ax2.set_xlabel("X-axis [m]")
# ax2.set_ylabel("Z-axis [m]")
# ax2.set_title("Liquid Pressure [Pa]")

# ax3 = fig.add_subplot(223)
# ax3.imshow(density[:, 0, :], cmap='viridis', interpolation='nearest')
# ax3.set_xlabel("X-axis [m]")
# ax3.set_ylabel("Z-axis [m]")
# ax3.set_title("Liquid Density [kg/m^3]")

# if not(xV.min() == 0 and zV.min() == 0):
#     X, Z = np.meshgrid(np.arange(xV.shape[0]), np.arange(xV.shape[2]))
#     ax4 = fig.add_subplot(224)
#     ax4.quiver(X, Z, xV[:, 0, :], zV[:, 0, :], scale=1e6)
#     ax4.set_xlabel("X-axis [m]")
#     ax4.set_ylabel("Z-axis [m]")
#     ax4.set_title("Velocity Field [m/yr]")

# fig.colorbar(ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest'), ax=ax1, orientation='vertical', label='Temperature [C]')
# fig.colorbar(ax2.imshow(pressures[:, 0, :], cmap='coolwarm', interpolation='nearest'), ax=ax2, orientation='vertical', label='Liquid Pressure [Pa]')
# fig.colorbar(ax3.imshow(density[:, 0, :], cmap='viridis', interpolation='nearest'), ax=ax3, orientation='vertical', label='Liquid Density [kg/m^3]')
# # fig.suptitle()
# plt.show()