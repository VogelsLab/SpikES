/* 
* This file is adapted from StimulusGroup, a part of Auryn, written by Friedemann Zenke
* only handles binary patterns
*/

#include "RandStimGroup.h"

using namespace auryn;

boost::mt19937 RandStimGroup::poisson_gen = boost::mt19937(); 
boost::mt19937 RandStimGroup::order_gen = boost::mt19937(); 
boost::uniform_01<boost::mt19937> RandStimGroup::order_die = boost::uniform_01<boost::mt19937> (order_gen);

void RandStimGroup::init(StimulusGroupModeType stimulusmode, AurynFloat baserate)
{
	auryn::sys->register_spiking_group(this);

	refractory_period = 1; // initialize with a default of one timestep (avoids two spikes in same time bin)

	activity = new AurynFloat [get_rank_size()];
	for ( NeuronID i = 0 ; i < get_rank_size() ; ++i ) activity[i] = 0.0;
	set_baserate(baserate);

	std::srand(std::time(0));
	seed(std::rand());

	set_stimulation_mode(stimulusmode); //updates stimulus_order to be stimulusmode
	stimulation_count = 0;
	stimulus_active = false;
	set_all(0.0); 

	randomintervals = true;
	mean_off_period = 0.0;
	mean_on_period = 0.0;

	randomintensities = false;
	scale = 1.0; // TODO does this need to be initialized at 2 ?
	curscale = scale;

	background_during_stimulus = true;

	background_rate = 0.0;
	bgx  = 0 ;
	fgx  = 0 ;

	cur_stim_index = 0;
	next_action_time = 0;
	last_action_time = 0;
	active = true;

}

RandStimGroup::RandStimGroup(NeuronID n, StimulusGroupModeType stimulusmode, AurynFloat baserate) : SpikingGroup(n)
{
	init(stimulusmode, baserate);
	write_stimfile = false;
}

RandStimGroup::RandStimGroup(NeuronID n, std::string stimfile, StimulusGroupModeType stimulusmode, AurynFloat baserate) : SpikingGroup(n)
{
	init(stimulusmode, baserate);
	write_stimfile = true;

	// if a filename was supplied and we are 
	// not supposed to be reading from it.
	if ( !stimfile.empty() && stimulus_order != STIMFILE ) 
	{
		tiserfile.open(stimfile.c_str(),std::ios::out);
		tiserfile.setf(std::ios::fixed);
	} else {
		if (stimulus_order==STIMFILE) {
			tiserfile.open(stimfile.c_str(),std::ios::in);
		}
	}

	if (!tiserfile) {
		std::stringstream oss;
		oss << "StimulusGroup:: Cannot open stimulus file " 
			<< stimfile
			<< " for ";
		if (stimulus_order==STIMFILE) oss << "reading.";
		else oss << "writing.";

		auryn::logger->msg(oss.str(),ERROR);
		throw AurynOpenFileException();
	}
}

RandStimGroup::~RandStimGroup(){
	tiserfile.close();
}

void RandStimGroup::set_baserate(AurynFloat baserate)
{
	base_rate = baserate;
}

void RandStimGroup::set_mean_off_period(AurynFloat period)
{
	mean_off_period = period;
}

void RandStimGroup::set_mean_on_period(AurynFloat period)
{
	mean_on_period = period;
}

