'''
Contains all the major plot functions. 

Plots for population:
- UV_heatmap:       Used for 2D space (both N, M > 1), plot distribution of U, V in all patches within a specified time interval.
                    Average population over that interval is taken.
- UV_bar:           Used for 1D space (N or M == 1), counterpart of UV_heatmap.
                    Plot average distribution of U, V in a specified time interval in a barplot.
- UV_dyna:         Plot change of total U, V overtime.
- UV_hist:          Make a histogram of U, V in a specified time interval.
- UV_std:           Plot change of standard deviation of U, V over time.
- UV_expected_val:  Calculate expected U, V distribution based on matrices, assuming no migration return values (np.array)
- UV_expected:      Calculate expected distribution of U, V based on matrices, assuming no migration.


Plots for payoff:
- pi_heatmap:       Used for 2D space, plot distribution of Upi & Vpiwithin a specified time interval.
                    Average payoff over that interval is taken.
- pi_bar:           Used for 1D space, counterpart of pi_heatmap.
                    Plot average distribution of Upi & Vpiin a specified time interval in a bar plot.
- pi_dyna:         Plot change of total Upi, Vpiovertime.
- pi_hist:          Make a histogram of Upi, Vpiin a specified time interval.
- pi_std:           Plot change of standard deviation of Upi, Vpiover time.


Popu-payoff correlation:
- UV_pi:            Make two scatter plots: x-axes are U, V, y-axes are U's and V's payoff, in a specified time interval.
                    Reveals relationship between population and payoff.

'''


from .tools import figure_tools as figure_t
from . import simulation

import matplotlib.pyplot as plt
import numpy as np


# curve type in plot
# used by UV_dyna, UV_std, and pi_dyna
CURVE_TYPE = '-'



def UV_heatmap(mod, ax_U = None, ax_V = None, U_color = 'Purples', V_color = 'Greens', start = 0.95, end = 1.0, annot = False, fmt = '.3g'):
    '''
    Makes two heatmaps for U, V average distribution over a time interval, respectively. Works best for 2D space.
    1D works as well, but figures look bad.

    Inputs:
        mod:        A simulation.model object.
        ax_U, ax_V: matplotlib axes to plot on. New axes will be created if None is given.
        U_color:    Color for U's heatmap, uses matplotlib color maps.
        V_color:    Color for V's heatmap.
        start:      (0,1) float, where the interval should start from. Intended as a 'percentage'. 
                    For example, start = 0.8 means the interval should start from the 80% point of mod.maxtime.
        end:        (0,1) float, where the interval ends.
        annot:      bool, whether to add annotations (show exact numbers for every patch).
        fmt:        Number format for annotations. How many digits you want to keep. Please set annot = True first and then use fmt.

    Returns:
        ax_U, ax_V: matplotlib axes with heatmaps of U, V distribution plotted upon.
    '''
    
    start_index = int(start * mod.max_record)
    end_index = int(end * mod.max_record)
    
    # see ave_interval below
    U_ave = figure_t.ave_interval(mod.U, start_index, end_index)
    V_ave = figure_t.ave_interval(mod.V, start_index, end_index)
    
    #### plot ####
    
    U_title = figure_t.gen_title('Popu U', start, end)
    U_text = figure_t.gen_text(np.mean(U_ave), np.std(U_ave))
    V_title = figure_t.gen_title('Popu V', start, end)
    V_text = figure_t.gen_text(np.mean(V_ave), np.std(V_ave))

    ax_U = figure_t.heatmap(U_ave, ax_U, U_color, annot, fmt, U_title, U_text)
    ax_V = figure_t.heatmap(V_ave, ax_V, V_color, annot, fmt, V_title, V_text)
        
    return ax_U, ax_V
    


