#include "auryn.h"
#include "SixParamConnection.h"
#include "CheckerScorer_FamDet_Lbasic.h"
#include "RFConnection.h"
#include "RandStimGroup.h"

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>

/*!\file 
* This is a part of Synapseek, written by Basile Confavreux. It uses the spiking network simulator Auryn written by Friedemann Zenke.
 * This file is intended to be called by the corresponding python synapseek innerloop as part of a meta-optimization of plasticity rules.
 * It simulates a E-I spiking network with I-E plasticity, parametrized with a polynomial with 6 parameters
 * Implementing simulation protocol similar From Vogels et al 2011, inhibitory plasticity. Adapted from sim_isp_orig, written by Friedemann Zenke.
 * Simulates and score a network of COBA Exc and Inh neurons, with AMPA and NMADA exc conductances, and inhibitory plasticity
 * Desired behaviour: reach and maintain target firing rate
 * Loss: <(firing rate - target)**2/(firing rate + 0.1)>neurons, time
 * */

namespace po = boost::program_options;
using namespace auryn;

template<class T>
std::string toString(const T &value) {
    std::ostringstream os;
    os << value;
    return os.str();
}

// this function generates input patterns for the network to learn (compatible with RandStimGroup)
std::vector< std::vector< std::vector<float> > > Fam_PatternGenerator(int N_neurons, int N_active, int N_patterns)
{
    std::vector< std::vector< std::vector<float> > > pat_array(N_patterns, std::vector< std::vector<float> >(N_active , std::vector<float>(2)));
	int aux = (int)N_neurons / (N_patterns+1);
	for (int pattern_num = 0; pattern_num < N_patterns; pattern_num++){
        int start_int = pattern_num*aux;
		///////////////////////////////// DEBUG ///////////////////////////////////
		// std::cout << "in pattern generator, start ind" << start_int << std::endl;
		///////////////////////////////////////////////////////////////////////////
        for (int ind = 0; ind < N_active; ind++){
            pat_array[pattern_num][ind][0] = ind + start_int;
            pat_array[pattern_num][ind][1] = 1;
        }
    }
	
    return pat_array;
}

std::vector< std::vector< std::vector<float> > > Nov_PatternGenerator(int N_neurons, int N_active, int N_patterns)
{
    std::vector< std::vector< std::vector<float> > > pat_array(1, std::vector< std::vector<float> >(N_active , std::vector<float>(2)));
	int aux = (int)N_neurons / (N_patterns+1);
    int start_int = N_patterns*aux;
    for (int ind = 0; ind < N_active; ind++){
		pat_array[0][ind][0] = ind + start_int;
		pat_array[0][ind][1] = 1;
    }
    return pat_array;
}