void RandStimGroup::evolve()
{
	if ( !active ) return;

	if ( stimulus_active ) { // during active stimulation

		// detect and push spikes
		boost::exponential_distribution<> dist(curscale);
		boost::variate_generator<boost::mt19937&, boost::exponential_distribution<> > die(poisson_gen, dist);

		type_pattern current = stimuli[cur_stim_index];

		if ( !background_during_stimulus )
			bgx = get_rank_size();

		while ( bgx < get_rank_size() || fgx < current.size() ) {
			if ( fgx < current.size() && current.at(fgx).i < bgx ) {
				push_spike ( current.at(fgx).i );
				AurynDouble r = die();
				fgx += 1+(NeuronID)(r/auryn_timestep);
			} else {
				push_spike ( bgx );

				boost::exponential_distribution<> bg_dist(background_rate);
				boost::variate_generator<boost::mt19937&, boost::exponential_distribution<> > bg_die(poisson_gen, bg_dist);
				AurynDouble r = bg_die();
				bgx += 1+(NeuronID)(r/auryn_timestep); 
			}
		}
		if ( background_during_stimulus )
			bgx -= get_rank_size();

		if ( fgx >= current.size() )
			fgx -= current.size();

	} else { // while stimulation is off
		if ( background_rate ) {
			boost::exponential_distribution<> dist(background_rate);
			boost::variate_generator<boost::mt19937&, boost::exponential_distribution<> > die(poisson_gen, dist);

			while ( bgx < get_rank_size() ) {
				push_spike ( bgx );
				AurynDouble r = die();
				bgx += 1+(NeuronID)(r/auryn_timestep); 
			}
			bgx -= get_rank_size();
		}
	}

	// update stimulus properties
	if ( auryn::sys->get_clock() >= next_action_time ) { // action required
		last_action_time = next_action_time; // store last time before updating next_action_time

		if ( get_num_stimuli() == 0 ) {
			set_next_action_time(10); // TODO make this a bit smarter at some point -- i.e. could send this to the end of time 
			return;
		}

		if (write_stimfile){write_stimulus_file(auryn_timestep*(auryn::sys->get_clock()));}

		// if we have variable rate stimuli update curscale otherwise set to scale 
		// this is only needed for binary stimuli -- otherwise the change is done in
		// set_pattern_activity
		if ( randomintensities ) {
			curscale = scale*(AurynFloat)order_die();
		} else {
			curscale = scale;
		}

		
		// generate stimulus times
		if (stimulus_active) { // stimulus was active and going inactive now

			stimulus_active = false;
			last_stim_offset_time = sys->get_clock();

			if ( randomintervals && mean_off_period>0.0 ) {
				boost::exponential_distribution<> dist(1./mean_off_period);
				boost::variate_generator<boost::mt19937&, boost::exponential_distribution<> > die(order_gen, dist);
				next_action_time = auryn::sys->get_clock() + (AurynTime)(std::max(0.0,die())/auryn_timestep);
			} else {
				next_action_time = auryn::sys->get_clock() + (AurynTime)(mean_off_period/auryn_timestep);
			}
		} else { // stimulus was not active and is going active now
			if ( active && get_num_stimuli() ) { // the group is active and there are stimuli in the array

				// chooses stimulus according to schema specified in stimulusmode
				double draw, cummulative;
				switch ( stimulus_order ) {
					case RANDOM: //draw a random stimulus
						draw = order_die();
						cummulative = 0; 
						cur_stim_index = 0;
						for ( unsigned int i = 0 ; i < probabilities.size() ; ++i ) {
							cummulative += probabilities[i];
							if ( draw <= cummulative ) {
								cur_stim_index = i;
								break;
							}
						}
					break;
					case SEQUENTIAL:
						cur_stim_index = (cur_stim_index+1)%get_num_stimuli();
					break;
					case SEQUENTIAL_REV:
						--cur_stim_index;
						if ( cur_stim_index <= 0 ) 
							cur_stim_index = get_num_stimuli() - 1 ;
					break;
					case MANUAL:
					default:
					break;
				}

				stimulus_active = true;
				stimulation_count++;
				last_stim_onset_time = sys->get_clock();

				if ( randomintervals && stimulus_order != STIMFILE ) {
					boost::normal_distribution<> dist(mean_on_period,mean_on_period/3);
					boost::variate_generator<boost::mt19937&, boost::normal_distribution<> > die(order_gen, dist);
					next_action_time = auryn::sys->get_clock() + (AurynTime)(std::max(0.0,die())/auryn_timestep);
				} else {
					next_action_time = auryn::sys->get_clock() + (AurynTime)(mean_on_period/auryn_timestep);
				}
			}
		}
		if (write_stimfile){write_stimulus_file(auryn_timestep*(auryn::sys->get_clock()+1));}
	}
}

void RandStimGroup::set_activity(NeuronID i, AurynFloat val)
{
	activity[i] = val;
}

void RandStimGroup::set_all(AurynFloat val)
{
	for ( NeuronID i = 0 ; i < get_rank_size() ; ++i )
		set_activity(i,val);
}

AurynFloat RandStimGroup::get_activity(NeuronID i)
{
	if ( localrank(i) )
		return activity[global2rank(i)];
	else 
		return 0;
}

void RandStimGroup::clear_patterns( )
{
	stimuli.clear();
	stimulus_active = false;
	bgx  = 0;
	fgx  = 0;
	cur_stim_index = 0;
	next_action_time = 0;
	last_action_time = 0;
	set_all(0.0); 
	randomintervals = true;
	curscale = scale;
}

void RandStimGroup::load_patterns( std::vector< std::vector< std::vector<float> > > pat_array)
{
	clear_patterns();

	int n_patterns = pat_array.size();
	pattern_member pm;
	for (int pattern_num = 0; pattern_num < n_patterns; pattern_num++) {
		type_pattern pattern;
		int size_pattern = pat_array[pattern_num].size();
		for (int neuron_num = 0; neuron_num < size_pattern; neuron_num++){
			pm.i = global2rank(int(pat_array[pattern_num][neuron_num][0]));
			pm.gamma = pat_array[pattern_num][neuron_num][1];
			pattern.push_back(pm);
		}
		stimuli.push_back(pattern);
	}

	// initializing all probabilities as a flat distribution
	probabilities.clear();
	flat_distribution();
}

