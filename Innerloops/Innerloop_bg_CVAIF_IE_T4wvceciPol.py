import numpy as np
import matplotlib.pyplot as plt
import subprocess
import random
from Innerloops.Innerloop import Innerloop
from concurrent import futures
import torch
from torch import nn


class Innerloop_bg_CVAIF_IE_T4wvceciPol(Innerloop):
    """
    Information about Innerloop_bg_CVAIF_IE_T4wvceciPol:

    Innerloop that calls NE + NI E-I network (see Vogels et al. 2011 for details). Loss scores spread to target firing rate of the exc population
    This Innerloop can run on a desktop or on a cluster using the submitit library

    Important parameters:
    [wie_low, wie_high]: initial IE weights
    length_training_phase, length_scoring_phase, length_scoring_window: scoring protocol
    auryn_sim_dir: where the auryn executable is located
    workdir: directory where auryn can write/read from files if needed (usually /sim_workdir)
    target: target firing rate for the exc population
    """
    
    def __init__(self, inner_loop_params):

        self.req_cls_str_args = [
            "auryn_sim_dir",
            "hardware",
            "n_rules",
            "Lr",
            "Nd",
            "NE",
            "NI",
            "wee",
            "wei",
            "wie_low",
            "wie_high",
            "wii",
            "wmax_low",
            "wmax_high",
            "sparseness",
            "length_training_phase",
            "length_scoring_phase",
            "length_scoring_window",
            "target",
            "N_inputs",
            "sparseness_poisson",
            "w_poisson",
            "poisson_rate_low",
            "poisson_rate_high",
            "min_rate_checker",
            "max_rate_checker",
            "tau_checker",
            "workdir",
        ]
         
        # Check if required arguments are in param dictionary
        assert np.all(
            [
                k in inner_loop_params.keys()
                for k in (self.req_cls_str_args)
            ]
        )

        self.auryn_sim_dir = inner_loop_params['auryn_sim_dir']                 #directory where auryn executable is located
        self.hardware = inner_loop_params['hardware']                           #'local' or 'slurm_cluster'
        self.parallel_args = ''                 #arguments for SLURM job array submission or local parallel execution
        self.Nr = inner_loop_params['n_rules']                                  #number of rules to score during each meta-iteration
        self.Lr = inner_loop_params['Lr']                                       #number of parameters of one plasticity rule
        self.Nd = inner_loop_params['Nd']                                       #number of input datasets used to compute the loss
        self.NE = inner_loop_params['NE']                                       #total number of excitatory input neurons
        self.NI = inner_loop_params['NI']                                       #total number of inhibitory input neurons
        self.wee = inner_loop_params['wee']                                     #wee in units of leak conductance
        self.wei = inner_loop_params['wei']                                     #wei in units of leak conductance
        self.wie_low = inner_loop_params['wie_low']                             #wie_low in units of leak conductance
        self.wie_high = inner_loop_params['wie_high']                           #wie_high in units of leak conductance
        self.wii = inner_loop_params['wii']                                     #wii in units of leak conductance
        self.wmax_low = inner_loop_params['wmax_low']                           #lower bound for maximum excitatory weights
        self.wmax_high = inner_loop_params['wmax_high']                         #upper bound for maximum excitatory weights
        self.sparseness = inner_loop_params['sparseness']                       #sparseness of recurrent connections
        self.length_training_phase = inner_loop_params['length_training_phase'] #s
        self.length_scoring_phase = inner_loop_params['length_scoring_phase']   #s
        self.length_scoring_window = inner_loop_params['length_scoring_window'] #s
        self.target = inner_loop_params['target']                               #target firing rate for loss function, Hz
        self.N_inputs = inner_loop_params['N_inputs']                           #number of input neurons
        self.sparseness_poisson = inner_loop_params['sparseness_poisson']       #sparseness of poisson to exc and inh neurons
        self.w_poisson = inner_loop_params['w_poisson']                         #weights of poisson to exc and inh neurons
        self.poisson_rate_low = inner_loop_params['poisson_rate_low']           #lowest rate of poisson neurons Hz
        self.poisson_rate_high = inner_loop_params['poisson_rate_high']         #highest rate of poisson neurons Hz
        self.min_rate_checker = inner_loop_params['min_rate_checker']           #rate under which a simulation is stopped and "blows up"
        self.max_rate_checker = inner_loop_params['max_rate_checker']           #rate over which a simulation is stopped and "blows up"
        self.tau_checker = inner_loop_params['tau_checker']                     #time constant to evaluate population rate to decide on blow ups
        self.workdir = inner_loop_params['workdir']                             #directory where auryn can write/read files (currently monitor outputs)
        
    def score(self, A):
        """
        simulates Nd networks with Auryn for each plasticity rule in A
        convention: size(A) = [n_rules to test, n_param/sim_workdir/s of one rule: tau_pre, tau_post, alpha, beta, kappa, gamma]
        convention: assuming we are getting log(tau_pre) and log(tau_post) in A
        """
        # generate the parameters for each auryn simulation
        id = 0
        call_strings_array = []

        for rule_num in range(self.Nr):

            rule_str = make_rule_str(A[rule_num])
        
            for dataset_num in range(self.Nd):
                # generate the parameters for that simualtion
                lns = random.uniform(self.length_training_phase, self.length_training_phase +\
                                                 self.length_scoring_phase - self.length_scoring_window)
                wie = random.uniform(self.wie_low, self.wie_high)
                wmax = np.exp(random.uniform(np.log(self.wmax_low), np.log(self.wmax_high))) #log uniform distribution
                poisson_rate = random.uniform(self.poisson_rate_low, self.poisson_rate_high)

                cl_str = self.auryn_sim_dir + "sim_innerloop_bg_CVAIF_IE_T4wvceciPol --ID " + str(id) +\
                    " --NE " + str(self.NE) +\
                    " --NI " + str(self.NI) +\
                    " --wee " + str(self.wee) +\
                    " --wei " + str(self.wei) +\
                    " --wie " + str(wie) +\
                    " --wii " + str(self.wii) +\
                    rule_str +\
                    " --wmax " + str(wmax) +\
                    " --sparseness " + str(self.sparseness) +\
                    " --lns " + str(lns) +\
                    " --ls " + str(self.length_scoring_window) +\
                    " --target " + str(self.target) +\
                    " --N_inputs " + str(self.N_inputs) +\
                    " --sparseness_poisson " + str(self.sparseness_poisson) +\
                    " --w_poisson " + str(self.w_poisson) +\
                    " --poisson_rate " + str(poisson_rate) +\
                    " --min_rate_checker " + str(self.min_rate_checker) +\
                    " --max_rate_checker " + str(self.max_rate_checker) +\
                    " --tau_checker " + str(self.tau_checker) +\
                    " --workdir " + str(self.workdir)

                id += 1
                call_strings_array.append([cl_str])

        if self.hardware == "local": #use concurrent.futures for local multithreading
            with futures.ThreadPoolExecutor(max_workers=self.parallel_args['n_cores']) as executor:
                jobs = [executor.submit(worker, cl_str) for cl_str in call_strings_array]
        else:
            print("hardware option not recognized")


        #################### DEBUG #########################################################################
        # print(call_strings_array)
        ####################################################################################################


        # collect results, average the losses across datasets and send back to outerloop 
        id = 0
        losses = np.zeros(self.Nr)
        for rule_num in range(self.Nr):
            for dataset_num in range(self.Nd):
                losses[rule_num] += jobs[id].result()
                id += 1
        return(losses/self.Nd)

    def __str__(self):
        return("Above: parameters from Innerloop_bg_CVAIF_IE_T4wvceciPol: " + str(print(vars(self))))
    
    def plot_optimization(self, rule_hist, loss_hist, n_meta_it, lr):
        plot_parameters(rule_hist, n_meta_it)
        plot_loss(loss_hist, n_meta_it)



