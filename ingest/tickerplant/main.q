
events:([eId: `long$()]
	intime:`datetime$();
	time:`time$();  
	source:`symbol$();
	chan:`symbol$();
	entity:`symbol$();
	datum:();
	);


// get batch, used by hdb  
.worker.getbatch :{[batchSize]
	  
	  };

// remove events from events table
.worker.ackbatch :{[eventIds]
	delete from `events where eId in eventIds;
	};


// add an event to the 
.worker.addevents :{[e]
		  
	};