int main(int ac, char* av[]) 
{
	std::srand(std::time(0));

	/////////////////////////////////////////////////////////
	// Get simulation parameters from command line options //
	/////////////////////////////////////////////////////////

	int ID;
	int NE;
	int NI;
	float wee;
	float wei;
	float wie;
	float wii;
	float eta;
	std::vector<float> rule(6);
	std::vector<std::string> rule_str;
	float wmax;
	float sparseness;
	float l_train;
	float l_break1;
	float l_score;
	float l_break2;
	float rate_cut_fam;
	float rate_cut_nov;
	int N_inputs;
	float w_poisson;
	float bg_input_rate;
	int N_active_input;
	float active_input_rate;
	int N_patterns;
	int radius;
	float tau_checker_pop;
	float ontime_train;
	float offtime_train;
	float ontime_test;
	float offtime_test;
	AurynFloat min_rate_checker;
	AurynFloat max_rate_checker;
	std::string workdir;

    try {
        po::options_description desc("Allowed options");
        desc.add_options()
			("ID", po::value<int>(), "ID to name the monitor output files correctly")
			("NE", po::value<int>(), "number of excitatory neurons")
			("NI", po::value<int>(), "number of inhibitory neurons")
			("wee", po::value<float>(), "initial ee weights")
			("wei", po::value<float>(), "initial ei weights")
			("wie", po::value<float>(), "initial ie weights")
			("wii", po::value<float>(), "initial ii weights")
			("eta", po::value<float>(), "learning rate for the rule")
			("rule", po::value< std::vector<std::string> >(), "plasticity rule, to enter as a string with separator a, one a at the beginning")
			("wmax", po::value<float>(), "max exc weight")
			("sparseness", po::value<float>(), "sparseness of all 4 recurrent connection types")
			("l_train", po::value<float>(), "training time during which network sees famniliar stimuli")
			("l_break1", po::value<float>(), "break between train and test, no active patterns")
			("l_score", po::value<float>(), "length of scoring window during which loss is computed, no active input pattern")
			("l_break2", po::value<float>(), "break with no active pattern between 2 testing phases")
			("rate_cut_fam", po::value<float>(), "lower bound on the exc population firing rate to get 0 loss during familiar stim presentation ")
			("rate_cut_nov", po::value<float>(), "upper bound on the exc population firing rate to get 0 loss during novel stim presentation ")
			("N_inputs", po::value<int>(), "number of input neurons")
			("w_poisson", po::value<float>(), "weights from inputs to exc and inh neurons")
			("bg_input_rate", po::value<float>(), "poisson_rate in Hz")
			("N_active_input", po::value<int>(), "")
			("active_input_rate", po::value<float>(), "firing rate of active stimulus")
			("N_patterns", po::value<int>(), "")
			("radius", po::value<int>(), "radius (in number of neurons) of the receptive field of the exc neurons in the network")
			("tau_checker_pop", po::value<float>(), "time constant to compute population firing rate")
			("ontime_train", po::value<float>(), "mean duration of 1 pattern presentation during training phase")
			("offtime_train", po::value<float>(), "mean duration between pattern presentations during training phase")
			("ontime_test", po::value<float>(), "mean duration of 1 pattern presentation during test phase")
			("offtime_test", po::value<float>(), "mean duration between pattern presentations during test phase")
			("min_rate_checker", po::value<float>(), "min_rate_checker in Hz")
			("max_rate_checker", po::value<float>(), "max_rate_checker in Hz")
			("workdir", po::value<std::string>(), "workdir to write output files (until we have a writeless monitor)")
        ;

        po::variables_map vm;        
        po::store(po::parse_command_line(ac, av, desc), vm);

		if (vm.count("ID")) {ID= vm["ID"].as<int>();}
		if (vm.count("NE")) {NE = vm["NE"].as<int>();}
		if (vm.count("NI")) {NI = vm["NI"].as<int>();}
		if (vm.count("wee")) {wee = vm["wee"].as<float>();}
		if (vm.count("wei")) {wei = vm["wei"].as<float>();}
		if (vm.count("wie")) {wie = vm["wie"].as<float>();}
		if (vm.count("wii")) {wii = vm["wii"].as<float>();}
		if (vm.count("eta")) {eta = vm["eta"].as<float>();}
		if (vm.count("rule")) {rule_str = vm["rule"].as< std::vector<std::string> >();}
		if (vm.count("wmax")) {wmax = vm["wmax"].as<float>();}
		if (vm.count("sparseness")) {sparseness = vm["sparseness"].as<float>();}
		if (vm.count("l_train")) {l_train = vm["l_train"].as<float>();}
		if (vm.count("l_break1")) {l_break1 = vm["l_break1"].as<float>();}
		if (vm.count("l_score")) {l_score = vm["l_score"].as<float>();}
		if (vm.count("l_break2")) {l_break2 = vm["l_break2"].as<float>();}
		if (vm.count("rate_cut_fam")) {rate_cut_fam = vm["rate_cut_fam"].as<float>();}
		if (vm.count("rate_cut_nov")) {rate_cut_nov = vm["rate_cut_nov"].as<float>();}
		if (vm.count("N_inputs")) {N_inputs = vm["N_inputs"].as<int>();}
		if (vm.count("w_poisson")) {w_poisson = vm["w_poisson"].as<float>();}
		if (vm.count("bg_input_rate")) {bg_input_rate = vm["bg_input_rate"].as<float>();}
		if (vm.count("N_active_input")) {N_active_input = vm["N_active_input"].as<int>();}
		if (vm.count("active_input_rate")) {active_input_rate = vm["active_input_rate"].as<float>();}
		if (vm.count("N_patterns")) {N_patterns = vm["N_patterns"].as<int>();}
		if (vm.count("radius")) {radius = vm["radius"].as<int>();}
		if (vm.count("tau_checker_pop")) {tau_checker_pop = vm["tau_checker_pop"].as<float>();}
		if (vm.count("ontime_train")) {ontime_train = vm["ontime_train"].as<float>();}
		if (vm.count("offtime_train")) {offtime_train = vm["offtime_train"].as<float>();}
		if (vm.count("ontime_test")) {ontime_test = vm["ontime_test"].as<float>();}
		if (vm.count("offtime_test")) {offtime_test = vm["offtime_test"].as<float>();}
		if (vm.count("min_rate_checker")) {min_rate_checker = vm["min_rate_checker"].as<float>();}
		if (vm.count("max_rate_checker")) {max_rate_checker = vm["max_rate_checker"].as<float>();}
		if (vm.count("workdir")) {workdir = vm["workdir"].as<std::string>();}
	}
	catch(std::exception& e) {
        std::cerr << "error: " << e.what() << "\n";
        return 1;
    }
    catch(...) {
        std::cerr << "Exception of unknown type!\n";
    }

	// parsing the command line rule argument: (it is given as a string because multitoken() is bugged: negative numbers cause errors)
	std::string s = rule_str[0];
	std::string delimiter = "a";
	size_t pos = 0;
	int ct = 0; 
	std::string token;
	
	token = s.substr(0, pos); // remove the first a (needed in case first param is negative, or is it?)
	s.erase(0, pos + delimiter.length());

	while ((pos = s.find(delimiter)) != std::string::npos) { // parse the rest of the expression
		token = s.substr(0, pos);
		rule[ct] = boost::lexical_cast<float>(token);
		s.erase(0, pos + delimiter.length());
		ct ++;
	}

	float tau_pre = rule[0];
	float tau_post = rule[1];
	float alpha = rule[2];
	float beta = rule[3];
	float gamma = rule[4];
	float kappa = rule[5];

	///////////////////////////////// DEBUG ///////////////////////////////////
	// std::cout << "tau_pre " << tau_pre << " tau_post " << tau_post << " alpha " << alpha << " beta " << beta << std::endl;
	// std::cout << " gamma " << gamma << " kappa " << kappa << " ID " << ID << " NE " << NE << " NI " << NI << std::endl;
	// std::cout << " wee " << wee << " wei " << wei << " wie " << wie << " wii " << wii << " eta " << eta << std::endl;
	// std::cout << " wmax " << wmax << " sparseness " << sparseness << " l_train " << l_train << std::endl;
	// std::cout << " l_break1 " << l_break1 << " l_score " << l_score << " l_break2 " << l_break2 << std::endl;
	// std::cout << " rate_cut_fam " << rate_cut_fam << " rate_cut_nov " << rate_cut_nov << " N_inputs " << N_inputs << std::endl;
	// std::cout << " w_poisson " << w_poisson << " bg_input_rate " << bg_input_rate << std::endl;
	// std::cout << " N_active_input " << N_active_input << " active_input_rate " << active_input_rate << " N_patterns " << N_patterns << std::endl;
	// std::cout << " radius " << radius << " tau_checker_pop " << tau_checker_pop << " ontime_train " << ontime_train << std::endl;
	// std::cout << " offtime_train " << offtime_train << " ontime_test " << ontime_test << " offtime_test " << offtime_test << std::endl;
	// std::cout << " min_rate_checker " << min_rate_checker << " max_rate_checker " << max_rate_checker << " workdir " << workdir << std::endl;
	///////////////////////////////////////////////////////////////////////////


	///////////////////////
	// Build the network //
	///////////////////////

	auryn_init(ac, av, workdir.c_str(), "default", "", NONE, NONE);
	sys->quiet = true;
	
	// neuron populations
	TIFGroup * neurons_e = new TIFGroup(NE);
	TIFGroup * neurons_i = new TIFGroup(NI);
	neurons_e->set_refractory_period(5.0e-3);
	neurons_i->set_refractory_period(5.0e-3);

	// external inputs to the network:
	std::vector< std::vector< std::vector<float> > > pat_array_fam = Fam_PatternGenerator(N_inputs, N_active_input, N_patterns);
    std::vector< std::vector< std::vector<float> > > pat_array_new = Nov_PatternGenerator(N_inputs, N_active_input, N_patterns);
	RandStimGroup* stimgroup = new RandStimGroup(N_inputs);
    stimgroup->set_mean_on_period(ontime_train);
    stimgroup->set_mean_off_period(offtime_train);
    stimgroup->scale = active_input_rate/(bg_input_rate+0.01);
    stimgroup->background_rate = bg_input_rate;
    stimgroup->background_during_stimulus = true;
    stimgroup->load_patterns(pat_array_fam);
	RFConnection* rf_con = new RFConnection(stimgroup, neurons_e, w_poisson, radius);
	RFConnection* rf_con_i = new RFConnection(stimgroup, neurons_i, w_poisson, radius);

	// recurrent connectivity
	SparseConnection* con_ee = new SparseConnection(neurons_e, neurons_e, wee, sparseness, GLUT);
	SparseConnection* con_ei = new SparseConnection(neurons_e, neurons_i, wei, sparseness, GLUT);
	SixParamConnection* con_ie = new SixParamConnection(neurons_i, neurons_e, wie, sparseness, eta, alpha, beta, gamma, kappa, tau_pre, tau_post, wmax, GABA);
	SparseConnection* con_ii = new SparseConnection(neurons_i, neurons_i, wii, sparseness, GABA);

	// rate checker and loss calculation when during scoring phase
	CheckerScorer_FamDet_Lbasic* cs = new CheckerScorer_FamDet_Lbasic(neurons_e,
																	  min_rate_checker,
																	  max_rate_checker,
																	  tau_checker_pop,
																	  rate_cut_fam,
																	  rate_cut_nov);
	
	///////////////////////////////////////////////////////
	// Run the network for the training time, no scoring //
	///////////////////////////////////////////////////////

	///////////////////////////////// DEBUG ///////////////////////////////////
	SpikeMonitor * smon_input = new SpikeMonitor(stimgroup , sys->fn("input.e","ras") );
	SpikeMonitor * smon_e = new SpikeMonitor(neurons_e , sys->fn("out.e","ras") );
	SpikeMonitor * smon_i = new SpikeMonitor(neurons_i, sys->fn("out.i","ras") );
	WeightMonitor * wmon = new WeightMonitor(con_ie, sys->fn("con_ie","syn"), 0.1);
	wmon->add_equally_spaced(100);
	///////////////////////////////////////////////////////
	
	sys->run(l_train);

	stimgroup->clear_patterns();
	sys->run(l_break1);
	con_ie->stdp_active = false;


	/////////////////////////////////////////////////
	// Scoring phase: evaluate network performance //
	/////////////////////////////////////////////////
	
	// a break with no active patterns
	///////////////////////////////// DEBUG ///////////////////////////////////
	// stimgroup->clear_patterns();
	// sys->run(l_break1);
	///////////////////////////////////////////////////////

	// decide if this trial will be a new or familiar stimulus presentation first:
	int bin_int = std::rand() % 2;
	bool familiar_first = false; ////////////////////////////////////////////TO PUT BACK TO FALSE
	
	
	
	///////////////////////////////// DEBUG ///////////////////////////////////
	// if (bin_int == 1){familiar_first = true;} #####################################TO PUT BACK
	///////////////////////////////////////////////////////

	// stimulus presentation number 1
	cs->scoring_active = true;
	if (familiar_first){stimgroup->load_patterns(pat_array_fam); cs->familiar = true;} // if we start by playing a familiar pattern, then load it, otherwise use the new one
	else{stimgroup->load_patterns(pat_array_new); cs->familiar = false;}
	stimgroup->set_mean_on_period(ontime_test);
    stimgroup->set_mean_off_period(offtime_test);
	sys->run(l_score);

	///////////////////////////////// DEBUG ///////////////////////////////////
	// std::cout << "loss after one stimulus presentation " <<  cs->loss_pop/(l_score)/10000 << std::endl;
	///////////////////////////////////////////////////////////////////////////
	
	// a break with no active patterns
	cs->scoring_active = false;
	stimgroup->clear_patterns();
	sys->run(l_break2);

	// stimulus presentation number 2
	cs->scoring_active = true;
	if (familiar_first){stimgroup->load_patterns(pat_array_new); cs->familiar = false;} // if we already tested the familiar pattern, play the novel one, and vice versa
	else{stimgroup->load_patterns(pat_array_fam); cs->familiar = true;}
	sys->run(l_score);


	/////////////////////////////////
	// Compute and return the loss //
	/////////////////////////////////

	double loss_pop = 0.0;
	double length_test_phase_tot = (l_break1 + l_score + l_break2 + l_score);
	if (cs->time_blow_up != -1.0) //there was a blow-up in the network before the end
	{
		loss_pop = (exp(-cs->time_blow_up/(l_train + length_test_phase_tot)) + 42);
		///////////////////////////////// DEBUG ///////////////////////////////////
		std::cout << "blow up " <<  cs->time_blow_up << std::endl;
		///////////////////////////////////////////////////////////////////////////
	}
	else {
		loss_pop = cs->loss_pop/(2*l_score)/10000; //10000 -> 0.1ms integration timestep in auryn
		///////////////////////////////// DEBUG ///////////////////////////////////
		std::cout << "no blow up " << std::endl;
		std::cout << "loss_pop " << loss_pop << std::endl;
		///////////////////////////////////////////////////////////////////////////
	}

	std::cout << "cynthia" << loss_pop << "cynthia";
	// because of the potential other things output by auryn to command line that will be captured by python, use an identifier ("cynthia")
    
	auryn_free();
	return 0;
}