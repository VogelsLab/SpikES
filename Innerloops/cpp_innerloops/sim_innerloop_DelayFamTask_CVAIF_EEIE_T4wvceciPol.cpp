#include "auryn.h"
#include "T4wvceciPolConnection.h"
#include "CheckerScorer_DelayFamTask.h"
#include "RFConnection.h"
#include "RandStimGroup.h"

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <ctime>

/*!\file 
 * This is a part of Synapseek, written by Basile Confavreux. It uses the spiking network simulator Auryn written by Friedemann Zenke.
 * This file is intended to be called by the corresponding python synapseek innerloop as part of a meta-optimization of plasticity rules.
 * It simulates a E-I spiking network with I-E and E-E plasticity, parametrized with polynomials.
 * The exc neurons receive structured activity (N_patterns alternating input patterns), with spatially structured connectivity.
 * The loss returned quantifies the ability of the network to recognize familiar input partterns vs novel ones 
 * The protocol and parameter values are inspired by/taken from Zenke, Agnes & Gerstner 2015.
 * For more details about each parameter, see below in program options.
 */

namespace po = boost::program_options;
using namespace auryn;

template<class T>
std::string toString(const T &value) {
    std::ostringstream os;
    os << value;
    return os.str();
}

// this function generates random input patterns for the network to learn (compatible with RandStimGroup)
std::vector< std::vector< std::vector<float> > > PatternGenerator(int N_neurons, int N_active, int N_patterns, float gamma)
{
    std::vector< std::vector< std::vector<float> > > pat_array(N_patterns, std::vector< std::vector<float> >(N_active , std::vector<float>(2)));
	for (int pattern_num = 0; pattern_num < N_patterns; pattern_num++){
		//pick a random starting neuron then choosing contiguous neurons to be the rest of the pattern
        int rand_ind = std::rand() % (N_neurons - N_active);
        for (int ind = 0; ind < N_active; ind++){
            pat_array[pattern_num][ind][0] = ind + rand_ind;
            pat_array[pattern_num][ind][1] = gamma;
        }
    }
    return pat_array;
}