def UV_bar(mod, ax_U = None, ax_V = None, U_color = 'purple', V_color = 'green', start = 0.95, end = 1.0):
    '''
    Makes two barplots for U, V average distribution over a time interval. Works best for 1D space.
    2D works as well, but figures look bad.

    Inputs:
        mod:        A simulation.model object.
        ax_U, ax_V: matplotlib axes to plot on. New axes will be created if None is given.
        U_color:    Color of U's barplot. Uses Matplotlib colors.
                    See available colors at: https://matplotlib.org/stable/gallery/color/named_colors.html
        V_color:    Color of V's barplot. Uses Matplotlib colors.
        start:      (0,1) float. How much proportion of mod.maxtime you want the interval to start from.
        end:        (0,1) float. Where you want the interval to end.

    Returns:
        ax_U, ax_V: matplotlib axes with bar plots for U and V plotted upon.
    '''
    
    start_index = int(start * mod.max_record)
    end_index = int(end * mod.max_record)
    
    U_ave = figure_t.ave_interval_1D(mod.U, start_index, end_index)
    V_ave = figure_t.ave_interval_1D(mod.V, start_index, end_index)

    #### plot ####

    U_title = figure_t.gen_title('Population U', start, end)
    U_text = figure_t.gen_text(np.mean(U_ave), np.std(U_ave))
    V_title = figure_t.gen_title('Population V', start, end)
    V_text = figure_t.gen_text(np.mean(V_ave), np.std(V_ave))

    ax_U = figure_t.bar(U_ave, ax = ax_U, color = U_color, xlabel = 'patches', ylabel = 'U', title = U_title, text = U_text)
    ax_V = figure_t.bar(V_ave, ax = ax_V, color = V_color, xlabel = 'patches', ylabel = 'V', title = V_title, text = V_text)

    return ax_U, ax_V




def UV_dyna(mod, ax = None, interval = 20, grid = True):
    '''
    Plots how total U, V change overtime.
    The curves are not directly based on every single data point. 
    Rather, it takes the average over many intervals of points to smooth out local fluctuations.
        For example, interval = 20 means the first point on the curves are based on the average value of data points 0~19.
        So if there are 2000 data points in total, then there will be 2000 / 20 = 100 points on the curves.

    Inputs:
        mod:        A simulation.model object.
        ax:         matplotlib ax to plot on. New ax will be created if None is given.
        interval:   How many data points to take average over. Larger value makes curves smoother, but also loses local fluctuations.
                    NOTE: this interval doesn't overlap with mod.compress_itv. 
                    e.g. you already took average over every 20 data points, then using interval <= 20 here has no smoothing effect.
        grid:       Whether to add grid lines to plot.
    
    Returns:
        ax:        matplotlib ax, contains U's, V's, and sum of U & V population.
    '''
    
    # store the average values in lists
    U_curve = []
    V_curve = []
    total_curve = []

    interval = figure_t.scale_interval(interval, mod.compress_itv)
    interval_num = int(mod.max_record / interval)
    
    for i in range(interval_num):
        U_ave = figure_t.ave_interval(mod.U, i * interval, (i + 1) * interval)
        V_ave = figure_t.ave_interval(mod.V, i * interval, (i + 1) * interval)
        
        U_curve.append(np.sum(U_ave))
        V_curve.append(np.sum(V_ave))
        total_curve.append(U_curve[-1] + V_curve[-1])
        
    #### plot ####   
    xaxis = np.linspace(0, mod.maxtime, len(U_curve))

    if ax == None:
        _, ax = plt.subplots()
    ax.grid(grid)
    ax.plot(xaxis, U_curve, CURVE_TYPE, label = 'U')
    ax.plot(xaxis, V_curve, CURVE_TYPE, label = 'V')
    ax.plot(xaxis, total_curve, CURVE_TYPE, label = 'total')
    ax.set_xlabel('Time')
    ax.set_ylabel('Population')
    ax.set_title('Population U & V Over Time')
    ax.legend()

    return ax




def UV_hist(mod, ax_U = None, ax_V = None, U_color = 'purple', V_color = 'green', start = 0.95, end = 1.0):
    '''
    Makes density histograms for U, V's average distribution over an interval.
    Sometimes it may not be shown in density plots due to matplotlib features.

    Returns:
        ax_U, ax_V: matplotlib axes with heatmaps of U, V population density plotted upon.
    '''

    start_index = int(start * mod.max_record)
    end_index = int(end * mod.max_record)
    
    U_ave = figure_t.ave_interval_1D(mod.U, start_index, end_index)
    V_ave = figure_t.ave_interval_1D(mod.V, start_index, end_index)
    
    #### plot ####
    
    if ax_U == None:
        _, ax_U = plt.subplots()
    ax_U.set_xlabel('Population U')
    ax_U.set_ylabel('Density')
    ax_U.hist(U_ave, color = U_color, density = True)
    ax_U.set_title(figure_t.gen_title('U Hist', start, end))
    
    if ax_V == None:
        _, ax_V = plt.subplots()
    ax_V.set_xlabel('Population V')
    ax_V.set_ylabel('Density')
    ax_V.hist(V_ave, color = V_color, density = True)
    ax_V.set_title(figure_t.gen_title('V Hist', start, end))

    return ax_U, ax_V




