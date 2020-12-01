import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import seaborn as sns

from utility.colors import color_wheel
from utility.config import paths
import utility.globals as glob

sns.set()


def plot_ty(name, yaxis_name):
    mask = glob.df['name'] == name
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(glob.df[mask]['datetime'], glob.df[mask][yaxis_name], color=color_wheel[1], lw=2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlabel('Time (hs)')
    ax.set_ylabel(yaxis_name)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(paths['last_export'], f'{name}_time_vs_{yaxis_name}.png'))
    plt.clf()
