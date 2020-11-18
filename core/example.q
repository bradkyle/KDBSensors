\l model/model.q
\l state/init.q

// TODO map existing adapters to production effectors

.model.init[]

.z.ts :{
	// Get the next observation from the local
	// state ticker plant
  obs:.state.obs.GetObs[step;.conf.c[`env;`obsWindowSize];aIds]; // TODO make better

	// Run inference on the typescript model 
	action:.model.forward[obs];

	// The adapter takes a given action set and creates
	// the set of events that need to transpire to anneal
	// to this target. The events are then inserted into
	// the pipeline in such a manner that preserves the 
	// temporal coherence of macro actions and the delay
	// in time between the agent and the exchange.
	xevents:.state.adapter.Adapt[action];

	// TODO better logic
	// Send the resultant events to the effector which 
	// proceeds to send them 
	res:.effector.Execute[xevents];

	// Persist events such that post processing/training
	// can be done
	h(`step;(obs;action;xevents;res));
	};