def UV_std(mod, ax = None, interval = 20, grid = True):
    '''
    Plots how standard deviation of U, V change over time.
    Takes average over many small interval to smooth out local fluctuations.

    Returns:
        ax:    matplotlib ax, contains U's and V's std curves.
    '''

    interval = figure_t.scale_interval(interval, mod.compress_itv)
    interval_num = int(mod.max_record / interval)
    
    U_std = []
    V_std = []
    
    for i in range(interval_num):
        U_ave = figure_t.ave_interval(mod.U, i * interval, (i + 1) * interval)
        V_ave = figure_t.ave_interval(mod.V, i * interval, (i + 1) * interval)
        
        U_std.append(np.std(U_ave))
        V_std.append(np.std(V_ave))
    
    #### plot ####
    xaxis = np.linspace(0, mod.maxtime, len(U_std))

    if ax == None:
        _, ax = plt.subplots()
    ax.grid(grid)
    ax.plot(xaxis, U_std, CURVE_TYPE, label = 'U std')
    ax.plot(xaxis, V_std, CURVE_TYPE, label = 'V std')
    ax.legend()
    ax.set_xlabel('Time')
    ax.set_ylabel('Std Dev')
    ax.set_title('Population Std-Dev Dynamics')

    return ax



def UV_expected_val(mod):
    '''
    Calculate expected U & V distribution based on matrices, assume no migration.
    To differentiate from UV_expected in figures.py: this one return arrays (values).
    '''
    
    U_expected = np.zeros((mod.N, mod.M))
    V_expected = np.zeros((mod.N, mod.M))
    
    for i in range(mod.N):
        for j in range(mod.M):
            # say matrix = [a, b, c, d]
            # U_proportion = (d - b) / (a - b - c + d)
            U_prop = (mod.X[i][j][3] - mod.X[i][j][1]) / (mod.X[i][j][0] - mod.X[i][j][1] - mod.X[i][j][2] + mod.X[i][j][3])
            # equilibrium payoff, U_payoff = V_payoff
            eq_payoff = U_prop * mod.X[i][j][0] + (1 - U_prop) * mod.X[i][j][1]
            
            # payoff / kappa * proportion
            U_expected[i][j] = eq_payoff / mod.P[i][j][4] * U_prop
            V_expected[i][j] = eq_payoff / mod.P[i][j][5] * (1 - U_prop)
                
    return U_expected, V_expected




def UV_expected(mod, ax_U = None, ax_V = None, U_color = 'Purples', V_color = 'Greens', annot = False, fmt = '.3g'):
    '''
    Calculate expected population distribution based on matrices, assuming no migration.
    For the formulas, see stochastic_mode.expected_UV

    Some Inputs:
        Note the colors are color maps.
    
    Returns:
    ax_U, ax_V: If 2D (N and M both > 1), then ax_U and ax_V are heatmaps.
                If 1D (N or M == 1), then ax_U and ax_V are barplots.
    '''
    
    U_expected, V_expected = UV_expected_val(mod)
    
    U_text = figure_t.gen_text(np.mean(U_expected), np.std(U_expected))
    V_text = figure_t.gen_text(np.mean(V_expected), np.std(V_expected))
    
    #### plot ####
    
    if (mod.N != 1) and (mod.M != 1):
        # 2D
        ax_U = figure_t.heatmap(U_expected, ax_U, U_color, annot, fmt, title = 'Expected U', text = U_text)
        ax_V = figure_t.heatmap(V_expected, ax_V, V_color, annot, fmt, title = 'Expected V', text = V_text)

    else:
        # 1D     
        ax_U = figure_t.bar(U_expected.flatten(), ax_U, color = U_color, xlabel = 'patches', ylabel = 'popu', title = 'Expected Population U', text = U_text)
        ax_V = figure_t.bar(V_expected.flatten(), ax_V, color = V_color, xlabel = 'patches', ylabel = 'popu', title = 'Expected Population V', text = V_text)

    return ax_U, ax_V




