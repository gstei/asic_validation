import plotly.graph_objects as go
import os
import plotly.io as pio

# Input data
# chip name, input voltage, output voltage, input current, output current
data = [
    ("OUR_CHIP", "5V", "5V", "252mA", "200mA"),
    ("OUR_CHIP", "5V", "5V", "123mA", "100mA"),
    ("OUR_CHIP", "4.3V", "5V", "147mA", "100mA"),
    ("OUR_CHIP", "4.3V", "5V", "295mA", "200mA")
]

# Convert string data to float and calculate efficiency
converted_data = []
for datum in data:
    chip_name, input_voltage, output_voltage, input_current, output_current = datum
    input_voltage = float(input_voltage[:-1])
    output_voltage = float(output_voltage[:-1])
    input_current = float(input_current[:-2])
    output_current = float(output_current[:-2])
    efficiency = (output_voltage * output_current) / (input_voltage * input_current)
    converted_data.append((output_current, efficiency, chip_name, input_voltage))

# Separate output current, efficiency and chip name into separate lists for plotting
output_current, efficiency, chip_name, input_voltage= zip(*converted_data)

# Create scatter plot
fig = go.Figure()

# Add scatter plot for each data point
for i in range(len(output_current)):
    fig.add_trace(go.Scatter(x=[output_current[i]], y=[efficiency[i]], mode='markers', 
                             marker=dict(size=15, color=efficiency[i], colorscale='Viridis', showscale=False),
                             name=f'Chip Name: {chip_name[i]}, Output Current: {output_current[i]}mA, Input Voltage: {input_voltage[i]}V'))

# Show grid
fig.update_layout(
    yaxis=dict(showgrid=True, gridcolor='lightgray'),
    xaxis=dict(showgrid=True, gridcolor='lightgray'),
    plot_bgcolor='white',
    legend=dict(x=0, y=1, xanchor='auto', yanchor='top')  # Set legend position to top left
)
fig.update_layout(title='Efficiency vs Output Current', xaxis_title='Output Current (mA)', yaxis_title='Efficiency')

# Display plot
fig.show()

additional_path = r'C:\\Users\\matth\\OneDrive\\Master1\\99_git_repos\\ASIC-DESIGN-2\\images'
if os.path.exists(additional_path):
    # Export as PNG to the additional path
    title='Efficiency vs Output Current'
    pio.write_image(fig, os.path.join(additional_path, f'{title.replace(" ", "_")}.png'), width=800, height=600, scale=6)
