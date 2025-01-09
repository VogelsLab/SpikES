import subprocess
import numpy as np
import time
import os
import matplotlib.pyplot as plt
import time
from mpl_toolkits.axes_grid1 import make_axes_locatable

def compile_and_run_auryn_net(params, compile = True):
    # Make call string for auryn sim
    params["id"] = 0
    if params["name"]=="sim_innerloop_bg_TIF_IE_6pPol":
        cl_str = generate_cl_str_bg_TIF_IE_6pPol(params)
    elif params["name"]=="sim_innerloop_bg_TIF_EE_6pPol":
        cl_str = generate_cl_str_bg_TIF_EE_6pPol(params)
    elif params["name"]=="sim_innerloop_bg_TIF_EI_6pPol":
        cl_str = generate_cl_str_bg_TIF_EI_6pPol(params)
    elif params["name"]=="sim_innerloop_bg_TIF_II_6pPol":
        cl_str = generate_cl_str_bg_TIF_II_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_IE_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_IE_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_EE_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_EE_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_EI_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_EI_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_II_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_II_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_EEIE_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_EEIE_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_EEII_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_EEII_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_EIIE_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_EIIE_6pPol(params)
    elif params["name"]=="sim_innerloop_FamDet_Lbasic_TIF_EEEI_6pPol":
        cl_str = generate_cl_str_FamDet_Lbasic_TIF_EEEI_6pPol(params)
    
    elif params["name"]=="sim_MemoryByHysteresis_FamDet_TIF_IE_6pPol":
        cl_str = generate_cl_str_MemoryByHysteresis_FamDet_TIF_IE_6pPol(params)
    elif params["name"]=="sim_MemoryByHysteresis_FamDet_IF_IE_6pPol":
        cl_str = generate_cl_str_MemoryByHysteresis_FamDet_IF_IE_6pPol(params)
    elif params["name"]=="sim_test_RFConnection":
        cl_str = sim_test_RFConnection(params)
    elif params["name"]=="sim_test_RFConnection1D":
        cl_str = sim_test_RFConnection1D(params)
    elif params["name"]=="sim_MemoryByHysteresis_FamDet_AIF_IE_6pPol":
        cl_str = generate_cl_str_MemoryByHysteresis_FamDet_AIF_IE_6pPol(params)
    elif params["name"]=="sim_MemoryByHysteresis_FamDet_FriedRule_TIF_IE_6pPol":
        cl_str = generate_cl_str_MemoryByHysteresis_FamDet_FriedRule_TIF_IE_6pPol(params)
    elif params["name"]=="sim_StabilityTimRule_TIF":
        cl_str = generate_cl_str_StabilityTimRule_TIF(params)
    elif params["name"]=="sim_StabilityTimRule_TIF_bgCurr":
        cl_str = generate_cl_str_StabilityTimRule_TIF_bgCurr(params)
    elif params["name"]=="sim_StabilityTimRule_AIF":
        cl_str = generate_cl_str_StabilityTimRule_AIF(params)
    elif params["name"]=="sim_StabilityTimRuleIEII_TIF":
        cl_str = generate_cl_str_StabilityTimRuleIEII_TIF(params)
    elif params["name"]=="sim_StabilityTimRule_singleneuron_TIF":
        cl_str = generate_cl_str_StabilityTimRule_singleneuron_TIF(params)
    elif params["name"]=="sim_TEST_TIFgroup_singleneuron":
        cl_str = generate_cl_str_TEST_TIFgroup_singleneuron(params)
    elif params["name"]=="sim_innerloop_bg_CVAIF_IE_T4wvceciPol":
        cl_str = generate_cl_str_bg_CVAIF_IE_T4wvceciPol(params)
    elif params["name"]=="sim_innerloop_bg_CVAIF_IE_T4wvceciMLP":
        cl_str = generate_cl_str_bg_CVAIF_IE_T4wvceciMLP(params)
    elif params["name"]=="sim_innerloop_ReluFamiliarityNet_Twvc":
        cl_str = generate_cl_str_ReluFamiliarityNet_Twvc(params)
    elif params["name"]=="sim_innerloop_DelayFamTask_CVAIF_EEIE_T4wvceciPol":
        cl_str = generate_cl_str_DelayFamTask_CVAIF_EEIE_T4wvceciPol(params)
    else:
        print('No call string function written for that innerloop name')
        print(params["name"])
        raise NotImplementedError
    
    # compile and simulation code if required
    if compile:
        if os.path.exists(params["auryn_sim_dir"] + params["name"]): #don't launch a sim on outdated code if compilation fails
            os.remove(params["auryn_sim_dir"] + params["name"]) 
        compile_str = "cd " + params["auryn_sim_dir"]
        compile_str += " && make " + params["name"]
        output1 = subprocess.run(compile_str, shell=True, capture_output=True)
    
    # run the network
    print(cl_str)
    start = time.time()
    output2 = subprocess.run(cl_str, shell=True, capture_output=True)
    exec_time = np.round(time.time() - start,3)

    # inform user
    return_str = ""

    if compile:
        return_str += "COMPILATION: \n \n Input: \n \n" + output1.args
        return_str += " \n \n Return: \n \n " + str(output1.stdout)[2:-1]
        return_str += " \n \n Potential errors: \n \n " + str(output1.stderr)[2:-1]
    else:
        return_str += "No compilation was demanded \n"
    
    return_str += " \n \nSIMULATION: \n \n Input: \n \n " + output2.args
    return_str += " \n \n Return: \n \n " + str(output2.stdout)[2:-1]
    return_str += " \n \n Potential errors: \n \n " + str(output2.stderr)[2:-1]
    return_str += " \n \n Simulation time: " + str(exec_time) + "s"
    return(return_str)

