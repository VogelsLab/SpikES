import numpy as np
import matplotlib.pyplot as plt
import subprocess
import random
from Innerloops.Innerloop import Innerloop
from concurrent import futures


class Innerloop_FamDet_Lbasic_TIF_EEIE_6pPol(Innerloop):
    """
    Information about Innerloop_FamDet_Lbasic_TIF_EEIE_6pPol:

    TODO!
    """
    
    def __init__(self, inner_loop_params):

        self.req_cls_str_args = [
            'NE',
            'NI',
            'wei',
            'wii',
            'sparseness',
            'length_train_low',
            'length_train_high',
            'length_break_low',
            'length_break_high',
            'length_scoring_window',
            'ontime_train',
            'ontime_test',
            'offtime_train',
            'offtime_test',
            'r_cut_fam',
            'r_cut_nov',
            'min_rate_checker',
            'max_rate_checker',
            'tau_checker_pop',
            'N_inputs',
            'w_poisson',
            'poisson_rate_low',
            'poisson_rate_high',
            'radius',
            'N_active_input',
            'N_patterns',
            'active_input_rate_low',
            'active_input_rate_high',
            'eta',
            'wmaxee_low',
            'wmaxee_high',
            'wee_low',
            'wee_high',
            'wmaxie_low',
            'wmaxie_high',
            'wie_low',
            'wie_high',
            'auryn_sim_dir',
            'hardware',
            'n_rules',
            'Lr',
            'Nd',
            'workdir'
        ]
         
        # Check if required arguments are in param dictionary
        assert np.all(
            [
                k in inner_loop_params.keys()
                for k in (self.req_cls_str_args)
            ]
        )

        # Network architecture
        self.NE = inner_loop_params['NE']                                       #total number of excitatory input neurons
        self.NI = inner_loop_params['NI']                                       #total number of inhibitory input neurons
        self.wei = inner_loop_params['wei']                                     #wei in units of leak conductance
        self.wii = inner_loop_params['wii']                                     #wii in units of leak conductance
        self.sparseness = inner_loop_params['sparseness']                       #sparseness of recurrent connections

        # Scoring protocol
        self.length_train_low = inner_loop_params['length_train_low']           #(s)
        self.length_train_high = inner_loop_params['length_train_high']         #(s)
        self.length_break_low = inner_loop_params['length_break_low']           #(s)
        self.length_break_high = inner_loop_params['length_break_high']         #(s)
        self.length_scoring_window = inner_loop_params['length_scoring_window'] #(s)
        self.ontime_train = inner_loop_params['ontime_train']                   #mean duration of 1 pattern presentation during training phase (s)
        self.ontime_test = inner_loop_params['ontime_test']                     #mean duration of 1 pattern presentation during testing phase (s)
        self.offtime_train = inner_loop_params['offtime_train']                 #mean duration between pattern presentations during training phase (s)
        self.offtime_test = inner_loop_params['offtime_test']                   #mean duration between pattern presentations during testing phase (s)
        self.r_cut_fam = inner_loop_params['r_cut_fam']                         #firing rate cut off for familiar patterns (Hz)
        self.r_cut_nov = inner_loop_params['r_cut_nov']                         #firing rate cut off for new patterns (Hz)
        self.min_rate_checker = inner_loop_params['min_rate_checker']           #rate under which a simulation is stopped and "blows up"
        self.max_rate_checker = inner_loop_params['max_rate_checker']           #rate over which a simulation is stopped and "blows up"
        self.tau_checker_pop = inner_loop_params['tau_checker_pop']                     #time constant to evaluate population rate to decide on blow ups

        # Task-relevant parameters
        self.N_inputs = inner_loop_params['N_inputs']                           #number of input neurons
        self.w_poisson = inner_loop_params['w_poisson']                         #weights of poisson to exc and inh neurons
        self.poisson_rate_low = inner_loop_params['poisson_rate_low']           #lowest rate of poisson neurons Hz
        self.poisson_rate_high = inner_loop_params['poisson_rate_high']         #highest rate of poisson neurons Hz
        self.radius = inner_loop_params['radius']                               #radius (in number of neurons) of the receptive field of the exc neurons in the network
        self.N_active_input = inner_loop_params['N_active_input']               #number of active input neurons in one pattern
        self.N_patterns = inner_loop_params['N_patterns']                       #number of patterns
        self.active_input_rate_low = inner_loop_params['active_input_rate_low'] #highest rate of poisson neurons Hz
        self.active_input_rate_high = inner_loop_params['active_input_rate_high']#highest rate of poisson neurons Hz
        
        # Plasticity parameters
        self.eta = inner_loop_params['eta']                                     #learning rate of the plasticity rule
        self.wmaxee_low = inner_loop_params['wmaxee_low']                       #lower bound for maximum excitatory weights
        self.wmaxee_high = inner_loop_params['wmaxee_high']                     #upper bound for maximum excitatory weights
        self.wee_low = inner_loop_params['wee_low']                             #wee_low in units of leak conductance
        self.wee_high = inner_loop_params['wee_high']                           #wee_high in units of leak conductance
        self.wmaxie_low = inner_loop_params['wmaxie_low']                       #lower bound for maximum ie weights
        self.wmaxie_high = inner_loop_params['wmaxie_high']                     #upper bound for maximum ie weights
        self.wie_low = inner_loop_params['wie_low']                             #wie_low in units of leak conductance
        self.wie_high = inner_loop_params['wie_high']                           #wie_high in units of leak conductance


        # Other general innerloop params
        self.auryn_sim_dir = inner_loop_params['auryn_sim_dir']                 #directory where auryn executable is located
        self.parallel_args = ''                #arguments for SLURM job array submission or local parallel execution
        self.hardware = inner_loop_params['hardware']                           #'local' or 'slurm_cluster'
        self.Nr = inner_loop_params['n_rules']                                  #number of rules to score during each meta-iteration
        self.Lr = inner_loop_params['Lr']                                       #number of parameters of one plasticity rule
        self.Nd = inner_loop_params['Nd']                                       #number of input datasets used to compute the loss
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
            rule_str = " --ruleEE a" + str(np.exp(A[rule_num][0])) + "a" + str(np.exp(A[rule_num][1]))
            rule_str += "a" + str(A[rule_num][2]) +  "a" + str(A[rule_num][3]) + "a" + str(A[rule_num][4]) +\
             "a" + str(A[rule_num][5]) + "a"
            rule_str += " --ruleIE a" + str(np.exp(A[rule_num][6])) + "a" + str(np.exp(A[rule_num][7]))
            rule_str += "a" + str(A[rule_num][8]) +  "a" + str(A[rule_num][9]) + "a" + str(A[rule_num][10]) +\
             "a" + str(A[rule_num][11]) + "a"
        
            for dataset_num in range(self.Nd):
                cl_str = self.auryn_sim_dir + "sim_innerloop_FamDet_Lbasic_TIF_EEIE_6pPol --ID " + str(id) +\
                    " --NE " + str(self.NE) +\
                    " --NI " + str(self.NI) +\
                    " --wee " + str(random.uniform(self.wee_low, self.wee_high)) +\
                    " --wei " + str(self.wei) +\
                    " --wie " + str(random.uniform(self.wie_low, self.wie_high)) +\
                    " --wii " + str(self.wii) +\
                    " --eta " + str(self.eta) +\
                    rule_str +\
                    " --wmaxee " + str(np.exp(random.uniform(np.log(self.wmaxee_low), np.log(self.wmaxee_high)))) +\
                    " --wmaxie " + str(np.exp(random.uniform(np.log(self.wmaxie_low), np.log(self.wmaxie_high)))) +\
                    " --sparseness " + str(self.sparseness) +\
                    " --l_train " + str(random.uniform(self.length_train_low, self.length_train_high)) +\
                    " --l_break1 " + str(random.uniform(self.length_break_low, self.length_break_high)) +\
                    " --l_score " + str(self.length_scoring_window) +\
                    " --l_break2 " + str(random.uniform(self.length_break_low, self.length_break_high)) +\
                    " --rate_cut_fam " + str(self.r_cut_fam) +\
                    " --rate_cut_nov " + str(self.r_cut_nov) +\
                    " --N_inputs " + str(self.N_inputs) +\
                    " --w_poisson " + str(self.w_poisson) +\
                    " --bg_input_rate " + str(random.uniform(self.poisson_rate_low, self.poisson_rate_high)) +\
                    " --N_active_input " + str(self.N_active_input) +\
                    " --active_input_rate " + str(random.uniform(self.active_input_rate_low, self.active_input_rate_high)) +\
                    " --N_patterns " + str(self.N_patterns) +\
                    " --radius " + str(self.radius) +\
                    " --tau_checker_pop " + str(self.tau_checker_pop) +\
                    " --ontime_train " + str(self.ontime_train) +\
                    " --offtime_train " + str(self.offtime_train) +\
                    " --ontime_test " + str(self.ontime_test) +\
                    " --offtime_test " + str(self.offtime_test) +\
                    " --min_rate_checker " + str(self.min_rate_checker) +\
                    " --max_rate_checker " + str(self.max_rate_checker) +\
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
        return("Above: parameters from Innerloop_FamDet_Lbasic_TIF_IE_6pPol: " + str(print(vars(self))))
    
    
    
    def plot_optimization(self, rule_hist, loss_hist, n_meta_it, lr):
        plot_parameters(rule_hist, n_meta_it)
        plot_loss(loss_hist, n_meta_it)



## Plotting functions

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