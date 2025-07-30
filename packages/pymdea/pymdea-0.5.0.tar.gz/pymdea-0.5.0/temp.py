import matplotlib.pyplot as plt

from pymdea.core import DeaEngine, DeaLoader
from pymdea.plot import DeaPlotter

plt.style.use("clean-light")

dea_loader = DeaLoader()
dea_loader.make_sample_data(10**6)

dea_engine = DeaEngine(dea_loader, theta=0.55, window_stop=0.5, windows=100)
dea_engine.analyze_with_stripes(fit_start=0.1, fit_stop=0.9, stripes=60)

dea_plot = DeaPlotter(dea_engine)
dea_plot.s_vs_l()
plt.show()
