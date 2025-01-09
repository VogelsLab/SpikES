/* 
* This file is adapted from StimulusGroup, a part of Auryn, written by Friedemann Zenke.
*/

#ifndef RANDSTIMGROUP_H_

#define RANDSTIMGROUP_H_

#include "auryn/auryn_definitions.h"
#include "auryn/AurynVector.h"
#include "auryn/System.h"
#include "auryn/SpikingGroup.h"

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_01.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random/exponential_distribution.hpp>
#include <boost/random/normal_distribution.hpp>
#include <boost/random/variate_generator.hpp>

#define SOFTSTARTTIME 0.1

namespace auryn {


/*! \brief Provides a poisson stimulus at random intervals in one or more
 *         predefined subsets of the group that are read from an array. */
class RandStimGroup : public SpikingGroup
{
private:
	AurynTime * clk;
	AurynFloat base_rate;
	/*! Internal name for the stimfile (tiser stands for time series). */
	std::fstream tiserfile;
	bool write_stimfile;

protected:

	AurynFloat * activity;

	/*! Stimulus order */
	StimulusGroupModeType stimulus_order ;

	/*! \brief Counter variable for number of stimuli shown */
	unsigned int stimulation_count;

	/*! Foreground Poisson field pointer */
	NeuronID fgx;

	/*! Background Poisson field pointer */
	NeuronID bgx;

	/*! stimulus probabilities */
	std::vector<double> probabilities ;

	/*! pseudo random number generators */
	static boost::mt19937 poisson_gen; 

	/*! generates info for what stimulus is active. Is supposed to give the same result on all nodes (hence same seed required) */
	static boost::mt19937 order_gen; 
	static boost::uniform_01<boost::mt19937> order_die; 

	/*! \brief next stimulus time requiring change in rates */
	AurynTime next_action_time ;

	/*! \brief last stimulus time requiring change in rates */
	AurynTime last_action_time ;

	/*! \brief last stimulus onset time */
	AurynTime last_stim_onset_time ;

	/*! \brief last stimulus offset time */
	AurynTime last_stim_offset_time ;

	/*! Standard initialization */
	void init(StimulusGroupModeType stimulusmode, AurynFloat baserate);

	/*! Sets the activity for a given unit on the local rank. Activity determines the freq as baserate*activity */
	void set_activity( NeuronID i, AurynFloat val=0.0 );

	/*! allow silence/background activity periods */
	AurynFloat mean_off_period ;

	/*! mean presentation time  */
	AurynFloat mean_on_period ;

	AurynFloat curscale;
	
public:
	bool active;
	
	/*! \brief Current stimulus index 
	 *
	 * Do not write this variable. */
	int cur_stim_index ;

	/*! \brief Current stimulus active 
	 *
	 * Only read this state. */
	bool stimulus_active;


	/*! \brief Vector containing all the stimuli. */
	std::vector<type_pattern> stimuli;

	/*! \brief Returns number of stimuli */
	virtual unsigned int get_num_stimuli();

	/*! \brief This is by how much the pattern gamma value is multiplied. The resulting value gives the x-times baseline activation */
	AurynFloat scale;

	/*! \brief Enables a finite refractory time specified in AurynTime (only works for non-binary-pattern mode. */
	AurynTime refractory_period;

	/*! \brief Determines if the Group is using random activation intervals */
	bool randomintervals;

	/*! \brief Determines if the Group is using random activation intensities */
	bool randomintensities;

	/*! \brief Play random Poisson noise with this rate on all channels 
	 * when no stim is active. */
	AurynDouble background_rate;

	/*! \brief Switch for background firing during stimulus. */
	bool background_during_stimulus;

	/*! \brief Default constructor. Patterns can be loaded afterwards using the load_patterns method. 
	 *
	 * \param n Size of the group 
	 * \param stimulusmode Stimulus mode specifies in which order patterns are presented 
	 * \param baserate The base firing rate with which all activity is multiplied. 
	 * */
	RandStimGroup(NeuronID n, StimulusGroupModeType stimulusmode=RANDOM, AurynFloat baserate=1.0 );

