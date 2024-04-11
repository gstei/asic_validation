"""
This module contains the PlotData class for plotting data using Matplotlib.
"""
import os
import matplotlib.pyplot as plt




class PlotData:
    """
    A class for plotting data using Matplotlib.

    Attributes:
        x (list): The x-coordinate data.
        y (list): The y-coordinate data.
        x2 (list): The x-coordinate data for the second set of data.
        y2 (list): The y-coordinate data for the second set of data.
        label (list): The labels for the data.
        label2 (list): The labels for the second set of data.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        y2_label (str): The label for the secondary y-axis.
        title (str): The title of the plot.

    Methods:
        __init__(self, x_label="Time [s]", y_label="Volt [V]", title="Voltage vs Time",
                y2_label="Current [A]"):
            Initialize the PlotData object.

        add_data(self, x_data, y_data, label):
            Add data to the plot.

        add_data2(self, x_data, y_data, label):
            Add data to the second set of x and y values.

        plot_all_data(self):
            Plots all the data in the object.
    """

    def __init__(self, x_label="Time [s]", y_label="Volt [V]", title="Voltage vs Time",
                 y2_label="Current [A]"):
        """
        Initialize the PlotData object.

        Args:
            x_label (str): The label for the x-axis. Defaults to "Time [s]".
            y_label (str): The label for the y-axis. Defaults to "Volt [V]".
            title (str): The title of the plot. Defaults to "Voltage vs Time".
            y2_label (str): The label for the secondary y-axis. Defaults to "Current [A]".
        """
        self.x = []
        self.y = []
        self.x2 = []
        self.y2 = []
        self.label = []
        self.label2 = []
        self.x_label = x_label
        self.y_label = y_label
        self.y2_label = y2_label
        self.title = title

    def add_data(self, x_data, y_data, label):
        """
        Add data to the plot.

        Args:
            x_data (float): The x-coordinate data.
            y_data (float): The y-coordinate data.
            label (str): The label for the data.

        Returns:
            None
        """
        self.x.append(x_data)
        self.y.append(y_data)
        self.label.append(label)

    def add_data2(self, x_data, y_data, label):
        """
        Add data to the second set of x and y values. This is useful when you use
        plot_all_data afterwards since it will plot the data on a different axis.

        Args:
            x_data (float): The x value to add.
            y_data (float): The y value to add.
            label (str): The label for the data.

        Returns:
            None
        """
        self.x2.append(x_data)
        self.y2.append(y_data)
        self.label2.append(label)

    def plot_all_data(self, plot_type='png', y1_min=None, y1_max=None, x1_min=None, x1_max=None, y2_min=None, y2_max=None, x2_min=None, x2_max=None):
        """
        Plots all the data in the object when the values are larger than 0.05.

        If `y2` is empty, it plots the data in `y` against `x` using different colors and labels.
        If `y2` is not empty, it plots the data in `y` against `x` on the left y-axis and the data
        in `y2` against `x2` on the right y-axis.

        Args:
            None

        Returns:
            None
        """
        if len(self.y2) == 0:
            for i in range(len(self.y)):
                #plot only if max value of y is larger than 0.02
                if max(abs(self.y[i]))>0.02:
                    plt.plot(self.x[i], self.y[i], label=self.label[i])
            plt.xlabel(self.x_label)
            plt.ylabel(self.y_label)
            plt.title(self.title)
            plt.legend()
            plt.show()
        else:
            colors = ['red', 'green', 'blue', 'purple', 'orange', 'pink', 'yellow', 'brown']
            fig, ax1 = plt.subplots()
            color = 'tab:red'
            ax1.set_xlabel(self.x_label)
            ax1.set_ylabel(self.y_label, color=color)
            #set axis range
            if y1_min is not None and y1_max is not None and x1_min is not None and x1_max is not None:
                ax1.set_ylim([y1_min, y1_max])
                ax1.set_xlim([x1_min, x1_max])
            #only plot if data makes sense
            for i in range(len(self.y)):
                if max(abs(self.y[i]))>0.02:
                    ax1.plot(self.x[i], self.y[i], label=self.label[i], color=colors[i])
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.grid(True)
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            color = 'tab:blue'
            ax2.set_ylabel(self.y2_label, color=color)  # we already handled the x-label with ax1
            for i in range(len(self.y2)):
                if max(abs(self.y2[i]))>0.001:
                    ax2.plot(self.x2[i], self.y2[i], label=self.label2[i],
                             color=colors[i+len(self.y)])
            ax2.tick_params(axis='y', labelcolor=color)
            ax2.grid(True)
            #set axis range
            if y2_min is not None and y2_max is not None and x2_min is not None and x2_max is not None:
                ax2.set_ylim([y2_min, y2_max])
                ax2.set_xlim([x2_min, x2_max])
            plt.title(self.title)
            fig.legend()
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            fig.set_figheight(9*2/3)
            fig.set_figwidth(16*2/3)

            current_directory = os.getcwd()
            if plot_type == 'png':
                plt.savefig(f'{current_directory}\\images\\{self.title}.png', dpi=300)
            elif plot_type == 'pdf':  
                plt.savefig(f'{current_directory}\\images\\{self.title}.pdf', dpi=300)
            else:
                print("No such plot type")
                return()
            plt.close()
            # plt.show()
