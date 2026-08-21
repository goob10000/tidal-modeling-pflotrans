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

dir1 = "A18"
tec_data1 = [read_tec_file(f"{dir1}/{dir1}-{x:03}.tec") for x in range(11)]
vel_tec_data1 = [read_tec_file(f"{dir1}/{dir1}-vel-{x:03}.tec") for x in range(11)]

dir2 = "A20"
tec_data2 = [read_tec_file(f"{dir2}/{dir2}-{x:03}.tec") for x in range(11)]
vel_tec_data2 = [read_tec_file(f"{dir2}/{dir2}-vel-{x:03}.tec") for x in range(11)]

x1:np.ndarray = tec_data1[0]["data"]["X [m]"]
z1:np.ndarray = tec_data1[0]["data"]["Z [m]"]

x2:np.ndarray = tec_data2[0]["data"]["X [m]"]
z2:np.ndarray = tec_data2[0]["data"]["Z [m]"]

xDim, yDim, zDim = tuple([(x-1) for x in tec_data1[0]["dimensions"]])
dims = (zDim, yDim, xDim)

for data1, data_vel1, data2, data_vel2 in zip([tec_data1[-1]], [vel_tec_data1[-1]], [tec_data2[-1]], [vel_tec_data2[-1]]):
# for data, data_vel in zip(tec_data, vel_tec_data):
    fig = plt.figure()
    temps1 = data1["data"]["Temperature [C]"].reshape(dims)
    pressures1 = data1["data"]['Liquid Pressure [Pa]'].reshape(dims)
    density1 = data1["data"]["Liquid Density [kg/m^3]"].reshape(dims)
    xV1 = data_vel1["data"]["qlx [m/yr]"].reshape((xDim, yDim, zDim))
    zV1 = data_vel1["data"]["qlz [m/yr]"].reshape((xDim, yDim, zDim))

    temps2 = data2["data"]["Temperature [C]"].reshape(dims)
    pressures2 = data2["data"]['Liquid Pressure [Pa]'].reshape(dims)
    density2 = data2["data"]["Liquid Density [kg/m^3]"].reshape(dims)
    xV2 = data_vel2["data"]["qlx [m/yr]"].reshape((xDim, yDim, zDim))
    zV2 = data_vel2["data"]["qlz [m/yr]"].reshape((xDim, yDim, zDim))

    ax1 = fig.add_subplot(221)
    fig.colorbar(ax1.pcolormesh(np.unique(x1), np.unique(z1), temps1[:, 0, :] - temps2[:, 0, :], shading='auto', cmap='hot'), ax=ax1, orientation='vertical', label='Temperature [C]')
    ax1.set_xlabel("X-axis [m]")
    ax1.set_ylabel("Z-axis [m]")
    ax1.set_title("Temperature [C]")

    ax2 = fig.add_subplot(222)
    fig.colorbar(ax2.pcolormesh(np.unique(x1), np.unique(z1), pressures1[:, 0, :] - pressures2[:, 0, :], shading='auto', cmap='coolwarm'), ax=ax2, orientation='vertical', label='Liquid Pressure [Pa]')
    ax2.set_xlabel("X-axis [m]")
    ax2.set_ylabel("Z-axis [m]")
    ax2.set_title("Liquid Pressure [Pa]")

    ax3 = fig.add_subplot(223)
    fig.colorbar(ax3.pcolormesh(np.unique(x1), np.unique(z1), density1[:, 0, :] - density2[:, 0, :], shading='auto', cmap='viridis'), ax=ax3, orientation='vertical', label='Liquid Density [kg/m^3]')
    ax3.set_xlabel("X-axis [m]")
    ax3.set_ylabel("Z-axis [m]")
    ax3.set_title("Liquid Density [kg/m^3]")

    quiverXP = x1.reshape(117, 2, 573)
    quiverX = (quiverXP[1:, 0, 1:] + quiverXP[:-1, 0, :-1])/2

    quiverZP = z1.reshape(117, 2, 573)
    quiverZ = (quiverZP[1:, 0, 1:] + quiverZP[:-1, 0, :-1])/2
    
    # # if not(xV.min() == 0 and zV.min() == 0):
    ax4 = fig.add_subplot(224)
    a = 29
    b = zDim//a
    c = 52
    d = xDim//c

    def squash(m):
        return (m[1:, 0, 1:] + m[:-1, 0, :-1])/2
    
    
    quiverXP = x1.reshape(117, 2, 573)
    quiverX = squash(quiverXP)
    X = quiverX.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    xV1 = data_vel1["data"]["qlx [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]
    xV2 = data_vel2["data"]["qlx [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]

    quiverZP = z1.reshape(117, 2, 573)
    quiverZ = squash(quiverZP)
    Z = quiverZ.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV1 = data_vel1["data"]["qlz [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]
    zV2 = data_vel2["data"]["qlz [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]

    xV_new1 = (xV1).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV_new1 = (zV1).reshape(a, b, c, d).mean(axis=3).mean(axis=1)

    xV_new2 = (xV2).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV_new2 = (zV2).reshape(a, b, c, d).mean(axis=3).mean(axis=1)

    # f = (quiverX >= 5000) & (quiverX <= 15000) & (quiverZ >= -1000)
    fs = (X >= 5000) & (X <= 15000) & (Z >= -1000)
    
    ax4.quiver(X[fs], Z[fs], xV_new1[fs] - xV_new2[fs], zV_new1[fs] - zV_new2[fs])
    ax4.set_xlabel("X-axis [m]")
    ax4.set_ylabel("Z-axis [m]")
    ax4.set_title("Velocity Field [m/yr]")
    # ax4.set_ylim(0, zDim)  # Set y-limits to match the data shape
    # ax4.set_yticks(np.linspace(0, zDim, num=5))  # Set y-ticks to match the data shape
    # ax4.set_yticklabels(np.linspace(z.min(), z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    # ax4.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    # ax4.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    # fig.suptitle("Simulation Data Visualization")
    plt.show()

for data1, data_vel1 in zip([tec_data1[-1]], [vel_tec_data1[-1]]):
# for data, data_vel in zip(tec_data, vel_tec_data):
    fig = plt.figure()
    xV1 = data_vel1["data"]["qlx [m/yr]"].reshape((xDim, yDim, zDim))
    zV1 = data_vel1["data"]["qlz [m/yr]"].reshape((xDim, yDim, zDim))

    quiverXP = x1.reshape(117, 2, 573)
    quiverX = (quiverXP[1:, 0, 1:] + quiverXP[:-1, 0, :-1])/2

    quiverZP = z1.reshape(117, 2, 573)
    quiverZ = (quiverZP[1:, 0, 1:] + quiverZP[:-1, 0, :-1])/2

    ax4 = fig.add_subplot(111)
    
    a = 29
    b = zDim//a
    c = 52
    d = xDim//c

    def squash(m):
        return (m[1:, 0, 1:] + m[:-1, 0, :-1])/2
    
    
    quiverXP = x1.reshape(117, 2, 573)
    quiverX = squash(quiverXP)
    X = quiverX.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    xV1 = data_vel1["data"]["qlx [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]

    quiverZP = z1.reshape(117, 2, 573)
    quiverZ = squash(quiverZP)
    Z = quiverZ.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV1 = data_vel1["data"]["qlz [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]

    xV_new1 = (xV1).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
    zV_new1 = (zV1).reshape(a, b, c, d).mean(axis=3).mean(axis=1)

    f = (quiverX >= 5000) & (quiverX <= 15000) & (quiverZ >= -1000)
    fs = (X >= 5000) & (X <= 15000) & (Z >= -1000)
    
    ax4.quiver(X[fs], Z[fs], xV_new1[fs], zV_new1[fs])
    ax4.set_xlabel("X-axis [m]")
    ax4.set_ylabel("Z-axis [m]")
    ax4.set_title("Velocity Field [m/yr]")
    # ax4.set_ylim(0, zDim)  # Set y-limits to match the data shape
    # ax4.set_yticks(np.linspace(0, zDim, num=5))  # Set y-ticks to match the data shape
    # ax4.set_yticklabels(np.linspace(z.min(), z.max(), num=5).astype(int))  # Set y-tick labels to match the data range
    # ax4.set_xticks(np.linspace(0, xDim, num=5))  # Set x-ticks to match the data shape
    # ax4.set_xticklabels(np.linspace(x.min(), x.max(), num=5).astype(int))  # Set x-tick labels to match the data range

    plt.show()


for data1, data_vel1 in zip([tec_data1[-1]], [vel_tec_data1[-1]]):
# for data, data_vel in zip(tec_data, vel_tec_data):
    fig = plt.figure()
    temps1 = data1["data"]["Temperature [C]"].reshape(dims)

    ax1 = fig.add_subplot(111)
    ax1.pcolormesh(np.unique(x1), np.unique(z1), temps1[:, 0, :], shading='auto', cmap='viridis')
    ax1.set_xlabel("X-axis [m]")
    ax1.set_ylabel("Z-axis [m]")
    ax1.set_title("Temperature [C]")
    # fig.colorbar(ax1.imshow(temps[:, 0, :], cmap='hot', interpolation='nearest'), ax=ax1, orientation='vertical', label='Temperature [C]')
    plt.show()

x1.shape

a = 29
b = zDim//a
c = 52
d = xDim//c

def squash(m):
    return (m[1:, 0, 1:] + m[:-1, 0, :-1])/2

quiverXP = x1.reshape(117, 2, 573)
quiverX = squash(quiverXP)
X = quiverX.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
xV1 = data_vel1["data"]["qlx [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]

quiverZP = z1.reshape(117, 2, 573)
quiverZ = squash(quiverZP)
Z = quiverZ.reshape(a, b, c, d).mean(axis=3).mean(axis=1)
zV1 = data_vel1["data"]["qlz [m/yr]"].reshape((zDim, yDim, xDim))[:, 0, :]

xV_new1 = (xV1).reshape(a, b, c, d).mean(axis=3).mean(axis=1)
zV_new1 = (zV1).reshape(a, b, c, d).mean(axis=3).mean(axis=1)

f = (quiverX >= 5000) & (quiverX <= 15000) & (quiverZ >= -1000)
fs = (X >= 5000) & (X <= 15000) & (Z >= -1000)

plt.quiver(X[fs], Z[fs], xV_new1[fs], zV_new1[fs])
plt.quiver(quiverX[f], quiverZ[f], xV1[f], zV1[f])

# plt.scatter(quiverX, quiverZ, s=0.5)
# plt.scatter(quiverXP, quiverZP, s=0.5)
# plt.scatter(x, z, s=0.5)
plt.show()


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