## Plotting functions NOT UPDATED

def plot_parameters(A_hist, n_meta_it, fontsize = 15, linewidth = 2, font = 'Arial', alpha = 1):
    fig, (ax1, ax2) = plt.subplots(figsize=(7, 1.5), nrows=1, ncols=2)
    ax1.plot(np.exp(A_hist[:, 0])*1000, label = r'$\tau_{pre}$ (ms)', linewidth = linewidth, color = "#4863A0", alpha = alpha,zorder = 6)
    ax1.plot(np.exp(A_hist[:, 1])*1000, label = r'$\tau_{post}$ (ms)', linewidth = linewidth, color = '#E15D44', alpha = alpha,zorder = 5)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_linewidth(linewidth)
    ax1.spines['left'].set_linewidth(linewidth)
    ax1.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax1.set_xticks([0,int(n_meta_it/2), n_meta_it])
    ax1.set_xlim([0,n_meta_it])
    ax1.set_xlabel('meta-iterations', fontsize=fontsize, fontname=font)
    for tick in ax1.get_xticklabels():
            tick.set_fontname(font)
    for tick in ax1.get_yticklabels():
            tick.set_fontname(font)
    ax1.set_ylabel('', fontsize=fontsize, fontname=font, labelpad = 9)
    ax1.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
              bbox_to_anchor=(-0.1, 1, 1.2, 0),mode="expand",ncol=2, \
              handlelength=0.6, handletextpad = 0.3, labelspacing = 0.1)

    ax2.plot(A_hist[:, 2], label = r'$\alpha$', linewidth = linewidth, color = '#625D5D', alpha = alpha,zorder = 1)
    ax2.plot(A_hist[:, 3], label = r'$\beta$', linewidth = linewidth, color = '#009B77', alpha = alpha,zorder = 2)
    ax2.plot(A_hist[:, 4], label = r'$\gamma$', linewidth = linewidth, color = '#fdb462', alpha = alpha,zorder = 4)
    ax2.plot(A_hist[:, 5], label = r'$\kappa$', linewidth = linewidth, color = '#B565A7', alpha = alpha,zorder = 3)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_linewidth(linewidth)
    ax2.spines['left'].set_linewidth(linewidth)
    ax2.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax2.set_xticks([0,int(n_meta_it/2), n_meta_it])
    ax2.set_xlim([0,n_meta_it])
    ax2.set_xlabel('meta-iterations', fontsize=fontsize, fontname=font)
    for tick in ax2.get_xticklabels():
            tick.set_fontname(font)
    for tick in ax2.get_yticklabels():
            tick.set_fontname(font)
    ax2.set_ylabel('', fontsize=fontsize, fontname=font, labelpad = 9)
    ax2.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
              bbox_to_anchor=(-0.1, 1, 1.2, 0),mode="expand",ncol=4, \
              handlelength=0.6, handletextpad = 0.3, labelspacing = 0.3)
    plt.show()
 