def pi_heatmap(mod, ax_U = None, ax_V = None, U_color = 'BuPu', V_color = 'YlGn', start = 0.95, end = 1.0, annot = False, fmt = '.3g'):
    '''
    Make heatmaps for payoff in a specified interval.
    Works best for 2D. 1D works as well, but figures look bad.

    Some Inputs:.
        Note the colors are matplotlib color maps.

    Returns:
        ax_U, ax_V: Seaborn heatmaps, for U's & V's payoff distribution, respectively.
    '''
    
    start_index = int(mod.max_record * start)
    end_index = int(mod.max_record * end)
    
    Upi_ave = figure_t.ave_interval(mod.Upi, start_index, end_index)
    V_pi_ave = figure_t.ave_interval(mod.Vpi, start_index, end_index)
    
    U_title = figure_t.gen_title('Payoff ' + r'$p_U$', start, end)
    U_text = figure_t.gen_text(np.mean(Upi_ave), np.std(Upi_ave))
    V_title = figure_t.gen_title('Payoff ' + r'$p_V$', start, end)
    V_text = figure_t.gen_text(np.mean(V_pi_ave), np.std(V_pi_ave))
    
    ax_U = figure_t.heatmap(Upi_ave, ax_U, U_color, annot, fmt, U_title, U_text)
    ax_V = figure_t.heatmap(V_pi_ave, ax_V, V_color, annot, fmt, V_title, V_text)

    return ax_U, ax_V




def pi_bar(mod, ax_U = None, ax_V = None, U_color = 'violet', V_color = 'yellowgreen', start = 0.95, end = 1.0):
    '''
    Make barplot for payoff in a specified interval.
    Works best for 1D. 2D works as well, but figures look bad.

    Returns:
        ax_U, ax_V: matplotlib axes with barplots of U and V payoff distribution plotted upon.
    '''
    
    start_index = int(mod.max_record * start)
    end_index = int(mod.max_record * end)
    
    Upi_ave = figure_t.ave_interval_1D(mod.Upi, start_index, end_index)
    V_pi_ave = figure_t.ave_interval_1D(mod.Vpi, start_index, end_index)
    
    U_title = figure_t.gen_title(r'$p_U$', start, end)
    U_text = figure_t.gen_text(np.mean(Upi_ave), np.std(Upi_ave))
    V_title = figure_t.gen_title(r'$p_V$', start, end)
    V_text = figure_t.gen_text(np.mean(V_pi_ave), np.std(V_pi_ave))
    
    ax_U = figure_t.bar(Upi_ave, ax_U, U_color, 'Patches', 'Payoff ' + r'$p_U$', U_title, U_text)
    ax_V = figure_t.bar(V_pi_ave, ax_V, V_color, 'Patches', 'Payoff ' + r'$p_V$', V_title, V_text)

    return ax_U, ax_V




def pi_dyna(mod, ax = None, interval = 20, grid = True):
    '''
    Plot how payoffs change over time.

    Returns:
        ax:    matplotlib ax of U's, V's, and sum of U & V payoff.
    '''
    
    U_curve = []
    V_curve = []
    total_curve = []

    interval = figure_t.scale_interval(interval, mod.compress_itv)
    interval_num = int(mod.max_record / interval)
    
    for i in range(interval_num):
        U_ave = figure_t.ave_interval(mod.Upi, i * interval, (i + 1) * interval)
        V_ave = figure_t.ave_interval(mod.Vpi, i * interval, (i + 1) * interval)
    
        U_curve.append(np.sum(U_ave))
        V_curve.append(np.sum(V_ave))
        total_curve.append(U_curve[-1] + V_curve[-1])
        
    #### plot ####    
    xaxis = np.linspace(0, mod.maxtime, len(U_curve))
    
    if ax == None:
        _, ax = plt.subplots()
    ax.grid(grid)
    ax.plot(xaxis, U_curve, CURVE_TYPE, label = r'$p_U$')
    ax.plot(xaxis, V_curve, CURVE_TYPE, label = r'$p_V$')
    ax.plot(xaxis, total_curve, CURVE_TYPE, label = 'total')
    ax.set_xlabel('Time')
    ax.set_ylabel('Payoff')
    ax.set_title('Payoff ' + r'$p_U$' + ' & ' + r'$p_V$' + ' over time')
    ax.legend()

    return ax




