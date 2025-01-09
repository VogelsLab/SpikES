#include "auryn.h"
#include "SixParamConnection.h"
#include "CheckerScorer_Stability.h"

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

int main(int ac, char* av[]) 
{
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
	float length_no_scoring;
	float length_scoring;
	float target;
	int N_inputs;
	float sparseness_poisson;
	float w_poisson;
	float poisson_rate;
	AurynFloat min_rate_checker;
	AurynFloat max_rate_checker;
	AurynFloat tau_checker;
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
			("eta", po::value<float>(), "lerning rate for the rule")
			("rule", po::value< std::vector<std::string> >(), "plasticity rule, to enter as a string with separator a, one a at the beginning")
			("wmax", po::value<float>(), "max exc weight")
			("sparseness", po::value<float>(), "sparseness of all 4 recurrent connection types")
			("lns", po::value<float>(), "length_no_scoring")
			("ls", po::value<float>(), "length_scoring")
			("target", po::value<float>(), "target firing rate")
			("N_inputs", po::value<int>(), "number of input neurons")
			("sparseness_poisson", po::value<float>(), "sparseness of incoming poisson inputs to exc and inh  neurons")
			("w_poisson", po::value<float>(), "weights from inputs to exc and inh neurons")
			("poisson_rate", po::value<float>(), "poisson_rate in Hz")
			("min_rate_checker", po::value<float>(), "min_rate_checker in Hz")
			("max_rate_checker", po::value<float>(), "max_rate_checker in Hz")
			("tau_checker", po::value<float>(), "tau_checker in s")
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
		if (vm.count("lns")) {length_no_scoring = vm["lns"].as<float>();}
		if (vm.count("ls")) {length_scoring = vm["ls"].as<float>();}
		if (vm.count("target")) {target = vm["target"].as<float>();}
		if (vm.count("N_inputs")) {N_inputs = vm["N_inputs"].as<int>();}
		if (vm.count("sparseness_poisson")) {sparseness_poisson = vm["sparseness_poisson"].as<float>();}
		if (vm.count("w_poisson")) {w_poisson = vm["w_poisson"].as<float>();}
		if (vm.count("poisson_rate")) {poisson_rate = vm["poisson_rate"].as<float>();}
		if (vm.count("min_rate_checker")) {min_rate_checker = vm["min_rate_checker"].as<float>();}
		if (vm.count("max_rate_checker")) {max_rate_checker = vm["max_rate_checker"].as<float>();}
		if (vm.count("tau_checker")) {tau_checker = vm["tau_checker"].as<float>();}
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

	// DEBUG //////////////////////////////////////////////
	// std::cout << "tau_pre " << tau_pre << " tau_post " << tau_post << " alpha " << alpha << " beta " << beta << std::endl;
	// std::cout << " gamma " << gamma << " kappa " << kappa << " ID " << ID << " NE " << NE << " NI " << NI << std::endl;
	// std::cout << " eta " << eta << " length_no_scoring " << length_no_scoring << " length_scoring " <<length_scoring << std::endl;
	// std::cout << " wie " << wie << " target " << target << " workdir " << workdir << std::endl;
	///////////////////////////////////////////////////////


	///////////////////////
	// Build the network //
	///////////////////////

	auryn_init(ac, av, workdir.c_str(), "default", "", NONE, NONE);
	sys->quiet = true;
	
	TIFGroup * neurons_e = new TIFGroup(NE);
	TIFGroup * neurons_i = new TIFGroup(NI);
	neurons_e->set_refractory_period(5.0e-3);
	neurons_i->set_refractory_period(5.0e-3);

	// external inputs
	PoissonGroup * poisson = new PoissonGroup(N_inputs, poisson_rate);
	SparseConnection * con_ext_exc = new SparseConnection(poisson, neurons_e, w_poisson, sparseness_poisson, GLUT);
	SparseConnection * con_ext_inh = new SparseConnection(poisson, neurons_i, w_poisson, sparseness_poisson, GLUT);

	// recurrent connectivity
	SparseConnection * con_ee = new SparseConnection(neurons_e, neurons_e, wee, sparseness, GLUT);
	SparseConnection * con_ei = new SparseConnection(neurons_e, neurons_i, wei, sparseness, GLUT);
	SixParamConnection * con_ie = new SixParamConnection(neurons_i, neurons_e, wie, sparseness, eta, alpha, beta, gamma, kappa, tau_pre, tau_post, wmax, GABA);
	SparseConnection * con_ii = new SparseConnection(neurons_i, neurons_i, wii, sparseness, GABA);

	// rate checker and loss calculation when during scoring phase
	CheckerScorer_Stability* cs = new CheckerScorer_Stability(neurons_e , min_rate_checker , max_rate_checker , tau_checker, target);
	

	///////////////////////////////////////////////////////
	// Run the network for the training time, no scoring //
	///////////////////////////////////////////////////////
	
	sys->run(length_no_scoring);
	

	//////////////////////////////////////////
	// Run the network for the scoring time //
	//////////////////////////////////////////

	///////////////////////////////// DEBUG ///////////////////////////////////
	SpikeMonitor * smon_input = new SpikeMonitor(poisson , sys->fn("input.e","ras") );
	SpikeMonitor * smon_e = new SpikeMonitor(neurons_e , sys->fn("out.e","ras") );
	SpikeMonitor * smon_i = new SpikeMonitor(neurons_i, sys->fn("out.i","ras") );
	WeightMonitor * wmon = new WeightMonitor(con_ie, sys->fn("con_ie","syn"), 0.1);
	wmon->add_equally_spaced(100);
	///////////////////////////////////////////////////////

	cs->scoring_active = true;
	sys->run(length_scoring);



	/////////////////////////////////
	// Compute and return the loss // //TO CHANGE DEPENDING ON WHAT LOSS YOU CARE ABOUT
	/////////////////////////////////

	//return actual loss
	double loss_tot = 0.0;
	if (cs->time_blow_up != -1.0) //there was a blow-up in the network
	{
		//////////////DEBUG ////////////////////////////////////
		std::cout << "blow up " <<  cs->time_blow_up << std::endl;
		////////////////////////////////////////////////////////
		loss_tot = 160*(exp(-cs->time_blow_up/(length_scoring + length_no_scoring)) + 1);
	}
	else {
		loss_tot = cs->loss/length_scoring/10000; //10000 -> 0.1ms integration timestep in auryn
	}

	//return simply average firing rate
	// double loss_tot = 0.0;
	// if (cs->time_blow_up != -1.0) //there was a blow-up in the network
	// {
	// 	//////////////DEBUG ////////////////////////////////////
	// 	// std::cout << "blow up " <<  cs->time_blow_up << std::endl;
	// 	////////////////////////////////////////////////////////
	// 	loss_tot = 200;
	// }
	// else {
	// 	loss_tot = cs->avg_rate/length_scoring/10000; //10000 -> 0.1ms integration timestep in auryn
	// }

	std::cout << "cynthia" << loss_tot << "cynthia";
	// because of the potential other things output by auryn to command line that will be captured by python, use an identifier ("cynthia")
    
	auryn_free();
	return 0;
}