void RandStimGroup::set_pattern_activity(unsigned int i)
{
	type_pattern current = stimuli[i];
	type_pattern::iterator iter;

	AurynFloat addrate = 0.0;
	if ( background_during_stimulus ) 
		addrate = background_rate;

	AurynFloat curscale = scale;
	if ( randomintensities ) {
		boost::exponential_distribution<> dist(1.);
		boost::variate_generator<boost::mt19937&, boost::exponential_distribution<> > die(order_gen, dist);
		curscale *= (AurynFloat)die();
	}

	for ( iter = current.begin() ; iter != current.end() ; ++iter )
	{
		set_activity(iter->i,curscale*iter->gamma+addrate);
	}
}

void RandStimGroup::set_pattern_activity(unsigned int i, AurynFloat setrate)
{
	type_pattern current = stimuli[i];
	type_pattern::iterator iter;

	for ( iter = current.begin() ; iter != current.end() ; ++iter )
	{
		set_activity(iter->i,setrate);
	}
}


void RandStimGroup::set_active_pattern(unsigned int i, AurynFloat default_value)
{
	std::stringstream oss;
	oss << "RandStimGroup:: Setting active pattern " << i ;

	set_all( default_value );
	if ( i < get_num_stimuli() ) {
		set_pattern_activity(i);
	}
}

void RandStimGroup::set_active_pattern(unsigned int i)
{
	set_active_pattern(i, background_rate);
}


void RandStimGroup::set_distribution( std::vector<double> probs )
{
	for ( unsigned int i = 0 ; i < get_num_stimuli() ; ++i ) {
		probabilities[i] = probs[i];
	}

	normalize_distribution();

	std::stringstream oss;
	oss << "RandStimGroup: Set distribution [";
	for ( unsigned int i = 0 ; i < get_num_stimuli() ; ++i ) {
		oss << " " << probabilities[i];
	}
	oss << " ]";
}

std::vector<double> RandStimGroup::get_distribution( )
{
	return probabilities;
}

double RandStimGroup::get_distribution( int i )
{
	return probabilities[i];
}

void RandStimGroup::flat_distribution( ) 
{
	for ( unsigned int i = 0 ; i < get_num_stimuli() ; ++i ) {
		probabilities.push_back(1./((double)get_num_stimuli()));
	}
}

void RandStimGroup::normalize_distribution()
{
	std::stringstream oss;
	oss << "RandStimGroup: Normalizing distribution [";
	double sum = 0 ;
	for ( unsigned int i = 0 ; i < get_num_stimuli() ; ++i ) {
		sum += probabilities[i];
	}

	// normalize vector 
	for ( unsigned int i = 0 ; i < get_num_stimuli() ; ++i ) {
		probabilities[i] /= sum;
		oss << " " << probabilities[i];
	}

	oss << " ]";
}

std::vector<type_pattern> * RandStimGroup::get_patterns()
{
	return &stimuli;
}

void RandStimGroup::set_next_action_time( double time ) {
	next_action_time = auryn::sys->get_clock() + time/auryn_timestep;
}

void RandStimGroup::set_stimulation_mode( StimulusGroupModeType mode ) {
	stimulus_order = mode ;
}

void RandStimGroup::seed(int rndseed)
{
	unsigned int rnd = rndseed + sys->get_synced_seed(); // most be same on all ranks
	order_gen.seed(rnd); 

	// this is here because the seeding above alone does not seem to do anything
	// also need to overwrite the dist operator because it makes of copy of the
	// generator
	// see http://www.bnikolic.co.uk/blog/cpp-boost-uniform01.html
	order_die = boost::uniform_01<boost::mt19937> (order_gen);

	rnd = rndseed + sys->get_seed(); // adds salt to make it different across ranks
	std::stringstream oss;
	oss << "RandStimGroup:: " 
		<< "seeding Poisson generator with " 
		<< rnd;
	
	poisson_gen.seed(rnd); // is now drawn differently but reproducibly so for each rank
}

AurynTime RandStimGroup::get_last_action_time()
{
	return last_action_time;
}

AurynTime RandStimGroup::get_next_action_time()
{
	return next_action_time;
}

AurynTime RandStimGroup::get_last_onset_time()
{
	return last_stim_onset_time;
}

AurynTime RandStimGroup::get_last_offset_time()
{
	return last_stim_offset_time;
}

bool RandStimGroup::get_stim_active()
{
	return stimulus_active;
}

unsigned int RandStimGroup::get_cur_stim()
{
	return cur_stim_index;
}

unsigned int RandStimGroup::get_num_stimuli()
{
	return stimuli.size();
}

unsigned int RandStimGroup::get_stim_count()
{
	return stimulation_count;
}

void RandStimGroup::write_stimulus_file(AurynDouble time) {
	if ( tiserfile && stimulus_order != STIMFILE ) {
		tiserfile 
			<< time
			<< " ";
		if (stimulus_active) tiserfile << "1 "; else tiserfile << "0 ";
		tiserfile 
			<< cur_stim_index
			<< std::endl;
	}
}