def generate_cl_str_bg_TIF_IE_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_bg_TIF_IE_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --lns " + str(args["lns"]) +\
                    " --ls " + str(args["ls"]) +\
                    " --target " + str(args["target"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --sparseness_poisson " + str(args["sparseness_poisson"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --poisson_rate " + str(args["poisson_rate"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --tau_checker " + str(args["tau_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_bg_TIF_EE_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_bg_TIF_EE_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --lns " + str(args["lns"]) +\
                    " --ls " + str(args["ls"]) +\
                    " --target " + str(args["target"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --sparseness_poisson " + str(args["sparseness_poisson"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --poisson_rate " + str(args["poisson_rate"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --tau_checker " + str(args["tau_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_bg_TIF_EI_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_bg_TIF_EI_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --lns " + str(args["lns"]) +\
                    " --ls " + str(args["ls"]) +\
                    " --target " + str(args["target"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --sparseness_poisson " + str(args["sparseness_poisson"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --poisson_rate " + str(args["poisson_rate"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --tau_checker " + str(args["tau_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_bg_TIF_II_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_bg_TIF_II_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --lns " + str(args["lns"]) +\
                    " --ls " + str(args["ls"]) +\
                    " --target " + str(args["target"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --sparseness_poisson " + str(args["sparseness_poisson"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --poisson_rate " + str(args["poisson_rate"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --tau_checker " + str(args["tau_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_IE_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_IE_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_EE_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_EE_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_EI_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_EI_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_II_6pPol(args):
    rule_str = " --rule a" + str(args['rule']['tau_pre']) + "a" + str(args['rule']['tau_post']) +\
               "a" + str(args['rule']['alpha']) +  "a" + str(args['rule']['beta']) + "a" + str(args['rule']['gamma']) +\
               "a" + str(args['rule']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_II_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_EEIE_6pPol(args):
    rule_str = " --ruleEE a" + str(args['ruleEE']['tau_pre']) + "a" + str(args['ruleEE']['tau_post']) +\
               "a" + str(args['ruleEE']['alpha']) +  "a" + str(args['ruleEE']['beta']) + "a" + str(args['ruleEE']['gamma']) +\
               "a" + str(args['ruleEE']['kappa']) + "a"
    rule_str += " --ruleIE a" + str(args['ruleIE']['tau_pre']) + "a" + str(args['ruleIE']['tau_post']) +\
               "a" + str(args['ruleIE']['alpha']) +  "a" + str(args['ruleIE']['beta']) + "a" + str(args['ruleIE']['gamma']) +\
               "a" + str(args['ruleIE']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_EEIE_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmaxee " + str(args["wmaxee"]) +\
                    " --wmaxie " + str(args["wmaxie"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_EEII_6pPol(args):
    rule_str = " --ruleEE a" + str(args['ruleEE']['tau_pre']) + "a" + str(args['ruleEE']['tau_post']) +\
               "a" + str(args['ruleEE']['alpha']) +  "a" + str(args['ruleEE']['beta']) + "a" + str(args['ruleEE']['gamma']) +\
               "a" + str(args['ruleEE']['kappa']) + "a"
    rule_str += " --ruleII a" + str(args['ruleII']['tau_pre']) + "a" + str(args['ruleII']['tau_post']) +\
               "a" + str(args['ruleII']['alpha']) +  "a" + str(args['ruleII']['beta']) + "a" + str(args['ruleII']['gamma']) +\
               "a" + str(args['ruleII']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_EEII_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmaxee " + str(args["wmaxee"]) +\
                    " --wmaxii " + str(args["wmaxii"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_EIIE_6pPol(args):
    rule_str = " --ruleEI a" + str(args['ruleEI']['tau_pre']) + "a" + str(args['ruleEI']['tau_post']) +\
               "a" + str(args['ruleEI']['alpha']) +  "a" + str(args['ruleEI']['beta']) + "a" + str(args['ruleEI']['gamma']) +\
               "a" + str(args['ruleEI']['kappa']) + "a"
    rule_str += " --ruleIE a" + str(args['ruleIE']['tau_pre']) + "a" + str(args['ruleIE']['tau_post']) +\
               "a" + str(args['ruleIE']['alpha']) +  "a" + str(args['ruleIE']['beta']) + "a" + str(args['ruleIE']['gamma']) +\
               "a" + str(args['ruleIE']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_EIIE_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmaxei " + str(args["wmaxei"]) +\
                    " --wmaxie " + str(args["wmaxie"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_FamDet_Lbasic_TIF_EEEI_6pPol(args):
    rule_str = " --ruleEE a" + str(args['ruleEE']['tau_pre']) + "a" + str(args['ruleEE']['tau_post']) +\
               "a" + str(args['ruleEE']['alpha']) +  "a" + str(args['ruleEE']['beta']) + "a" + str(args['ruleEE']['gamma']) +\
               "a" + str(args['ruleEE']['kappa']) + "a"
    rule_str += " --ruleEI a" + str(args['ruleEI']['tau_pre']) + "a" + str(args['ruleEI']['tau_post']) +\
               "a" + str(args['ruleEI']['alpha']) +  "a" + str(args['ruleEI']['beta']) + "a" + str(args['ruleEI']['gamma']) +\
               "a" + str(args['ruleEI']['kappa']) + "a"

    cl_str = args["auryn_sim_dir"] + "sim_innerloop_FamDet_Lbasic_TIF_EEEI_6pPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --eta " + str(args["eta"]) +\
                    rule_str +\
                    " --wmaxee " + str(args["wmaxee"]) +\
                    " --wmaxei " + str(args["wmaxei"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --l_train " + str(args["l_train"]) +\
                    " --l_break1 " + str(args["l_break1"]) +\
                    " --l_score " + str(args["l_score"]) +\
                    " --l_break2 " + str(args["l_break2"]) +\
                    " --rate_cut_fam " + str(args["rate_cut_fam"]) +\
                    " --rate_cut_nov " + str(args["rate_cut_nov"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --bg_input_rate " + str(args["bg_input_rate"]) +\
                    " --active_input_rate " + str(args["active_input_rate"]) +\
                    " --N_active_input " + str(args["N_active_input"]) +\
                    " --N_patterns " + str(args["N_patterns"]) +\
                    " --radius " + str(args["radius"]) +\
                    " --tau_checker_pop " + str(args["tau_checker_pop"]) +\
                    " --ontime_train " + str(args["ontime_train"]) +\
                    " --offtime_train " + str(args["offtime_train"]) +\
                    " --ontime_test " + str(args["ontime_test"]) +\
                    " --offtime_test " + str(args["offtime_test"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_bg_CVAIF_IE_T4wvceciPol(args):
    rule_str = " --rule a"
    for i in range(0, len(args["rule"])):
        rule_str += str(args["rule"][i])+"a"
   
    cl_str = args["auryn_sim_dir"] + "sim_innerloop_bg_CVAIF_IE_T4wvceciPol --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --lns " + str(args["lns"]) +\
                    " --ls " + str(args["ls"]) +\
                    " --target " + str(args["target"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --sparseness_poisson " + str(args["sparseness_poisson"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --poisson_rate " + str(args["poisson_rate"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --tau_checker " + str(args["tau_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def generate_cl_str_bg_CVAIF_IE_T4wvceciMLP(args):
    rule_str = make_rule_str(args['rule'], args['rule_cst_part'])
   
    cl_str = args["auryn_sim_dir"] + "sim_innerloop_bg_CVAIF_IE_T4wvceciMLP --ID " + str(args["id"]) +\
                    " --NE " + str(args["NE"]) +\
                    " --NI " + str(args["NI"]) +\
                    " --wee " + str(args["wee"]) +\
                    " --wei " + str(args["wei"]) +\
                    " --wie " + str(args["wie"]) +\
                    " --wii " + str(args["wii"]) +\
                    " --nh1 " + str(args["nh1"]) +\
                    " --nh2 " + str(args["nh2"]) +\
                    rule_str +\
                    " --wmax " + str(args["wmax"]) +\
                    " --sparseness " + str(args["sparseness"]) +\
                    " --lns " + str(args["lns"]) +\
                    " --ls " + str(args["ls"]) +\
                    " --target " + str(args["target"]) +\
                    " --N_inputs " + str(args["N_inputs"]) +\
                    " --sparseness_poisson " + str(args["sparseness_poisson"]) +\
                    " --w_poisson " + str(args["w_poisson"]) +\
                    " --poisson_rate " + str(args["poisson_rate"]) +\
                    " --min_rate_checker " + str(args["min_rate_checker"]) +\
                    " --max_rate_checker " + str(args["max_rate_checker"]) +\
                    " --tau_checker " + str(args["tau_checker"]) +\
                    " --workdir " + str(args["workdir"])
    return(cl_str)

def make_rule_str(rule, rule_cst):
    """
    here we only learn the learning rate and the final layer of the MLPs.
    we assume rule is such that: [eta, Wpre (nh2+1 params), Wpost (nh2 + 1 params)]
    """
    rule_str = " --rule a"+str(rule[0])+"a"
    for j in rule_cst:
        rule_str += str(j)+"a"
    for i in range(1, len(rule)):
        rule_str += str(rule[i])+"a"
    return(rule_str)

#######################
# ANALYSIS OF RESULTS #
#######################

################## for plotting meta-optimization

def plot_parameters_6pPol(r_hist, dpi=600, figsize = (3,1.5), linewidth=2, colors=["black", "black", "black", "black"], alpha=0.9, font='Arial',
        fontsize=10, xpad=10, ylabel1=None, ylabel2=None, s=8, logy1=False, y1_ticklabels=None, plot_point=None,
        x_label=None, x_lim=None, x_ticks=None, y1_ticks=None, y1_lim=None, y2_ticks=None, y2_lim=None,
                         bbox_to_anchor_left=(-0.5, 0), labelspacing_left=0.5, axwidth=1.5,
                         bbox_to_anchor_right=(-0.5, 0), labelspacing_right=0.5):
    orange = '#d95f02'
    blue = '#7570b3'
    n_meta_it = len(r_hist)
    fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)
    
    ax1.plot(r_hist[:,2], label = r'$\alpha$', linewidth = linewidth, color = '#625D5D', alpha = alpha,zorder = 0.1)
    ax1.plot(r_hist[:,3], label = r'$\beta$', linewidth = linewidth, color = '#009B77', alpha = alpha,zorder = 0.2)
    ax1.plot(r_hist[:,4], label = r'$\gamma$', linewidth = linewidth, color = '#fdb462', alpha = alpha,zorder = 0.3)
    ax1.plot(r_hist[:,5], label = r'$\kappa$', linewidth = linewidth, color = '#B565A7', alpha = alpha,zorder = 0.4)
    
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_linewidth(axwidth)
    ax1.spines['left'].set_linewidth(axwidth)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    if x_ticks is not None:
        ax1.set_xticks(x_ticks)
    if y1_ticklabels is not None:
        ax1.set_yticklabels(y1_ticklabels)
    if x_lim is not None:
        ax1.set_xlim(x_lim)
    if y1_ticks is not None:
        ax1.set_yticks(y1_ticks)
    if y1_lim is not None:
        ax1.set_ylim(y1_lim)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*linewidth)
    ax1.tick_params(axis='x', which='major', pad=xpad)
    ax1.set_ylabel(ylabel1, color=colors[0], fontsize=fontsize)
    ax1.set_xlabel(x_label, fontsize=fontsize)
    # ax1.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
    #           bbox_to_anchor=bbox_to_anchor_left,ncol=1, \
    #           handlelength=0.6, handletextpad = 0.3, labelspacing=labelspacing_left)
    
    ax2 = ax1.twinx()
    ax2.plot(1000*np.exp(r_hist[:,0]), label = r'$\tau_{pre}$', linestyle=(0, (1, 0.5)), linewidth = linewidth, color = orange, alpha = alpha,zorder = 0.6)
    ax2.plot(1000*np.exp(r_hist[:,1]), label = r'$\tau_{post}$', linestyle=(0, (1, 0.5)), linewidth = linewidth, color = blue, alpha = alpha,zorder = 0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['right'].set_linewidth(axwidth)
    if y2_ticks is not None:
        ax2.set_yticks(y2_ticks)
    if y2_lim is not None:
        ax2.set_ylim(y2_lim)
    ax2.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    ax2.set_ylabel(ylabel2, color=colors[1], fontsize=fontsize)
    # ax2.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
    #           bbox_to_anchor=bbox_to_anchor_right,ncol=1, \
    #           handlelength=0.6, handletextpad = 0.3, labelspacing = labelspacing_right)
    ax2.spines['right'].set_linestyle((0,(0.4,1.4)))
    # ax2.spines['right'].set_color("gray")
    
    # ax1.set_zorder(ax2.get_zorder()+1)
    ax2.set_zorder(ax1.get_zorder()+1)
    ax1.patch.set_visible(False)
    
    ax1.plot([x_lim[1], x_lim[1]], y2_lim, color="white", linewidth=1*axwidth)
    ax2.plot([x_lim[1], x_lim[1]], y2_lim, color="white", linewidth=1*axwidth)
    ax2.plot([x_lim[0], x_lim[0]], y2_lim, color="black", linewidth=1*axwidth)

    ax1.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
            bbox_to_anchor=bbox_to_anchor_left,ncol=4,\
            handlelength=0.6, handletextpad = 0.3, borderpad=0, columnspacing=labelspacing_left)
    ax2.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
              bbox_to_anchor=bbox_to_anchor_right,ncol=2, \
              handlelength=0.6, handletextpad = 0.3, columnspacing=labelspacing_right, borderpad=0)

    # ax1.set_clip_on(False)
    
    plt.show()

def plot_loss(loss_hist, figsize=(2.5, 1.5), dpi=600, fontsize = 22, linewidth = 3, font = 'Arial', alpha = 1,
              xlabelpad=-5, xlim=None, xticks=None, color = '#8C001A', ylim=None, yticks=None):
    n_meta_it = len(loss_hist)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.semilogy(loss_hist, linewidth = linewidth, color =color, alpha = alpha)
    ax.set_xlabel('meta-iterations', fontsize=fontsize, fontname=font, labelpad = xlabelpad)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)
    ax.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax.tick_params(which = 'minor', width=0, labelsize=0, length=0)
    if yticks is None:
        ax.set_yticks([1e-2,1,100])
    else:
        ax.set_yticks(yticks)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.set_ylabel(r'$L$', fontsize=fontsize, fontname=font, labelpad = -6)
    if xlim is not None:
        ax.set_xlim(xlim)
    else:
        ax.set_xlim([0,n_meta_it])
    if xticks is not None:
        ax.set_xticks(xticks)
    else:
        ax.set_xticks([0,int(n_meta_it/2), n_meta_it])
    plt.show()

def plot_rule(thetas=None, n_bins=1000,
              x_lim=[0,1], logx=False, logy=False, x_label="", ax=None, 
              color=None, save_path=None, linewidth=3, fontsize=20, figsize=(5,3), font="arial",
              x_ticks=None, x_ticklabels=None, rotation=0, y_label=None,
              y_lim=None, y_ticks=None, y_ticklabels=None, axwidth=3, labelpad_xlabel=30,
              labelpad_ylabel=-40, dpi=200, xticks_pad=None, yticks_pad=None, color_ylabel='black'):

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    ts = np.linspace(x_lim[0], x_lim[1],num=n_bins)
    ind_t_pos = 0
    while ts[ind_t_pos] < 0:
        ind_t_pos += 1
    
    dws = np.array([thetas[2] + thetas[3] + thetas[5]*np.exp(-np.abs(ts[i])/thetas[1]) for i in range(ind_t_pos)])
    dws = np.append(dws, np.array([thetas[2] + thetas[3] + thetas[4]*np.exp(-np.abs(ts[i])/thetas[0]) for i in range(ind_t_pos, len(ts))]), axis=0)


    ax.plot(ts, dws, color=color, 
            linewidth=linewidth)
        
    # if logx:
    #     ax.set_xscale('log')
    #     ax.tick_params(axis='x', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    
    if x_lim is not None:
        ax.set_xlim(x_lim)
    if x_ticks is not None:
        ax.set_xticks(x_ticks)
    if x_ticklabels is not None:
        ax.set_xticklabels(x_ticklabels, rotation = rotation)
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=fontsize, fontname=font, labelpad = labelpad_xlabel)
    
    if y_lim is not None:
        ax.set_ylim([y_lim[0], y_lim[1]])
        ax.set_yticks([y_lim[0], y_lim[1]])
    if y_ticks is not None:
        ax.set_yticks(y_ticks)
    if y_ticklabels is not None:
        ax.set_yticklabels(y_ticklabels)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=fontsize, fontname=font, labelpad=labelpad_ylabel, color=color_ylabel)

    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(axwidth)
    ax.spines['left'].set_linewidth(axwidth)
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_position('zero')

    ax.tick_params(axis='x', width=axwidth, labelsize=fontsize, length=2*axwidth, pad=xticks_pad)
    ax.tick_params(axis='y', width=axwidth, labelsize=fontsize, length=2*axwidth, pad=yticks_pad)
    # ax.tick_params(axis='y', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    plt.show()

def plot_PearsonMat_6Pol(PearsonMat, save=False, name="",
                    linewidth=1.5,
                    fontsize = 10,
                    font="Arial",
                    figsize=(3,3),
                    color=None):
    fig, ax = plt.subplots(figsize=figsize, dpi=600)
    matrice = ax.imshow(PearsonMat, vmin=-1, vmax=1, cmap=plt.get_cmap('BrBG')) #spectral Spectral copper
    ax.spines['top'].set_linewidth(linewidth)
    ax.spines['right'].set_linewidth(linewidth)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)
    ax.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax.set_xticks([0,1,2,3,4,5])
    ax.set_yticks([0,1,2,3,4,5])
    ax.set_yticklabels([r'$\tau_{pre}$',r'$\tau_{post}$',r'$\alpha$',r'$\beta$',r'$\gamma$', r'$\kappa$'])
    ax.set_xticklabels([r'$\tau_{pre}$',"\n"+r'$\tau_{post}$',
                        r'$\alpha$',"\n"+r'$\beta$',
                        r'$\gamma$',"\n"+r'$\kappa$'])
    ax.tick_params(axis='x', which='major', pad=0)

    for i in range(6):
        plt.gca().get_xticklabels()[i].set_color(color)
        plt.gca().get_yticklabels()[i].set_color(color)
#     ax.set_yticks([])
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="10%", pad=0.05)
    
    cbar = fig.colorbar(matrice, cax = cax, drawedges=False)
    cbar.outline.set_color('black')
    cbar.outline.set_linewidth(linewidth)
    cbar.ax.tick_params(labelsize=fontsize, width=linewidth, length=2*linewidth)
    
    if save:
        name_save = name + ".png"
        fig.savefig(name_save, format='png', dpi=800, bbox_inches='tight')
    
    plt.show()

def compute_PearsonMat(Cov):
    n_params = len(Cov)
    PearsonMat = np.ones((n_params, n_params))
    sigmas = [np.sqrt(Cov[i,i]) for i in range(n_params)]
    #diagonal elements are all ones, all good
    for i in range(n_params):
        for j in range(i+1,n_params):
            PearsonMat[i,j] = Cov[i, j]/sigmas[i]/sigmas[j]
            PearsonMat[j,i] = Cov[i, j]/sigmas[i]/sigmas[j]
    return(PearsonMat)

def plot_parameters_2x6pPol(r_hist, dpi=600, figsize = (3,1.5), linewidth=2, colors=["black", "black", "black", "black"], alpha=0.9, font='Arial',
        fontsize=10, xpad=10, ylabel1=None, ylabel2=None, s=8, logy1=False, y1_ticklabels=None, plot_point=None,
        x_label=None, x_lim=None, x_ticks=None, y1_ticks=None, y1_lim=None, y2_ticks=None, y2_lim=None,
                         bbox_to_anchor_left=(-0.5, 0), labelspacing_left=0.5, axwidth=1.5,
                         bbox_to_anchor_right=(-0.5, 0), labelspacing_right=0.5):
    orange = '#d95f02'
    blue = '#7570b3'
    n_meta_it = len(r_hist)
    fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)
    
    ax1.plot(r_hist[:,8], label = r'$\alpha$', linewidth = linewidth, color = '#625D5D', alpha = alpha,zorder = 0.1)
    ax1.plot(r_hist[:,9], label = r'$\beta$', linewidth = linewidth, color = '#009B77', alpha = alpha,zorder = 0.2)
    ax1.plot(r_hist[:,10], label = r'$\gamma$', linewidth = linewidth, color = '#fdb462', alpha = alpha,zorder = 0.3)
    ax1.plot(r_hist[:,11], label = r'$\kappa$', linewidth = linewidth, color = '#B565A7', alpha = alpha,zorder = 0.4)
    
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_linewidth(axwidth)
    ax1.spines['left'].set_linewidth(axwidth)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    if x_ticks is not None:
        ax1.set_xticks(x_ticks)
    if y1_ticklabels is not None:
        ax1.set_yticklabels(y1_ticklabels)
    if x_lim is not None:
        ax1.set_xlim(x_lim)
    if y1_ticks is not None:
        ax1.set_yticks(y1_ticks)
    if y1_lim is not None:
        ax1.set_ylim(y1_lim)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*linewidth)
    ax1.tick_params(axis='x', which='major', pad=xpad)
    ax1.set_ylabel(ylabel1, color=colors[0], fontsize=fontsize)
    ax1.set_xlabel(x_label, fontsize=fontsize)
    # ax1.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
    #           bbox_to_anchor=bbox_to_anchor_left,ncol=1, \
    #           handlelength=0.6, handletextpad = 0.3, labelspacing=labelspacing_left)
    
    ax2 = ax1.twinx()
    ax2.plot(1000*np.exp(r_hist[:,6]), label = r'$\tau_{pre}$', linestyle=(0, (1, 0.5)), linewidth = linewidth, color = orange, alpha = alpha,zorder = 0.6)
    ax2.plot(1000*np.exp(r_hist[:,7]), label = r'$\tau_{post}$', linestyle=(0, (1, 0.5)), linewidth = linewidth, color = blue, alpha = alpha,zorder = 0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['right'].set_linewidth(axwidth)
    if y2_ticks is not None:
        ax2.set_yticks(y2_ticks)
    if y2_lim is not None:
        ax2.set_ylim(y2_lim)
    ax2.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    ax2.set_ylabel(ylabel2, color=colors[1], fontsize=fontsize)
    # ax2.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
    #           bbox_to_anchor=bbox_to_anchor_right,ncol=1, \
    #           handlelength=0.6, handletextpad = 0.3, labelspacing = labelspacing_right)
    ax2.spines['right'].set_linestyle((0,(0.4,1.4)))
    # ax2.spines['right'].set_color("gray")
    
    # ax1.set_zorder(ax2.get_zorder()+1)
    ax2.set_zorder(ax1.get_zorder()+1)
    ax1.patch.set_visible(False)
    
    ax1.plot([x_lim[1], x_lim[1]], y2_lim, color="white", linewidth=1*axwidth)
    ax2.plot([x_lim[1], x_lim[1]], y2_lim, color="white", linewidth=1*axwidth)
    ax2.plot([x_lim[0], x_lim[0]], y2_lim, color="black", linewidth=1*axwidth)

    ax1.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
            bbox_to_anchor=bbox_to_anchor_left,ncol=4,\
            handlelength=0.6, handletextpad = 0.3, borderpad=0, columnspacing=labelspacing_left)
    ax2.legend(prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
              bbox_to_anchor=bbox_to_anchor_right,ncol=2, \
              handlelength=0.6, handletextpad = 0.3, columnspacing=labelspacing_right, borderpad=0)

    # ax1.set_clip_on(False)
    
    plt.show()

def plot_PearsonMat_2x6Pol(PearsonMat, save=False, name="",
                    linewidth=1.5,
                    fontsize = 10,
                    font="Arial",
                    figsize=(3,3),
                    color1=None,
                    color2=None):
    fig, ax = plt.subplots(figsize=figsize, dpi=600)
    matrice = ax.imshow(PearsonMat, vmin=-1, vmax=1, cmap=plt.get_cmap('BrBG')) #spectral Spectral copper
    ax.spines['top'].set_linewidth(linewidth)
    ax.spines['right'].set_linewidth(linewidth)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)
    ax.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11])
    ax.set_yticks([0,1,2,3,4,5,6,7,8,9,10,11])
    labelsy = [r'$\tau_{pre}$',r'$\tau_{post}$',
              r'$\alpha$',r'$\beta$',
              r'$\gamma$', r'$\kappa$',
              r'$\tau_{pre}$',r'$\tau_{post}$',
              r'$\alpha$',r'$\beta$',
              r'$\gamma$', r'$\kappa$']
    labelsx = [r'$\tau_{pre}$',"\n"+r'$\tau_{post}$',
              r'$\alpha$',"\n"+r'$\beta$',
              r'$\gamma$', "\n"+r'$\kappa$',
              r'$\tau_{pre}$',"\n"+r'$\tau_{post}$',
              r'$\alpha$',"\n"+r'$\beta$',
              r'$\gamma$', "\n"+r'$\kappa$']
    ax.set_xticklabels(labelsx)
    ax.tick_params(axis='x', which='major', pad=0)

    ax.set_yticklabels(labelsy)

    colors = [color1, color2]
    colors = np.repeat(colors, 6, axis=0)

    for i in range(12):
        plt.gca().get_xticklabels()[i].set_color(colors[i])
        plt.gca().get_yticklabels()[i].set_color(colors[i])
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    
    cbar = fig.colorbar(matrice, cax = cax, drawedges=False)
    cbar.outline.set_color('black')
    cbar.outline.set_linewidth(linewidth)
    cbar.set_ticks([-1,0,1])
    cbar.ax.tick_params(labelsize=fontsize, width=linewidth, length=2*linewidth)
    
    if save:
        name_save = name + ".png"
        fig.savefig(name_save, format='png', dpi=800, bbox_inches='tight')
    
    plt.show()

def plot_parameters_MLP(r_hist, dpi=600, figsize = (3,1.5), linewidth=2, colors=["black", "black", "black"], alpha=0.9, font='Arial',
        fontsize=10, xpad=10, ylabel1=None, y1_ticklabels=None, columnspacing=1,
        x_label=None, x_lim=None, x_ticks=None, y1_ticks=None, y1_lim=None,
        bbox_to_anchor_left=(-0.5, 0), labelspacing_left=0.5, axwidth=1.5,):
    orange = '#d95f02'
    blue = '#7570b3'
    n_meta_it = len(r_hist)
    fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)
    
    a, = ax1.plot(r_hist[:,0], label = r'$\eta$', linewidth = linewidth, color = colors[0], alpha = alpha,zorder = 0.3)

    for i in range(5):
        b, = ax1.plot(r_hist[:,i+1], label = r'$\theta_{on\ pre}$', linewidth = linewidth, color=colors[1], alpha = alpha,zorder = 0.1)
        c, = ax1.plot(r_hist[:,i+6], label = r'$\theta_{on\ post}$', linewidth = linewidth, color=colors[2], alpha = alpha,zorder = 0.1)


    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_linewidth(axwidth)
    ax1.spines['left'].set_linewidth(axwidth)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    if x_ticks is not None:
        ax1.set_xticks(x_ticks)
    if y1_ticklabels is not None:
        ax1.set_yticklabels(y1_ticklabels)
    if x_lim is not None:
        ax1.set_xlim(x_lim)
    if y1_ticks is not None:
        ax1.set_yticks(y1_ticks)
    if y1_lim is not None:
        ax1.set_ylim(y1_lim)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*linewidth)
    ax1.tick_params(axis='x', which='major', pad=xpad)
    ax1.set_ylabel(ylabel1, color=colors[0], fontsize=fontsize)
    ax1.set_xlabel(x_label, fontsize=fontsize, labelpad=0)
    ax1.legend(handles=[a,b, c], prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
              bbox_to_anchor=bbox_to_anchor_left,ncol=3, columnspacing=columnspacing,
              handlelength=0.6, handletextpad = 0.3, labelspacing=labelspacing_left)
    plt.show()

def plot_PearsonMat_BigPoly(PearsonMat, save=False, name="",
                    linewidth=1.5,
                    fontsize = 10,
                    font="Arial",
                    figsize=(3,3),
                    color=None):
    fig, ax = plt.subplots(figsize=figsize, dpi=600)
    matrice = ax.imshow(PearsonMat, vmin=-1, vmax=1, cmap=plt.get_cmap('BrBG')) #spectral Spectral copper
    ax.spines['top'].set_linewidth(linewidth)
    ax.spines['right'].set_linewidth(linewidth)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)
    # ax.tick_params(width=linewidth, labelsize=fontsize, length=2*linewidth)
    ax.set_xticks([])
    ax.set_yticks([])
    # labelsy = [r'$\tau_{pre}$',r'$\tau_{post}$',
    #           r'$\alpha$',r'$\beta$',
    #           r'$\gamma$', r'$\kappa$',
    #           r'$\tau_{pre}$',r'$\tau_{post}$',
    #           r'$\alpha$',r'$\beta$',
    #           r'$\gamma$', r'$\kappa$']
    # labelsx = [r'$\tau_{pre}$',"\n"+r'$\tau_{post}$',
    #           r'$\alpha$',"\n"+r'$\beta$',
    #           r'$\gamma$', "\n"+r'$\kappa$',
    #           r'$\tau_{pre}$',"\n"+r'$\tau_{post}$',
    #           r'$\alpha$',"\n"+r'$\beta$',
    #           r'$\gamma$', "\n"+r'$\kappa$']
    # ax.set_xticklabels(labelsx)
    # ax.tick_params(axis='x', which='major', pad=0)

    # ax.set_yticklabels(labelsy)

    # for i in range(21):
    #     plt.gca().get_xticklabels()[i].set_color(color)
    #     plt.gca().get_yticklabels()[i].set_color(color)
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    
    cbar = fig.colorbar(matrice, cax = cax, drawedges=False)
    cbar.outline.set_color('black')
    cbar.outline.set_linewidth(linewidth)
    cbar.set_ticks([-1,0,1])
    cbar.ax.tick_params(labelsize=fontsize, width=linewidth, length=2*linewidth)
    
    # if save:
    #     name_save = name + ".png"
    #     fig.savefig(name_save, format='png', dpi=800, bbox_inches='tight')
    
    plt.show()

def plot_parameters_BigPoly(r_hist, dpi=600, figsize = (3,1.5), linewidth=2, cmap=plt.cm.jet, alpha=0.9, font='Arial',
        fontsize=10, xpad=10, xlabel_pad=0, ylabel_pad=0, ylabel=None, y_ticklabels=None, columnspacing=1,
        x_label=None, x_lim=None, x_ticks=None, y_ticks=None, y_lim=None,
        bbox_to_anchor_left=(-0.5, 0), labelspacing_left=0.5, axwidth=1.5,):
    fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)


    colors = cmap(np.linspace(0,1,21))


    for i in range(21):
        a, = ax1.plot(r_hist[:,i], linewidth = linewidth, color=colors[i], alpha = alpha,zorder = 0.1)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_linewidth(axwidth)
    ax1.spines['left'].set_linewidth(axwidth)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    if x_ticks is not None:
        ax1.set_xticks(x_ticks)
    if y_ticklabels is not None:
        ax1.set_yticklabels(y_ticklabels)
    if x_lim is not None:
        ax1.set_xlim(x_lim)
    if y_ticks is not None:
        ax1.set_yticks(y_ticks)
    if y_lim is not None:
        ax1.set_ylim(y_lim)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*linewidth)
    ax1.tick_params(axis='x', which='major', pad=xpad)
    ax1.set_ylabel(ylabel, color="black", fontsize=fontsize, labelpad=ylabel_pad)
    ax1.set_xlabel(x_label, fontsize=fontsize, labelpad=xlabel_pad)
    # ax1.legend(handles=[a,b], prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
    #           bbox_to_anchor=bbox_to_anchor_left,ncol=3, columnspacing=columnspacing,
    #           handlelength=0.6, handletextpad = 0.3, labelspacing=labelspacing_left)
    plt.show()

def plot_parameters_VintagePoly(r_hist, dpi=600, figsize = (3,1.5), linewidth=2, cmap=plt.cm.jet, alpha=0.9, font='Arial',
        fontsize=10, xpad=10, ylabel1=None, y1_ticklabels=None, columnspacing=1,
        x_label=None, x_lim=None, x_ticks=None, y1_ticks=None, y1_lim=None,
        bbox_to_anchor_left=(-0.5, 0), labelspacing_left=0.5, axwidth=1.5,):
    fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)

    lr = 72
    n_meta_it = len(r_hist)//lr

    colors = cmap(np.linspace(0,1,lr))

    for i in range(72):
        inds = [j*lr + i for j in range(n_meta_it)]
        a, = ax1.plot( r_hist[inds], linewidth = linewidth, color=colors[i], zorder = 0.1)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_linewidth(axwidth)
    ax1.spines['left'].set_linewidth(axwidth)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    if x_ticks is not None:
        ax1.set_xticks(x_ticks)
    if y1_ticklabels is not None:
        ax1.set_yticklabels(y1_ticklabels)
    if x_lim is not None:
        ax1.set_xlim(x_lim)
    if y1_ticks is not None:
        ax1.set_yticks(y1_ticks)
    if y1_lim is not None:
        ax1.set_ylim(y1_lim)
    ax1.tick_params(width=axwidth, labelsize=fontsize, length=2*linewidth)
    ax1.tick_params(axis='x', which='major', pad=xpad)
    ax1.set_ylabel(ylabel1, color=colors[0], fontsize=fontsize)
    ax1.set_xlabel(x_label, fontsize=fontsize)
    # ax1.legend(handles=[a,b, c, d], prop={'family':font, 'size':fontsize}, loc = 'lower left', frameon=False, \
    #           bbox_to_anchor=bbox_to_anchor_left,ncol=2, columnspacing=columnspacing,
    #           handlelength=0.6, handletextpad = 0.3, labelspacing=labelspacing_left)
    plt.show()


################## for plotting spiking simulations

def get_spiketimes_auryn(filename, n_neurons):
    """
    assumes filename is a .ras file generated by auryn (spike monitor).
    will extract spiketimes and return a dic: key=neuron_num value=np.array(float) spiketimes in seconds
    """
    spiketimes = dict()
    for neuron in range(n_neurons):
        spiketimes[str(neuron)] = []
    f = open(filename, 'r')
    lines = f.readlines()
    for line in lines:
        aux = line.split(" ")
        spiketimes[str(int(aux[1]))].append(float(aux[0]))
    for neuron in range(n_neurons):
        spiketimes[str(neuron)] = np.array(spiketimes[str(neuron)])
    return(spiketimes)

def get_weights_auryn(filename, bin_size="default"):
    f = open(filename, "r")
    lines = f.readlines()
    n_neurons = len(lines[0].split(" "))-2
    n_ts = len(lines)
    
    #get the binning at which the weights were recorded
    if n_ts<2:
        raise Exception("not enough weights in the input file")
    else:
        orig_bin_size = float(lines[1].split(" ")[0]) - float(lines[0].split(" ")[0])
    
    #extract the weights at the recording bin_size
    if bin_size == "default":
        ts = np.zeros(n_ts)
        weights = np.zeros((n_neurons, n_ts))
        for i in range(n_ts):
            aux_ar = np.array(lines[i].split(" ")[:-1]).astype(float)
            ts[i] = aux_ar[0]
            weights[:,i] = aux_ar[1:]
    
    #if we want a specific binning of the timepoints
    else:
        #check that this binning is legit
        if bin_size < orig_bin_size:
            raise ValueError('bin size is smaller than the recording')
        t_start = float(lines[0].split(" ")[0])
        t_stop = float(lines[-1].split(" ")[0])
        ts = np.arange(t_start, t_stop, bin_size)
        weights = np.zeros((n_neurons, len(ts)))
        current_ts_index = 0
        for i in range(n_ts):
            t = float(lines[i].split(" ")[0])
            if t >= ts[current_ts_index]:
                weights[:,current_ts_index] = np.array(lines[i].split(" ")[1:-1]).astype(float)
                current_ts_index += 1
                if current_ts_index == len(ts):
                    break
                    
    w_dict = dict()
    w_dict['t'] = ts
    w_dict['w'] = weights
    return(w_dict)

def get_pop_rate_square_window(spiketimes=None, t_start=None, t_stop=None, window_size=None, n_neurons=None):
    ts = np.arange(t_start, t_stop, window_size)
    rates = np.zeros((n_neurons, len(ts)-1)) 
    for neuron in range(n_neurons):
        inds_insert = np.searchsorted(spiketimes[str(neuron)], ts, side='left', sorter=None)
        rates[neuron] = np.diff(inds_insert)
    
    pop_rate = np.zeros(len(ts)-1)
    for i in range(len(ts)-1):
        pop_rate[i] = np.mean(rates[:,i])
    return(ts[:-1], pop_rate/window_size)

def plot_simulation_2x6pPol_FamDet(sts_inp=None, sts_e=None, sts_i=None, n_to_plot_raster=None, 
                            n_exc=4096, n_inh=1024, n_input=5000, w1=None, w2=None, t_start=None, t_stop=None,
                            window_pop_rate=0.1, axwidth=4, linewidth=4, n_to_plot_weights=100, 
                            ms_raster_inp=0.5, ms_raster_e=0.5, ms_raster_i=0.5,
                            fontsize=20, figsize=(5, 2), font = "arial",
                            color_inp=None, color_exc=None, color_inh=None, color_w1=None, color_w2=None,
                            x_ticks=None, x_ticklabels=None, x_label=None, alpha_w=None, xlim=None,
                            linewidth_weights=0.5, y_label_w1 = r'$w^{E\to E}_{ij}$', y_label_w2 = r'$w^{I\to E}_{ij}$',
                            y_ticks_w1=None, y_ticklabels_w1=None, y_lim_w1=None,
                            y_ticks_w2=None, y_ticklabels_w2=None, y_lim_w2=None,
                            y_ticks_pop_rate=None, y_lim_pop_rate=None):
    
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6,1,figsize=figsize, constrained_layout=True, dpi=600, 
                                                  gridspec_kw={'height_ratios': [1.5, 1.5, 1.5, 1.2, 1.2, 1.2]})
    
    for ct, neuron_num in enumerate(np.linspace(0, n_input-1, num=n_to_plot_raster, dtype=int)):
        ax1.scatter(sts_inp[str(neuron_num)], np.full(len(sts_inp[str(neuron_num)]), ct),
                    linewidths=0, color=color_inp, s=ms_raster_inp, edgecolors=None, marker='o')
    if xlim is None:
        ax1.set_xlim([t_start, t_stop])
    else:
        ax1.set_xlim(xlim)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_ylabel("Inputs", fontsize=fontsize, fontname=font)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)

    for ct, neuron_num in enumerate(np.linspace(0, n_exc-1, num=n_to_plot_raster, dtype=int)):
        ax2.scatter(sts_e[str(neuron_num)], np.full(len(sts_e[str(neuron_num)]), ct), linewidths=0, 
                    color=color_exc, s=ms_raster_e, edgecolors=None, marker='o')
    if xlim is None:
        ax2.set_xlim([t_start, t_stop])
    else:
        ax2.set_xlim(xlim)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_ylabel("Exc", fontsize=fontsize, fontname=font)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    for ct, neuron_num in enumerate(np.linspace(0, n_inh-1, num=n_to_plot_raster, dtype=int)):
        ax3.scatter(sts_i[str(neuron_num)], np.full(len(sts_i[str(neuron_num)]), ct), linewidths=0,
                    color=color_inh, s=ms_raster_i, edgecolors=None, marker='o')
    if xlim is None:
        ax3.set_xlim([t_start, t_stop])
    else:
        ax3.set_xlim(xlim)
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_ylabel("Inh", fontsize=fontsize, fontname=font)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    
    ts, pop_rate = get_pop_rate_square_window(spiketimes=sts_e,t_start=t_start, t_stop=t_stop,
                                              window_size=window_pop_rate,n_neurons=n_exc)
    ax4.plot(ts, pop_rate, color=color_exc, linewidth=linewidth, marker='')
    if xlim is None:
        ax4.set_xlim([t_start, t_stop])
    else:
        ax4.set_xlim(xlim)
    ax4.set_xticks(x_ticks)
    ax4.set_xticklabels(["" for i in range(len(x_ticks))])
    ax4.set_ylabel(r'$\langle r_{i}^{exc} \rangle$' + "\n(Hz)", fontsize=fontsize, fontname=font)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['bottom'].set_linewidth(axwidth)
    ax4.spines['left'].set_linewidth(axwidth)
    ax4.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    ax4.set_yticks(y_ticks_pop_rate)
    ax4.set_ylim(y_lim_pop_rate)

    for syn_num in range(n_to_plot_weights):
        ax5.plot(w1['t'], w1['w'][syn_num, :], color=color_w1, linewidth=linewidth_weights, alpha=alpha_w)
    ax5.plot(w1['t'], np.mean(w1['w'], axis=0), color=color_w1, linewidth=linewidth, alpha=1)
    ax5.set_ylabel(y_label_w1, fontsize=fontsize, fontname=font)
    # ax5.set_yscale('log')
    # ax5.tick_params(axis='y', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    if xlim is None:
        ax5.set_xlim([t_start, t_stop])
    else:
        ax5.set_xlim(xlim)
    if y_lim_w1 is not None:
        ax5.set_ylim(y_lim_w1)
    if y_ticks_w1 is not None:
        ax5.set_yticks(y_ticks_w1)
    if y_ticklabels_w1 is not None:
        ax5.set_yticklabels(y_ticklabels_w1)
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    ax5.spines['bottom'].set_linewidth(axwidth)
    ax5.spines['left'].set_linewidth(axwidth)
    ax5.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    ax5.set_xticklabels(["" for i in range(len(x_ticks))])

    for syn_num in range(n_to_plot_weights):
        ax6.plot(w2['t'], w2['w'][syn_num, :], color=color_w2, linewidth=linewidth_weights, alpha=alpha_w)
    ax6.plot(w2['t'], np.mean(w2['w'], axis=0), color=color_w2, linewidth=linewidth, alpha=1)
    ax6.set_ylabel(y_label_w2, fontsize=fontsize, fontname=font)
    # ax6.set_yscale('log')
    # ax6.tick_params(axis='y', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    if xlim is None:
        ax6.set_xlim([t_start, t_stop])
    else:
        ax6.set_xlim(xlim)
    if y_lim_w2 is not None:
        ax6.set_ylim(y_lim_w2)
    if y_ticks_w2 is not None:
        ax6.set_yticks(y_ticks_w2)
    if y_ticklabels_w2 is not None:
        ax6.set_yticklabels(y_ticklabels_w2)
    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)
    ax6.spines['bottom'].set_linewidth(axwidth)
    ax6.spines['left'].set_linewidth(axwidth)
    ax6.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    # ax6.tick_params(axis='y', which="minor", width=0.5*axwidth, labelsize=0, labelcolor='w', length=1*axwidth)
    ax6.set_xticks(x_ticks)
    ax6.set_xlabel(x_label, fontsize=fontsize, fontname=font, labelpad = 0)

def plot_simulation_6pPol_bg(sts_e=None, sts_i=None, n_to_plot_raster=None, 
                            n_exc=4096, n_inh=1024, n_input=5000, wie=None, t_start=None, t_stop=None,
                            window_pop_rate=0.1, axwidth=4, linewidth=4, n_to_plot_weights=100, ms_raster=0.5,
                            fontsize=20, figsize=(5, 2), font = "arial",
                            color_inp=None, color_exc=None, color_inh=None, color_ie=None,
                            x_ticks=None, x_ticklabels=None, x_label=None, alpha_w=None, xlim=None,
                            linewidth_weights=0.5,
                            y_ticks_wi=None, y_ticklabels_wi=None, y_lim_wi=None,
                            y_ticks_pop_rate=None, y_lim_pop_rate=None, label_ws=r'$w^{I\to E}_{ij}$'):
    
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,figsize=figsize, constrained_layout=True, dpi=600, 
                                                  gridspec_kw={'height_ratios': [1.5, 1.5, 1.2, 1.2]})
    

    for ct, neuron_num in enumerate(np.linspace(0, n_exc-1, num=n_to_plot_raster, dtype=int)):
        ax1.scatter(sts_e[str(neuron_num)], np.full(len(sts_e[str(neuron_num)]), ct), linewidths=0, 
                    color=color_exc, s=ms_raster, edgecolors=None, marker='o')
    if xlim is None:
        ax1.set_xlim([t_start, t_stop])
    else:
        ax1.set_xlim(xlim)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_ylabel("Exc", fontsize=fontsize, fontname=font)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    for ct, neuron_num in enumerate(np.linspace(0, n_inh-1, num=n_to_plot_raster, dtype=int)):
        ax2.scatter(sts_i[str(neuron_num)], np.full(len(sts_i[str(neuron_num)]), ct), linewidths=0,
                    color=color_inh, s=ms_raster, edgecolors=None, marker='o')
    if xlim is None:
        ax2.set_xlim([t_start, t_stop])
    else:
        ax2.set_xlim(xlim)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_ylabel("Inh", fontsize=fontsize, fontname=font)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    ts, pop_rate = get_pop_rate_square_window(spiketimes=sts_e,t_start=t_start, t_stop=t_stop,
                                              window_size=window_pop_rate,n_neurons=n_exc)
    ax3.plot(ts, pop_rate, color=color_exc, linewidth=linewidth, marker='')
    if xlim is None:
        ax3.set_xlim([t_start, t_stop])
    else:
        ax3.set_xlim(xlim)
    ax3.set_xticks(x_ticks)
    ax3.set_xticklabels(["" for i in range(len(x_ticks))])
    ax3.set_ylabel(r'$\langle r_{i}^{exc} \rangle$' + "\n(Hz)", fontsize=fontsize, fontname=font)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_linewidth(axwidth)
    ax3.spines['left'].set_linewidth(axwidth)
    ax3.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    ax3.set_yticks(y_ticks_pop_rate)
    ax3.set_ylim(y_lim_pop_rate)

    for syn_num in range(n_to_plot_weights):
        ax4.plot(wie['t'], wie['w'][syn_num, :], color=color_ie, linewidth=linewidth_weights, alpha=alpha_w)
    ax4.plot(wie['t'], np.mean(wie['w'], axis=0), color=color_ie, linewidth=linewidth, alpha=1)
    ax4.set_ylabel(label_ws, fontsize=fontsize, fontname=font)
    # ax5.set_yscale('log')
    # ax5.tick_params(axis='y', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    if xlim is None:
        ax4.set_xlim([t_start, t_stop])
    else:
        ax4.set_xlim(xlim)
    if y_lim_wi is not None:
        ax4.set_ylim(y_lim_wi)
    if y_ticks_wi is not None:
        ax4.set_yticks(y_ticks_wi)
    if y_ticklabels_wi is not None:
        ax4.set_yticklabels(y_ticklabels_wi)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['bottom'].set_linewidth(axwidth)
    ax4.spines['left'].set_linewidth(axwidth)
    ax4.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    # ax5.tick_params(axis='y', which="minor", width=0.5*axwidth, labelsize=0, labelcolor='w', length=1*axwidth)
    ax4.set_xticks(x_ticks)
    ax4.set_xlabel(x_label, fontsize=fontsize, fontname=font, labelpad = 0)

def plot_simulation_6pPol_VintagePoly(sts_inp=None, sts_e=None, sts_i=None, n_to_plot_raster=None, 
                            n_exc=4096, n_inh=1024, n_input=5000, wie=None, wee=None, t_start=None, t_stop=None,
                            window_pop_rate=0.1, axwidth=4, linewidth=4, n_to_plot_weights=100, ms_raster=0.5,
                            fontsize=20, figsize=(5, 2), font = "arial",
                            color_inp=None, color_exc=None, color_inh=None, color_ie=None, color_ee=None,
                            x_ticks=None, x_ticklabels=None, x_label=None, alpha_w=None, xlim=None,
                            linewidth_weights=0.5, ylabel_w=r'$w^{I\to E}_{ij}$',
                            y_ticks_wi=None, y_ticklabels_wi=None, y_lim_wi=None,
                            y_ticks_pop_rate=None, y_lim_pop_rate=None,
                            y_lim_we=None, y_ticks_we=None, y_ticklabels_we=None):
    
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6,1,figsize=figsize, constrained_layout=True, dpi=600, 
                                                  gridspec_kw={'height_ratios': [1.5, 1.5, 1.5, 1.2, 1.2, 1.2]})
    
    for ct, neuron_num in enumerate(np.linspace(0, n_input-1, num=n_to_plot_raster, dtype=int)):
        ax1.scatter(sts_inp[str(neuron_num)], np.full(len(sts_inp[str(neuron_num)]), ct),
                    linewidths=0, color=color_inp, s=ms_raster, edgecolors=None, marker='o')
    if xlim is None:
        ax1.set_xlim([t_start, t_stop])
    else:
        ax1.set_xlim(xlim)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_ylabel("Inputs", fontsize=fontsize, fontname=font)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)

    for ct, neuron_num in enumerate(np.linspace(0, n_exc-1, num=n_to_plot_raster, dtype=int)):
        ax2.scatter(sts_e[str(neuron_num)], np.full(len(sts_e[str(neuron_num)]), ct), linewidths=0, 
                    color=color_exc, s=ms_raster, edgecolors=None, marker='o')
    if xlim is None:
        ax2.set_xlim([t_start, t_stop])
    else:
        ax2.set_xlim(xlim)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_ylabel("Exc", fontsize=fontsize, fontname=font)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    for ct, neuron_num in enumerate(np.linspace(0, n_inh-1, num=n_to_plot_raster, dtype=int)):
        ax3.scatter(sts_i[str(neuron_num)], np.full(len(sts_i[str(neuron_num)]), ct), linewidths=0,
                    color=color_inh, s=ms_raster, edgecolors=None, marker='o')
    if xlim is None:
        ax3.set_xlim([t_start, t_stop])
    else:
        ax3.set_xlim(xlim)
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_ylabel("Inh", fontsize=fontsize, fontname=font)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    
    ts, pop_rate = get_pop_rate_square_window(spiketimes=sts_e,t_start=t_start, t_stop=t_stop,
                                              window_size=window_pop_rate,n_neurons=n_exc)
    ax4.plot(ts, pop_rate, color=color_exc, linewidth=linewidth, marker='')
    if xlim is None:
        ax4.set_xlim([t_start, t_stop])
    else:
        ax4.set_xlim(xlim)
    ax4.set_xticks(x_ticks)
    ax4.set_xticklabels(["" for i in range(len(x_ticks))])
    ax4.set_ylabel(r'$\langle r_{i}^{exc} \rangle$' + "\n(Hz)", fontsize=fontsize, fontname=font)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['bottom'].set_linewidth(axwidth)
    ax4.spines['left'].set_linewidth(axwidth)
    ax4.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    ax4.set_yticks(y_ticks_pop_rate)
    ax4.set_ylim(y_lim_pop_rate)

    for syn_num in range(n_to_plot_weights):
        ax5.plot(wie['t'], wie['w'][syn_num, :], color=color_ie, linewidth=linewidth_weights, alpha=alpha_w)
    ax5.plot(wie['t'], np.mean(wie['w'], axis=0), color=color_ie, linewidth=linewidth, alpha=1)
    ax5.set_ylabel(ylabel_w, fontsize=fontsize, fontname=font)
    # ax5.set_yscale('log')
    # ax5.tick_params(axis='y', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    if xlim is None:
        ax5.set_xlim([t_start, t_stop])
    else:
        ax5.set_xlim(xlim)
    ax5.set_xticks([])
    ax5.set_yticks([])
    if y_lim_wi is not None:
        ax5.set_ylim(y_lim_wi)
    if y_ticks_wi is not None:
        ax5.set_yticks(y_ticks_wi)
    if y_ticklabels_wi is not None:
        ax5.set_yticklabels(y_ticklabels_wi)
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    ax5.spines['bottom'].set_linewidth(axwidth)
    ax5.spines['left'].set_linewidth(axwidth)
    ax5.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)

    for syn_num in range(n_to_plot_weights):
        ax6.plot(wee['t'], wee['w'][syn_num, :], color=color_ee, linewidth=linewidth_weights, alpha=alpha_w)
    ax6.plot(wee['t'], np.mean(wee['w'], axis=0), color=color_ee, linewidth=linewidth, alpha=1)
    ax6.set_ylabel(r'$w^{E\to E}_{ij}$', fontsize=fontsize, fontname=font)
    # ax5.set_yscale('log')
    # ax5.tick_params(axis='y', which="minor", width=0.5*linewidth, labelsize=0, labelcolor='w', length=1.5*linewidth)
    if xlim is None:
        ax6.set_xlim([t_start, t_stop])
    else:
        ax6.set_xlim(xlim)
    if y_lim_we is not None:
        ax6.set_ylim(y_lim_we)
    if y_ticks_we is not None:
        ax6.set_yticks(y_ticks_we)
    if y_ticklabels_we is not None:
        ax6.set_yticklabels(y_ticklabels_we)
    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)
    ax6.spines['bottom'].set_linewidth(axwidth)
    ax6.spines['left'].set_linewidth(axwidth)
    ax6.tick_params(width=axwidth, labelsize=fontsize, length=2*axwidth)
    # ax6.tick_params(axis='y', which="minor", width=0.5*axwidth, labelsize=0, labelcolor='w', length=1*axwidth)
    ax6.set_xticks(x_ticks)
    ax6.set_xlabel(x_label, fontsize=fontsize, fontname=font, labelpad = 0)
