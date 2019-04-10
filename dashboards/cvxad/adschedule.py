"""
AdSchedule 

This class holds information about a series of 
click through ads and performs a convex optimization to 
determine the most profitable schedule.
"""
import cvxpy as cp
import numpy as np
import pandas as pd

from bokeh.plotting import curdoc
from bokeh.models.widgets import Slider
from bokeh.layouts import row, widgetbox

import holoviews as hv
from holoviews import dim, opts
#hv.extension('bokeh')

from bokeh.models.widgets import Slider

from functools import reduce
renderer = hv.renderer('bokeh')

class Ad:
    """Holds information about an ad contract and returns a 
    user interface for changing values..
    
        Attributes:
            _min_lo : low end of range for contractual minimum ad shows 
            _min_hi : high end of range for contractual minimum ad shows
            _min_step : step for UI of contractual minimum ad shows

            _max_lo : low end of range for contractual maximum $
            _max_hi : high end of range for contractual maximum $
            _max_step : step for UI of contractual maximum $
    """
    _min_lo = 0
    _min_hi = 100
    _min_step = 10
    
    _max_lo = 1000
    _max_hi = 10000
    _max_step = 1000

    _clk_lo = 1
    _clk_hi = 10
    _clk_step = 1
    
    def __init__(self, i, update, update_constraints, cmin, cmax, cpc, contractMin = 10, contractMax = 5000, costPerClick = 5):
        """
        
        """
        self.i = i
        self.f = update
        self.fc = update_constraints
        self.cmin = cmin
        self.cmax = cmax
        self.cpc = cpc
        
        self.cmin.value[i] = contractMin
        self.cmax.value[i] = contractMax
        self.cpc.value[i] = costPerClick

        self.widget = [Slider(start=self._min_lo,
                              end=self._min_hi,
                              value=self.cmin.value[i],
                              step=self._min_step,
                              title=f"{i}--min ads"),
                       Slider(start=self._max_lo,
                              end=self._max_hi,
                              value=self.cmax.value[i],
                              step=self._max_step,
                              title="$ max"),
                       Slider(start=self._clk_lo,
                              end=self._clk_hi,
                              value=self.cpc.value[i],
                              step=self._clk_step,
                              title="$/click"),
                       ]
                       
        self.widget[0].on_change('value', self.update_constraints)
        self.widget[1].on_change('value', self.update_constraints)
        self.widget[2].on_change('value', self.update)

    def update(self,attr, old, new):
        print(self.widget[0].value)
        print(self.widget[1].value)
        print(self.widget[2].value)
        self.cpc.value[self.i] = self.widget[2].value
        self.f(attr, old, new)
        
    def update_constraints(self,attr, old, new):
        print(self.widget[0].value)
        print(self.widget[1].value)
        print(self.widget[2].value)
        self.cmin.value[self.i] = self.widget[0].value
        self.cmax.value[self.i] = self.widget[1].value
        self.fc(attr, old, new)
        
    def getConfig(self):
        return (self.cmin, self.cmax, self.cpc)
        

class AdSchedule:
    """Class for determining the optimal schedule for advertisements."""

    #class AdParameters:
    #    def __init__(self):
            
    
    def __init__(self):
        """Currently this class is for demonstration purposes only.
        
        Consequently, the blank initialization is it for now.
        """
        self.nads = 5
        self.periods = 24

        self.cmin = cp.Parameter(self.nads,value=10*np.ones(self.nads),nonneg=True)
        self.cmax = cp.Parameter(self.nads,value=1000*np.ones(self.nads),nonneg=True)
        self.cpc = cp.Parameter(self.nads,value=5*np.ones(self.nads),nonneg=True)

        self.seed = 123456
        np.random.seed(self.seed)

        self.ads = list(map(lambda i : Ad(i, self.update, self.update_constraints, self.cmin, self.cmax, self.cpc), range(self.nads)))

        self._clickProbabilities = self._generateRandomClickProbabilities()
        self._trafficData = self._generateTrafficData()
        
        self.schedule = cp.Variable((self.nads,self.periods), nonneg=True)
        self.expectation = cp.multiply(self._clickProbabilities,self.schedule)

        self.prob = cp.Problem(self.objective(), self.constraints())

        self.width = 800
        self.panel_width = 350
        
    def __call__(self):
        controls0 = widgetbox([ad.widget[0] for ad in self.ads], width=125)
        controls1 = widgetbox([ad.widget[1] for ad in self.ads], width=125)
        controls2 = widgetbox([ad.widget[2] for ad in self.ads], width=100)
        self.layout = row(controls0,controls1,controls2, self.create_figure()) 
        return self.layout
    
    def objective(self):
        return cp.Maximize(cp.sum(self.cpc*cp.sum(self.expectation, axis=1)))

    def constraints(self): 
        return [self.schedule.T * np.ones((self.nads,)) <= self._trafficData,
                self.schedule * np.ones((self.periods,))  >= self.cmin,
                cp.multiply(self.schedule * np.ones((self.periods,)), self.cpc)  <= self.cmax,
        ]

    
    
    def create_figure(self):
        data = self.solve()
        heatmap = hv.HeatMap(data,
                             label='Optimal Ads Served',
                             kdims=['hour','Advertisement id'],
                             vdims=['count'])
        heatmap.opts(tools=['hover'],
                     colorbar=True,
                     toolbar=None,
                     invert_yaxis=True,
                     width=self.width-self.panel_width,
        )
        return renderer.get_plot(heatmap).state

    def solve(self):
        self.prob.solve()
        print("status:", self.prob.status)
        print("optimal value", self.prob.value)
        
        return [(j, i, round(d)) for i, l in enumerate(self.schedule.value) for j, d in enumerate(l)]
    
    def update(self,attr, old, new):
        self.layout.children[3] = self.create_figure()

    def update_constraints(self,attr, old, new):
        print(self.schedule.value)
        print((self.schedule * np.ones((self.periods,))).value)
        print(self.cmin.value)
        #self.prob = cp.Problem(self.prob.objective, self.constraints())
        self.layout.children[3] = self.create_figure()
        
    def _generateRandomClickProbabilities(self):
        r = np.random.random((self.nads,self.periods)) / 10.

        for i in range(self.nads):
            r[i]+= .05*np.sin(2*np.pi*np.arange(self.periods) / self.periods - np.pi/2 + i) + 0.05

        return r

    def _generateTrafficData(self):
        return (np.random.randint(200,400,self.periods)
                + 200*np.sin(2*np.pi*np.arange(self.periods) / self.periods - np.pi/2))

    #@property
    def probabilityMap(self):
        periods = range(self.periods)
        l = [hv.Curve((periods, self._clickProbabilities[i,:]),
                      group='Probability',
                      label=str(i),
                      kdims=['hr'],
                      vdims=['prob.'],
        )
             for i in range(self.nads)]
        overlay = reduce(lambda x, y: x*y, l)
        overlay.opts(tools=['hover'],
                     toolbar=None,
                     width=self.width,
        )
        return renderer.get_plot(overlay).state
        
    #@property
    def trafficData(self):
        curve = hv.Curve((range(self.periods),
                          self._trafficData),
                         kdims=['hr'],
                         vdims=['visitors'],
        )
        curve.opts(tools=['hover'],
                   toolbar=None,
                   width=self.width,
        )
        return renderer.get_plot(curve).state
                        
    
if __name__=="__main__":
    ads = AdSchedule()
    print(ads.ads)

    