	/*! \brief Constructor with an output file for stimtimes. Patterns can be loaded afterwards using the load_patterns method. 
	 *
	 * \param n Size of the group 
	 * \param stimfile The path and filename of the output file used to record the stimulus timing.
	 * \param stimulusmode Stimulus mode specifies in which order patterns are presented 
	 * \param baserate The base firing rate with which all activity is multiplied. 
	 * */
	RandStimGroup(NeuronID n, string stimfile, StimulusGroupModeType stimulusmode=RANDOM, AurynFloat baserate=1.0 );

	virtual ~RandStimGroup();

	/*! \brief Standard virtual evolve function */
	virtual void evolve();

	/*! \brief Sets the baserate that is the rate at 1 activity */
	void set_baserate(AurynFloat baserate);

	/*! \brief Sets the stimulation mode. Can be any of StimulusGroupModeType (MANUAL,RANDOM,SEQUENTIAL,SEQUENTIAL_REV). */
	void set_stimulation_mode(StimulusGroupModeType mode);

	/*! \brief Sets sets the activity of all units */
	void set_all( AurynFloat val=0.0 );

	/*! \brief Seeds the random number generator for all stimulus groups of the simulation. */
	void seed( int rndseed );

	/*! \brief Gets the activity of unit i */
	AurynFloat get_activity(NeuronID i);

	/*! \brief Loads stimulus patterns from a designated pat file given 
	 *
	 * \param filename The path and filename of the pat file to laod. 
	 * */
	virtual void load_patterns(std::vector< std::vector< std::vector<float> > > pat_array);

	/*! \brief Clear stimulus patterns */
	virtual void clear_patterns( );

	/*! \brief Set mean quiet interval between consecutive stimuli */
	void set_mean_off_period(AurynFloat period);

	/*! \brief Set mean on period */
	void set_mean_on_period(AurynFloat period);

	/*! \brief Function that loops over the stimulus/pattern vector and sets the activity verctor to the gamma values given with the pattern. */
	void set_pattern_activity( unsigned int i );

	/*! \brief Function that loops over the stimulus/pattern vector and sets the activity verctor to the given value. */
	void set_pattern_activity( unsigned int i, AurynFloat setval );

	/*! \brief This function is called internally and sets the activity level to a given active stimulus
	 *
	 * @param i the index of the pattern to set the activity to
	 */
	virtual void set_active_pattern( unsigned int i );

	/*! \brief This function is called internally and sets the activity level to a given active stimulus
	 *
	 * @param i The index of the pattern to set the activity to
	 * @param default_value The value to assign to the activity values which are not specified in the pattern file. 
	 * Typically this corresponds to some background value.
	 */
	void set_active_pattern( unsigned int i, AurynFloat default_value);

	void set_next_action_time(double time);

	/*! \brief Setter for pattern probability distribution */
	void set_distribution ( std::vector<double> probs );

	/*! \brief Getter for pattern probability distribution */
	std::vector<double> get_distribution ( );

	/*! \brief Getter for pattern i of the probability distribution */
	double get_distribution ( int i );

	/*! \brief Returns number of stimuli shown */
	unsigned int get_stim_count();


	/*! \brief returns the last action (stim on/off) time in units of AurynTime */
	AurynTime get_last_action_time();

	/*! \brief returns the last stimulus onset time in units of AurynTime */
	AurynTime get_last_onset_time();

	/*! \brief returns the last stimulus offset time in units of AurynTime */
	AurynTime get_last_offset_time();

	/*! \brief returns the next action (stim on/off) time in units of AurynTime */
	AurynTime get_next_action_time();

	/*! \brief returns the index of the current (or last -- if not active anymore) active stimulus */
	unsigned int get_cur_stim();

	/*! \brief Returns true if currently a stimulus is active and false otherwise. */
	bool get_stim_active();

	/*! Initialized distribution to be flat */
	void flat_distribution( );

	/*! Normalizes the distribution */
	void normalize_distribution( );

	std::vector<type_pattern> * get_patterns();

	/*! write current stimulus to stimfile */
	void write_stimulus_file(AurynDouble time);

};

}

#endif /*RANDSTIMGROUP_H_*/