int main(int ac, char* av[]) 
{
	std::srand(std::time(0)); //not good random source with rand(), try smth else?
	
	/////////////////////////////////////////////////////////
	// Get simulation parameters from command line options //
	/////////////////////////////////////////////////////////

	// Note all these default values can be modified by boost program options
	int ID = 0;

    int NE = 4096;
	int NI = 1024;

	float wi_exc = 0.1;
	float wi_inh = 0.5;
    float wmax = 1.5;
	float wii = 0.2;
	float wei = 0.2;
	double sparseness = 0.1;
	
    float r_cut_new = 15.0;
	float r_cut_fam = 25.0;
    float tau_pop = 0.1;
	float tau_ind = 1.0;

	int N_input = 4096;
	int N_active = 409;
    int N_patterns = 2;
	int radius = 8;
	double scale = 1.0;
    double bgrate = 10.0;
	float w_stim_e = 0.1; //0.5 in the paper!!
    float ontime_train = 2.0;
    float offtime_train = 0.1;
    float ontime_test =100;
    float offtime_test = 100;

	std::vector<std::string> rule_EE_str;
    std::vector<std::string> rule_IE_str;
	std::vector<float> rule_EE(21);
	std::vector<float> rule_IE(21);

	float l_train = 0.;
	float l_break1 = 0.;
	float l_stimon = 0.;
	float l_delay1 = 0.;
	float l_score = 0.;
	float l_break2 = 0.;
	float l_delay2 = 0.;

    std::string workdir;

    try {
        po::options_description desc("Allowed options");
        desc.add_options()
			("ID", po::value<int>(), "unique ID associated with this simulation")
			("NE", po::value<int>(), "number of excitatory neurons")
			("NI", po::value<int>(), "number of inhibitory neurons")
			("N_input", po::value<int>(), "number of input neurons, needs to be a perfect square")
            ("r_cut_new", po::value<float>(), "where to transition ReLu loss in case of novel stimulus")
			("r_cut_fam", po::value<float>(), "where to transition ReLu loss in case of familiar stimulus")
			("tau_pop", po::value<float>(), "time constant to compute population firing rate")
			("tau_ind", po::value<float>(), "time constant to compute population firing rate")
			("ontime_train", po::value<float>(), "mean duration of 1 pattern presentation during training phase")
			("offtime_train", po::value<float>(), "mean duration between pattern presentations during training phase")
			("ontime_test", po::value<float>(), "mean duration of 1 pattern presentation during test phase")
			("offtime_test", po::value<float>(), "mean duration between pattern presentations during test phase")
			("scale", po::value<double>(), "how much a input neuron from an active pattern fires compared to baseline")
			("bgrate", po::value<double>(), "baseline rate of input neurons")
			("N_active", po::value<int>(), "number of active input neurons in one pattern")
			("N_patterns", po::value<int>(), "number of patterns presented to the network")
			("radius", po::value<int>(), "radius (in number of neurons) of the receptive field of the exc neurons in the network")
			("rule_EE", po::value< std::vector<std::string> >(), "[tau_pre_EE1, tau_pre_EE2, tau_post_EE1, tau_post_EE2, 7 coeffs_pre, 7 coeffs_post] as a string")
            ("rule_IE", po::value< std::vector<std::string> >(), "[tau_pre_EE1, tau_pre_EE2, tau_post_EE1, tau_post_EE2, 7 coeffs_pre, 7 coeffs_post] as a string")
			("l_train", po::value<float>(), "training time during which network sees famniliar stimuli")
			("l_break1", po::value<float>(), "break between train and test, no active patterns")
			("l_stimon", po::value<float>(), "how long an input pattern is on during the 2 testing phases")
			("l_delay1", po::value<float>(), "delay between input pattern on and start of scoring window, no active input pattern")
			("l_score", po::value<float>(), "length of scoring window during which loss is computed, no active input pattern")
			("l_break2", po::value<float>(), "break with no active pattern between 2 testing phases")
			("l_delay2", po::value<float>(), "delay between second stimulus presentation and scoring window, no active input pattern")
			("wi_exc", po::value<float>(), "initial EE weights")
            ("wi_inh", po::value<float>(), "initial IE weights")
			("wmax", po::value<float>(), "max value for exc/inh weights")
			("wii", po::value<float>(), "II weight value")
			("wei", po::value<float>(), "EI weight value")
			("w_stim_e", po::value<float>(), "input weights to E value")
			("sparseness", po::value<float>(), "sparseness for EE EI IE and II connectivity")
			("workdir", po::value<std::string>(), "location to write or read files")
        ;

        po::variables_map vm;        
        po::store(po::parse_command_line(ac, av, desc), vm);

		if (vm.count("ID")) {ID= vm["ID"].as<int>();}
		if (vm.count("NE")) {NE = vm["NE"].as<int>();}
		if (vm.count("NI")) {NI = vm["NI"].as<int>();}
		if (vm.count("N_input")) {N_input = vm["N_input"].as<int>();}
		if (vm.count("r_cut_new")) {r_cut_new = vm["r_cut_new"].as<float>();}
		if (vm.count("r_cut_fam")) {r_cut_fam = vm["r_cut_fam"].as<float>();}
		if (vm.count("tau_pop")) {tau_pop = vm["tau_pop"].as<float>();}
		if (vm.count("tau_ind")) {tau_ind = vm["tau_ind"].as<float>();}
		if (vm.count("ontime_train")) {ontime_train = vm["ontime_train"].as<float>();}
		if (vm.count("offtime_train")) {offtime_train = vm["offtime_train"].as<float>();}
		if (vm.count("ontime_test")) {ontime_test = vm["ontime_test"].as<float>();}
		if (vm.count("offtime_test")) {offtime_test = vm["offtime_test"].as<float>();}
		if (vm.count("scale")) {scale = vm["scale"].as<double>();}
		if (vm.count("bgrate")) {bgrate = vm["bgrate"].as<double>();}
		if (vm.count("N_active")) {N_active = vm["N_active"].as<int>();}
		if (vm.count("N_patterns")) {N_patterns = vm["N_patterns"].as<int>();}
		if (vm.count("radius")) {radius = vm["radius"].as<int>();}
		if (vm.count("rule_EE")) {rule_EE_str = vm["rule_EE"].as< std::vector<std::string> >();}
        if (vm.count("rule_IE")) {rule_IE_str = vm["rule_IE"].as< std::vector<std::string> >();}
		if (vm.count("l_train")) {l_train = vm["l_train"].as<float>();}
		if (vm.count("l_break1")) {l_break1 = vm["l_break1"].as<float>();}
		if (vm.count("l_stimon")) {l_stimon = vm["l_stimon"].as<float>();}
		if (vm.count("l_delay1")) {l_delay1 = vm["l_delay1"].as<float>();}
		if (vm.count("l_score")) {l_score = vm["l_score"].as<float>();}
		if (vm.count("l_break2")) {l_break2 = vm["l_break2"].as<float>();}
		if (vm.count("l_delay2")) {l_delay2 = vm["l_delay2"].as<float>();}
		if (vm.count("wi_exc")) {wi_exc = vm["wi_exc"].as<float>();}
        if (vm.count("wi_inh")) {wi_inh = vm["wi_inh"].as<float>();}
		if (vm.count("wmax")) {wmax = vm["wmax"].as<float>();}
		if (vm.count("wii")) {wii = vm["wii"].as<float>();}
		if (vm.count("wei")) {wei = vm["wei"].as<float>();}
		if (vm.count("w_stim_e")) {w_stim_e = vm["w_stim_e"].as<float>();}
		if (vm.count("sparseness")) {sparseness = vm["sparseness"].as<float>();}
		if (vm.count("workdir")) {workdir = vm["workdir"].as<std::string>();}
	}
	catch(std::exception& e) {
        std::cerr << "error: " << e.what() << "\n";
        return 1;
    }
    catch(...) {
        std::cerr << "Exception of unknown type!\n";
    }

	// parsing the command line arguments for the plasticity parameters
	// (they are given as a string because multitoken() is bugged: negative numbers cause errors)
	// rule_EE
	std::string s = rule_EE_str[0];
	std::string delimiter = "a";
	size_t pos = 0;
	int ct = 0; 
	std::string token;
	
	token = s.substr(0, pos); // remove the first a (needed in case first param is negative, or is it?)
	s.erase(0, pos + delimiter.length());

	while ((pos = s.find(delimiter)) != std::string::npos) { // parse the rest of the expression
		token = s.substr(0, pos);
		rule_EE[ct] = boost::lexical_cast<float>(token);
		s.erase(0, pos + delimiter.length());
		ct ++;
	}

	// rule_IE
	s = rule_IE_str[0];
	pos = 0;
	ct = 0; 
	
	token = s.substr(0, pos); // remove the first a (needed in case first param is negative, or is it?)
	s.erase(0, pos + delimiter.length());

	while ((pos = s.find(delimiter)) != std::string::npos) { // parse the rest of the expression
		token = s.substr(0, pos);
		rule_IE[ct] = boost::lexical_cast<float>(token);
		s.erase(0, pos + delimiter.length());
		ct ++;
	}

	//////////////////////////////////////////////////
	// Define the rest of the simulation parameters //
	//////////////////////////////////////////////////

	float gamma = 1.0; //strength of stimulus wrt to bg (default 1 so that active rate = scale)
	AurynFloat min_rate_checker = 0.1; //Hz
	AurynFloat max_rate_checker = 100; //Hz

	// DEBUG //////////////////////////////////////////
	// std::cout << "ID=" << ID << " NE=" << NE << " NI=" << NI << " N_input=" << N_input << std::endl;
	// std::cout << " tau_pop=" << tau_pop << " tau_ind=" << tau_ind << " ontime_train=" << ontime_train << std::endl;
	// std::cout << " offtime_train=" << offtime_train << " ontime_test=" << ontime_test << " offtime_test=" << offtime_test << std::endl;
	// std::cout << " scale=" << scale << " bgrate=" << bgrate << " N_active=" << N_active << " N_patterns=" << N_patterns << std::endl;
	// std::cout << "rule_EE" << std::endl;
	// for (int i = 0; i < 36; i ++)
	// {
	// 	std::cout << rule_EE[i] << " ";
	// }
	// std::cout << "" << std::endl;
	// std::cout << "rule_IE" << std::endl;
	// for (int i = 0; i < 36; i ++)
	// {
	// 	std::cout << rule_IE[i] << " ";
	// }
	// std::cout << "" << std::endl;
	// std::cout << " radius=" << radius << std::endl;
	// std::cout << " length_scoring=" << length_scoring << " wi_inh=" << wi_inh << " wi_exc=" << wi_exc << " wmax=" << wmax << std::endl;
	//////////////////////////////////////////



	///////////////////////
	// Build the network //
	///////////////////////

	auryn_init(ac, av, workdir.c_str(), "default", "", NONE, NONE);
	sys->quiet = true;
	std::srand(std::time(0));
	sys->set_master_seed(std::rand());
	
	CVAIFGroup* neurons_e = new CVAIFGroup(NE);
	neurons_e->set_tau_ampa(5e-3);
	neurons_e->set_tau_gaba(10e-3);
	neurons_e->set_tau_nmda(100e-3);
	neurons_e->set_ampa_nmda_ratio(0.3);
	neurons_e->set_tau_vtrace(100e-3);
	neurons_e->set_tau_cexc(10e-3);
	neurons_e->set_tau_cinh(100e-3);

	CVAIFGroup* neurons_i = new CVAIFGroup(NI);
	neurons_i->set_tau_ampa(5e-3);
	neurons_i->set_tau_gaba(10e-3);
	neurons_i->set_tau_nmda(100e-3);
	neurons_i->set_ampa_nmda_ratio(0.3);
	neurons_i->set_tau_vtrace(100e-3);
	neurons_i->set_tau_cexc(10e-3);
	neurons_i->set_tau_cinh(100e-3);

	// external inputs to the network: familiar inputs
	std::vector< std::vector< std::vector<float> > > pat_array_fam = PatternGenerator(N_input, N_active, N_patterns, gamma);
    std::vector< std::vector< std::vector<float> > > pat_array_new = PatternGenerator(N_input, N_active, 1, gamma);
	RandStimGroup* stimgroup = new RandStimGroup(N_input);
    stimgroup->set_mean_on_period(ontime_train);
    stimgroup->set_mean_off_period(offtime_train);
    stimgroup->scale = scale;
    stimgroup->background_rate = bgrate;
    stimgroup->background_during_stimulus = true;
    stimgroup->load_patterns(pat_array_fam);
	RFConnection* rf_con = new RFConnection(stimgroup, neurons_e, w_stim_e, radius);

	// decide if this trial will be a new or familiar stimulus presentation first:
	int bin_int = std::rand() % 2;
	bool familiar_first;
	///////////////////////////////////////// DEBUG //////
	// std::cout << "will this be a familiar trial? " << bin_int << std::endl;
	///////////////////////////////////////////////////////
	if (bin_int == 1)
	{
		familiar_first = true;
	}
	else{
		familiar_first = false;
	}

	// recurrent connectivity
	SparseConnection* con_ei = new SparseConnection(neurons_e, neurons_i , wei , sparseness, GLUT);
	SparseConnection* con_ii = new SparseConnection(neurons_i, neurons_i , wii , sparseness, GABA);
	T4wvceciPolConnection* con_ee = new T4wvceciPolConnection(neurons_e, neurons_e, wi_exc, sparseness, rule_EE, wmax, GLUT, "T4wvceciPolConnectionEE");
	T4wvceciPolConnection* con_ie = new T4wvceciPolConnection(neurons_i, neurons_e, wi_inh, sparseness, rule_IE, wmax, GABA, "T4wvceciPolConnectionIE");

	// rate Checker (stop sim early if too bad), loss_pop and loss_ind calculation
	CheckerScorer_DelayFamTask* cs = new CheckerScorer_DelayFamTask(neurons_e, min_rate_checker, max_rate_checker, tau_pop, tau_ind, r_cut_fam, r_cut_new);
	
	///////////// DEBUG ///////////////////
	///////////////////////////////// DEBUG ///////////////////////////////////
	SpikeMonitor * smon_input = new SpikeMonitor(stimgroup , sys->fn("input.e","ras") );
	SpikeMonitor * smon_e = new SpikeMonitor(neurons_e , sys->fn("out.e","ras") );
	SpikeMonitor * smon_i = new SpikeMonitor(neurons_i, sys->fn("out.i","ras") );
	WeightMonitor * wmon = new WeightMonitor(con_ie, sys->fn("con_ie","syn"), 0.1);
	wmon->add_equally_spaced(100);
	WeightMonitor * wmon1 = new WeightMonitor(con_ee, sys->fn("con_ee","syn"), 0.1);
	wmon1->add_equally_spaced(100);
	///////////////////////////////////////////////////////
	//////////////////////////////////////////////////////////////////



	///////////////////////////////////////////////////////
	// Run the network for the training time, no scoring //
	///////////////////////////////////////////////////////
	
	sys->run(l_train);



	/////////////////////////////////////////////////
	// Scoring phase: evaluate network performance //
	/////////////////////////////////////////////////
	cs->scoring_phase = true; //means we compute loss_ind (individual firing rates)

	// a break with no active patterns
	stimgroup->clear_patterns();
	sys->run(l_break1);

	// stimulus presentation number 1
	// if we start by playing a familiar pattern, then load it, otherwise use the new one
	if (familiar_first)
	{
		stimgroup->load_patterns(pat_array_fam);
		cs->familiar = true;
	}
	else
	{
		stimgroup->load_patterns(pat_array_new);
		cs->familiar = false;
	}
	stimgroup->set_mean_on_period(ontime_test);
    stimgroup->set_mean_off_period(offtime_test);
	sys->run(l_stimon);

	// delay with no active patterns or scoring
	stimgroup->clear_patterns();
	sys->run(l_delay1);

	// scoring window
	cs->scoring_active = true;
	sys->run(l_score);
	cs->scoring_active = false;

	// break with no active pattern or scoring
	sys->run(l_break2);

	////////////// DEBUG ///////////////////////////////////
	// std::cout << "After first testing session " << std::endl;
	// std::cout << "loss_pop " << cs->loss_pop/(l_score)/10000 << std::endl;
	// std::cout << "loss_ind " << cs->loss_ind/(l_score + l_stimon + l_break1 + l_delay1)/NE/10000 << std::endl;
	// std::cout << "loss_reg " << con_ee->loss_reg/(l_score + l_stimon + l_break1 + l_delay1 + l_train)/10000/2 + con_ie->loss_reg/(l_score + l_stimon + l_break1 + l_delay1 + l_train)/10000/2 << std::endl;
	////////////////////////////////////////////////////////

	// stimulus presentation number 2
	// if we already tested the familiar pattern, play the novel one, and vice versa
	if (familiar_first)
	{
		stimgroup->load_patterns(pat_array_new);
		cs->familiar = false;
	}
	else
	{
		stimgroup->load_patterns(pat_array_fam);
		cs->familiar = true;
	}
	sys->run(l_stimon);

	// delay with no active patterns or scoring
	stimgroup->clear_patterns();
	sys->run(l_delay2);

	// scoring window
	cs->scoring_active = true;
	sys->run(l_score);



	/////////////////////////////////
	// Compute and return the loss //
	/////////////////////////////////

	double loss_pop = 0.0;
	double loss_ind = 0.0;
	double loss_reg = 0.0;
	double l_test_phase_tot = (l_break1 + l_stimon + l_delay1 + l_score + l_break2 + l_stimon + l_delay2 + l_score);
	if (cs->time_blow_up != -1.0) //there was a blow-up in the network before the end
	{
		////////////// DEBUG ///////////////////////////////////
		// std::cout << "blow up " <<  cs->time_blow_up << std::endl;
		////////////////////////////////////////////////////////
		loss_pop = (exp(-cs->time_blow_up/(l_train + 2*l_score + 2*l_stimon + l_break1 + l_break2 + l_delay1 + l_delay2)) + 42);
	}
	else {
		//10000 -> 0.1ms integration timestep in auryn
		loss_pop = cs->loss_pop/(2*l_score)/10000/2;
		loss_ind = cs->loss_ind/l_test_phase_tot/NE/10000/2;
		loss_reg = con_ee->loss_reg/(l_test_phase_tot + l_train)/10000/2 + con_ie->loss_reg/(l_test_phase_tot + l_train)/10000/2;

		////////////// DEBUG ///////////////////////////////////
		// std::cout << "no blow up " << std::endl;
		// std::cout << "loss_pop " << loss_pop << std::endl;
		// std::cout << "loss_ind " << loss_ind << std::endl;
		// std::cout << "loss_reg " << loss_reg << std::endl;
		// std::cout << "raw_loss_reg from con_ee " << con_ee->loss_reg << std::endl;
		// std::cout << "raw_loss_reg from con_ie " << con_ie->loss_reg << std::endl;
		////////////////////////////////////////////////////////
	}

	std::cout << "cynthia" << loss_pop << "cynthia" << loss_ind << "cynthia" << loss_reg << "cynthia";
	// because of the potential other things output by auryn to command line that will be captured by python, use an identifier ("cynthia")
    
	// Clean up
	auryn_free();
	
	return 0;
}