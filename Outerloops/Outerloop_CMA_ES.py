import numpy as np
from Outerloops.Outerloop import Outerloop
import Innerloops

class Outerloop_CMA_ES(Outerloop):
    """
    Information on Outerloop_CMA_ES:
    Outer loop using the evolutionnary strategy CMA_ES. Based on The CMA Evolution Strategy: A Tutorial, Nikolaus Hansen, arXiv 2016
    At each generation, new individuals (here plasticity rules) are drawn from N(m,C). Both m (distr mean) and C (covariance matrix) are learnt")
    Specific requirements for innerloop: none

    Important parameters:
    lambda: generation size. Can be set automatically depending on n_coeffs of the plasticity rules, but this number is often too small
    sigma: initial step size for both m and C. sigma is adaptative, but initial value should be ~0.3(a-b) if the the estimated search range for the plasticity rules coeffs is [a,b]**lr
    reg: coefficient for L1 regularization
    There are many other parameters, most of them have a strongly recommended value (see tutorial). Go inside the code to change them if needed
    """
       
    def __init__(self, outerloop_params, innerloop_params): 
        # L1 regularization on plasticity rule parameters
        self.reg = outerloop_params["reg"]
        
        # optimizer parameters
        self.lr = len(outerloop_params["A"])
        self.current_meta_it = 0
        if outerloop_params["lambd"] == "auto":
            self.lambd = int(4 + np.floor(3*np.log(len(outerloop_params["A"])))) #number of search points in a generation #population size
            print("generation size lambda = " + str(self.lambd))
        else:
            self.lambd = outerloop_params["lambd"]
        innerloop_params["n_rules"] = self.lambd + 1 #+1 cuz we will test self.m for plotting purpose in addition
        self.mu = int(np.floor(self.lambd/2)) #number of non negative recombination weights
        wi_aux = np.array([np.log((self.lambd + 1)/2) - np.log(i+1) for i in range(self.lambd)])
        self.mu_eff = np.sum(wi_aux[:self.mu])**2/np.sum(np.multiply(wi_aux[:self.mu], wi_aux[:self.mu]))
        
        # covariance matrix adaptation
        self.c_c = (4 + self.mu_eff/self.lr)/(self.lr + 4 + 2*self.mu_eff/self.lr)
        self.c_1 = 2/((self.lr + 1.3)**2 + self.mu_eff)
        self.c_mu = np.minimum(1 - self.c_1, 2*(self.mu_eff - 2 + 1/self.mu_eff)/((self.lr + 2)**2 + self.mu_eff))
        
        # selection and recombination
        mu_eff_m = np.sum(wi_aux[self.mu+1:])**2/np.sum(np.multiply(wi_aux[self.mu+1:], wi_aux[self.mu+1:]))
        alpha_mu_m = 1 + self.c_1/self.c_mu
        alpha_mu_eff_m = 1 + 2*mu_eff_m/(self.mu_eff + 2)
        alpha_pos_def_m = (1 - self.c_1 - self.c_mu)/(self.lr*self.c_mu)
        sum_wi_aux_pos = 0; sum_wi_aux_neg = 0
        for i in range(self.lambd):
            if wi_aux[i] >= 0:
                sum_wi_aux_pos += wi_aux[i]
            else:
                sum_wi_aux_neg -= wi_aux[i]
            
        self.wi = np.zeros(self.lambd) #recombination weights
        for i in range(self.lambd):
            if wi_aux[i] >= 0:
                self.wi[i] = wi_aux[i]/sum_wi_aux_pos
            else:
                self.wi[i] = wi_aux[i]*np.minimum(alpha_mu_m, np.minimum(alpha_mu_eff_m, alpha_pos_def_m))/sum_wi_aux_neg
            
        # step size control
        self.c_sig = (self.mu_eff + 2)/(self.lr + self.mu_eff + 5)
        self.d_sig = 1 + 2*np.maximum(0, np.sqrt((self.mu_eff - 1)/(self.lr + 1)) - 1) + self.c_sig
        
        # optimizer initialisation
        self.C = np.identity(self.lr) #initial covariance matrix
        self.m = outerloop_params["A"] #initial mean distribution
        self.sigma = outerloop_params["sigma"] #step size
        self.p_sig= np.zeros(self.lr) #evolution path
        self.p_c = np.zeros(self.lr) #evolution path
        self.chiN = np.sqrt(self.lr)*(1 - 1/(4*self.lr) + 1/(21*(self.lr**2))) #expectation of ||N(0,I)||
        self.innerloop = getattr(getattr(Innerloops,outerloop_params['inner_loop'] ), outerloop_params['inner_loop'])(innerloop_params)
        self.innerloop_name = outerloop_params['inner_loop']
        
        # for plotting
        self.rule_hist = np.array([outerloop_params["A"]]) #plot best element of population at each meta-iteration
        self.loss_hist = []  #plot loss associated to best element in the population
        self.sigma_init = outerloop_params["sigma"]
        self.C_hist = []; #keep covariance matrices along evolutionnary path
        
        

    def score_population(self, x): #evaluate meta-objective at the points in parameter space in A_pop 
        loss_no_l1 = self.innerloop.score(x)
        l1 = np.multiply([np.linalg.norm(x[i, :],ord = 1).item() for i in range(self.lambd)],self.reg)
        return(loss_no_l1[-1], loss_no_l1[:-1] + l1)
    
    
    
    def run(self, n_meta_it):
        initial_meta_it = self.current_meta_it #meta-it is the generation number
        
        while self.current_meta_it < (initial_meta_it + n_meta_it):   
            
            # eigendecomposition of C: C = BDDt(B) 
            D,B = np.linalg.eigh(self.C)
            D = np.diagflat(np.sqrt(D))
            
            # sample new population of search points
            z = np.array([np.random.multivariate_normal([0 for i in range(self.lr)], np.identity(self.lr)) for j in range(self.lambd)])
            y = np.array([np.matmul(B, np.matmul(D, z[i,:])) for i in range(self.lambd)])
            x = self.m + self.sigma*y #x are the new population of rules for this generation (i.e. meta-iteration)
            
            # sort population by ascending score
            x_aux = np.concatenate((x, np.expand_dims(self.m, axis=0))) #get loss(m) for plotting purposes only, m itself not included as an individual in CMA-ES
            loss_current, meta_obj = self.score_population(x_aux)
            x_sorted = np.array([x for _,x in sorted(zip(meta_obj, x), key=lambda pair: pair[0])]) 
            y_sorted = (x_sorted - self.m)/self.sigma
            
            # selection and recombination
            y_w = np.sum(np.array([self.wi[i]*y_sorted[i,:] for i in range(self.mu)]), axis = 0) #step of the distribution mean
            self.m = self.m + 1*self.sigma*y_w #cm = 1, see tuto
            
            # step size control
            d_1 = np.diagflat([1/i for i in np.diagonal(D)])
            C_12 = np.matmul(B, np.matmul(d_1, np.transpose(B)))
            self.p_sig = (1 - self.c_sig)*self.p_sig + np.sqrt(self.c_sig*(2 - self.c_sig)*self.mu_eff)*np.matmul(C_12, y_w)
            self.sigma = self.sigma*np.exp((self.c_sig/self.d_sig)*((np.linalg.norm(self.p_sig)/self.chiN) - 1))
            
            # heaviside function for step size control
            if np.linalg.norm(self.p_sig)/np.sqrt(1 - (1 - self.c_sig)**(2*(self.current_meta_it + 1))) < \
            (1.4 + 2/(self.lr + 1))*self.chiN:
                h_sig = 1
            else:
                h_sig = 0
            
            # covariance matrix adaptation
            self.p_c = (1 - self.c_c)*self.p_c + h_sig*np.sqrt(self.c_c*(2 - self.c_c)*self.mu_eff)*y_w
            wi_o = np.zeros(self.lambd)
            for i in range(self.lambd):
                if self.wi[i] > 0:
                    wi_o[i] = self.wi[i]
                else:
                    wi_o[i] = self.wi[i]*self.lr/(np.linalg.norm(np.matmul(C_12, y_sorted[i,:])))**2
            delta_h_sig = (1 - h_sig)*self.c_c*(2 - self.c_c)
            self.C = (1 + self.c_1*delta_h_sig - self.c_1 - self.c_mu*np.sum(self.wi))*self.C \
            + self.c_1*np.outer(self.p_c, self.p_c) \
            + self.c_mu*np.sum([wi_o[i]*np.outer(y_sorted[i,:], y_sorted[i,:]) for i in range(self.lambd)], axis = 0)

            # keep user informed of meta-optimization progress
            if (self.current_meta_it % 5 == 0):
                print("iteration " + str(self.current_meta_it+1) + "/" + str(initial_meta_it + n_meta_it))
                print("current_loss (without outerloop regularizations): " + str(loss_current))
                print("m " + str(self.m))
                print("sigma " + str(self.sigma))
#             print("cov " + str(self.C))
#             print("evol path " + str(self.p_c))
    
            self.current_meta_it += 1  
            self.rule_hist = np.concatenate((self.rule_hist, np.array([self.m])), axis = 0)
            self.loss_hist.append(loss_current)
            self.C_hist.append(self.C)
            
            
            
    def save(self, name, path):
        return("TODO")
    
    
    
    def __str__(self):
        return("Above: parameters from Outerloop_CMA_ES. " + str(print(vars(self))))


    def plot(self):
        super().plot()