def plot_loss(loss_hist, n_meta_it, fontsize = 15, linewidth = 2, font = 'Arial', alpha = 1):
    fig, ax = plt.subplots(figsize=(2.5, 1.5))
    ax.semilogy(loss_hist, linewidth = linewidth, color = '#8C001A', alpha = alpha)
    ax.set_xlabel('meta-iterations', fontsize=fontsize, fontname=font)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)
    ax.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax.tick_params(which = 'minor', width=0, labelsize=0, length=0)
    ax.set_xticks([0,int(n_meta_it/2), n_meta_it])
    ax.set_yticks([1e-2,1,100])
    ax.set_ylabel(r'$L$', fontsize=fontsize, fontname=font, labelpad = -6)
    ax.set_xlim([0,n_meta_it])
    plt.show()       
    
def format_func_exc(value, tick_number):
    return(str(int(value/100)+1))

def format_func_inh(value, tick_number):
    return(str(int(value/25)+1))

def format_func_time(value, tick_number):
    return(str(int(value/10000)))



### Auxilliary functions
def worker(args):
    """
    Creates a subprocess to run one auryn network, and sends back the command line output generated by the C++ sim
    args: command line call to auryn simulation (string)
    """
    ####################### DEBUG ##########################################################################################
    # output = subprocess.run(args[0], shell = True, capture_output = True)
    # return(output)
    # return
    ########################################################################################################################
    # call auryn subprocess, capture output of auryn simulation, compute loss from simualtion and return it.
    output = subprocess.run(args[0], shell = True, capture_output = True)
    return (float(output.stdout.decode().split("cynthia")[1]))

def make_rule_str(rule):
    """
    """
    rule_str = " --rule a"
    for i in range(0, len(rule)):
        rule_str += str(rule[i])+"a"
    return(rule_str)