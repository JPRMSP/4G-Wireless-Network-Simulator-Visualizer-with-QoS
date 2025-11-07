import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon

# Streamlit Page Config
st.set_page_config(page_title="4G Network Simulator", layout="wide")
st.title("4G Wireless Network Simulator & Visualizer with QoS")

# Parameters
num_cells = st.slider("Number of Cells", 3, 7, 4)
num_users = st.slider("Number of Mobile Users", 5, 50, 15)
user_speed = st.slider("User Speed (units/sec)", 0.1, 2.0, 0.5)
sim_steps = st.slider("Simulation Steps", 5, 50, 10)
bs_capacity = st.slider("Base Station Capacity (Mbps)", 10, 200, 50)

# Generate Hexagonal Grid for Cells
def generate_hex_grid(num_cells):
    centers = []
    spacing = 10
    for i in range(num_cells):
        for j in range(num_cells):
            x = spacing * (i + 0.5 * (j % 2))
            y = spacing * np.sqrt(3)/2 * j
            centers.append((x, y))
    return centers

cell_centers = generate_hex_grid(num_cells)

# Initialize Users
users = np.random.rand(num_users, 2) * (num_cells * 10)

# Simulation Function
def simulate_network(users, cell_centers, steps, speed, bs_capacity):
    history = []
    for step in range(steps):
        # Move users randomly
        users += (np.random.rand(users.shape[0], 2) - 0.5) * speed
        users = np.clip(users, 0, num_cells*10)
        
        # Assign each user to nearest BS
        user_bs = []
        for user in users:
            dists = [np.linalg.norm(user - np.array(center)) for center in cell_centers]
            user_bs.append(np.argmin(dists))
        
        # Bandwidth Demand (random 1-10 Mbps per user)
        demand = np.random.randint(1, 11, size=num_users)
        
        # Allocate bandwidth per BS
        allocated_bw = np.zeros(num_users)
        for bs_idx in range(len(cell_centers)):
            bs_users = [i for i, b in enumerate(user_bs) if b == bs_idx]
            if bs_users:
                total_demand = demand[bs_users].sum()
                if total_demand <= bs_capacity:
                    allocated_bw[bs_users] = demand[bs_users]
                else:
                    # Proportional allocation
                    allocated_bw[bs_users] = demand[bs_users] / total_demand * bs_capacity
        
        history.append((users.copy(), user_bs.copy(), demand.copy(), allocated_bw.copy()))
    return history

history = simulate_network(users, cell_centers, sim_steps, user_speed, bs_capacity)

# Visualization
st.subheader("Network Simulation with QoS")
for step, (users_pos, user_bs, demand, allocated_bw) in enumerate(history):
    st.write(f"Step {step+1}")
    fig, axs = plt.subplots(1,2, figsize=(14,6))
    
    # Left: Cellular Layout
    ax = axs[0]
    for idx, center in enumerate(cell_centers):
        hex = RegularPolygon(center, numVertices=6, radius=5, edgecolor='k', facecolor='lightblue', alpha=0.3)
        ax.add_patch(hex)
        ax.text(center[0], center[1], f"BS{idx}", ha='center', va='center', fontsize=8, color='blue')
    
    for i, pos in enumerate(users_pos):
        color = 'green' if allocated_bw[i] >= demand[i] else 'red'
        ax.plot(pos[0], pos[1], 'o', color=color)
        ax.text(pos[0]+0.3, pos[1]+0.3, f"U{i}", fontsize=6)
        bs = cell_centers[user_bs[i]]
        ax.plot([pos[0], bs[0]], [pos[1], bs[1]], 'g--', linewidth=0.5)
    
    ax.set_xlim(-2, num_cells*10 +2)
    ax.set_ylim(-2, num_cells*10 +2)
    ax.set_aspect('equal')
    ax.set_title("Cellular Layout with Users (Green=QoS Met, Red=Violated)")

    # Right: Bandwidth Allocation
    ax2 = axs[1]
    ax2.bar(range(num_users), allocated_bw, color=['green' if allocated_bw[i]>=demand[i] else 'red' for i in range(num_users)])
    ax2.plot(range(num_users), demand, 'b--', label="Demand")
    ax2.set_xlabel("User ID")
    ax2.set_ylabel("Bandwidth (Mbps)")
    ax2.set_title("Bandwidth Allocation vs User Demand")
    ax2.legend()
    
    st.pyplot(fig)
