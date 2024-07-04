#if image genearation is not working ==> pip install kaleido==0.1.0.post1

import plotly.graph_objects as go
import plotly.io as pio
import os

def create_boxplot(data, title, y_axis, x_axis):
    import plotly.graph_objects as go
    import plotly.io as pio

    # Create boxplot
    fig = go.Figure()
    fig.add_trace(go.Box(y=data, boxpoints='all', jitter=0.3, pointpos=-1.8))
    
    
    # Add title and axis descriptions
    fig.update_layout(
        plot_bgcolor='white',
        title=title,
        xaxis=dict(title=x_axis),
        yaxis=dict(title=y_axis),
        showlegend=False
    )

    # Show grid
    fig.update_layout(
        yaxis=dict(showgrid=True, gridcolor='lightgray'),
        xaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    
    # Export as PNG
    
    pio.write_image(fig, f'{title.replace(" ", "_")}.png', width=800, height=600, scale=6)
    additional_path = r'C:\Users\matth\OneDrive\Master1\99_git_repos\ASIC-DESIGN-2\images'
    if os.path.exists(additional_path):
        # Export as PNG to the additional path
        pio.write_image(fig, os.path.join(additional_path, f'{title.replace(" ", "_")}.png'), width=800, height=600, scale=6)

# Data points
voltage_data = [1258, 1243, 1275, 1240, 1288, 1290, 1253, 1257, 1274, 1266, 1260]
voltage_data = [x / 1000 for x in voltage_data]
# Data points for Current Reference
current_data = [1418, 1470, 1434, 1444, 1488, 1458, 1416, 1483, 1412, 1431, 1435]
current_data = [x / 100 for x in current_data]

# Create boxplot for Current Reference
create_boxplot(current_data, 'Current Reference Distribution', 'Current (uA)', 'Current Reference')


create_boxplot(voltage_data, 'Bandgap Voltage Distribution', 'Voltage (V)', 'Bandgap')