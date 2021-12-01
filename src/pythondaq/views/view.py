import matplotlib.pyplot as plt

"""Module to process the model data from the module "model.py" 
Plots are made in the make_plot function in the class View"""


class View:
    """Class where one or more views are available"""

    def __init__(self) -> None:
        pass

    def make_plot(data):
        """Plots the voltage vs the current"""
        fig, ax = plt.subplots()
        voltagelist, currentlist = data
        ax.plot(voltagelist, currentlist)
        ax.set(xlabel="Voltage over LED (V)", ylabel="Current over LED (A)")
        plt.show()