def pi_hist(mod, ax_U = None, ax_V = None, U_color = 'violet', V_color = 'yellowgreen', start = 0.95, end = 1.0):
    '''
    Makes deensity histograms of U's and V's payoffs in a sepcified interval.
    Sometimes it may not be shown in density plots due to matplotlib features.
    
    Returns:
        ax_U, ax_V:     histogram of U's and V's payoff.
    '''

    start_index = int(start * mod.max_record)
    end_index = int(end * mod.max_record)

    Upi_ave = figure_t.ave_interval_1D(mod.Upi, start_index, end_index)
    V_pi_ave = figure_t.ave_interval_1D(mod.Vpi, start_index, end_index)
    
    #### plot ####
    
    if ax_U == None:
        _, ax_U = plt.subplots()
    ax_U.set_xlabel('Payoff ' + r'$p_U$')
    ax_U.set_ylabel('Density')
    ax_U.hist(Upi_ave, color = U_color, density = True)
    ax_U.set_title(figure_t.gen_title('Payoff ' + r'$p_U$' + ' Hist', start, end))
    
    if ax_V == None:
        _, ax_V = plt.subplots()
    ax_V.set_xlabel('Payoff ' + r'$p_V$')
    ax_V.set_ylabel('Density')
    ax_V.hist(V_pi_ave, color = V_color, density = True)
    ax_V.set_title(figure_t.gen_title('Payoff ' + r'$p_V$' + ' Hist', start, end))

    return ax_U, ax_V




def pi_std(mod, ax = None, interval = 20, grid = True):
    '''
    Plots how standard deviation of payoff change over time.

    Returns:
        ax:    matplotlib ax of the std of payoffs.
    '''
    
    
    interval = figure_t.scale_interval(interval, mod.compress_itv)
    interval_num = int(mod.max_record / interval)
    
    Upi_std = []
    V_pi_std = []
    
    for i in range(interval_num):
        Upi_ave = figure_t.ave_interval(mod.Upi, i * interval, (i + 1) * interval)
        V_pi_ave = figure_t.ave_interval(mod.Vpi, i * interval, (i + 1) * interval)
        
        Upi_std.append(np.std(Upi_ave))
        V_pi_std.append(np.std(V_pi_ave))
    
    #### plot ####
    xaxis = np.linspace(0, mod.maxtime, len(Upi_std))
    
    if ax == None:
        _, ax = plt.subplots()
    ax.grid(grid)
    ax.plot(xaxis, Upi_std, CURVE_TYPE, label = r'$p_U$' + ' std')
    ax.plot(xaxis, V_pi_std, CURVE_TYPE, label = r'$p_V$' + ' std')
    ax.legend()
    ax.set_xlabel('Time')
    ax.set_ylabel('Std Dev')
    ax.set_title('Payoff Std-Dev Dynamics')
    
    return ax




def UV_pi(mod, ax_U = None, ax_V = None, U_color = 'violet', V_color = 'yellowgreen', alpha = 0.5, start = 0.95, end = 1.0):
    '''
    Make two scatter plots: x-axes are population and y-axes are payoff in a specified time interval.
    Reveals relationship between population and payoff.

    Returns:
        ax_U, ax_V: matplotlib axes with U and V population-payoff scatter plots.
    '''
    
    start_index = int(start * mod.max_record)
    end_index = int(end * mod.max_record)
    
    U_ave = figure_t.ave_interval_1D(mod.U, start_index, end_index)
    V_ave = figure_t.ave_interval_1D(mod.V, start_index, end_index)

    Upi_ave = figure_t.ave_interval(mod.Upi, start_index, end_index)
    V_pi_ave = figure_t.ave_interval(mod.Vpi, start_index, end_index)
    
    
    ax_U = figure_t.scatter(U_ave, Upi_ave, ax_U, U_color, alpha, xlabel = 'U', ylabel = 'Payoff ' + r'$p_U$', title = 'U - ' + r'$p_U$')
    ax_V = figure_t.scatter(V_ave, V_pi_ave, ax_V, V_color, alpha, xlabel = 'V', ylabel = 'Payoff ' + r'$p_V$', title = 'V - ' + r'$p_V$')
    
    return ax_U, ax_V


