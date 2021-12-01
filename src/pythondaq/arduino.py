from pythondaq.models.model import ArduinoModel as AM
from pythondaq.views.view import View

"""file/script used to test all the classes from the other modules with."""

p = AM()
data = p.sweep_waardes(print=False)
View.make_plot(data)
p.csv_maker(filename="vuur")
