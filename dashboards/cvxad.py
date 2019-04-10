from functools import reduce

from bokeh.models.widgets import Panel, Tabs
from bokeh.plotting import curdoc
from cvxad.adschedule import AdSchedule


schedule = AdSchedule()
f1 = schedule()
t1 = Panel(child=f1, title = "Advertising Optimization")

f2 = schedule.probabilityMap()
t2 = Panel(child=f2, title = "Click Through Probabilities")

t3 = Panel(child=schedule.trafficData(), title = "Traffic Data")

tabs = Tabs(tabs=[t1, t2, t3])

curdoc().add_root(tabs)
curdoc().title = "Advertising Optimization"
