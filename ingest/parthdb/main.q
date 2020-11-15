\c 10 300
\cd kdb-common
\l src/require.q
.require.init[];
\l src/file.q
\l src/ipc.q
\cd ../


// Main HDB logic
args:.Q.opt[.z.x];
tport:first"J"$args[`tport];
batchsize:first"J"$args[`batchsize];
outpath:first `$args[`outpath];
interval:first "J"$args[`interval];
show args;

.worker.write:{[outpath;x]  
      x:(0!(`utc_day`source`inst`chan xgroup x));
      {
        path:(` sv x,(`$string[y[`utc_day]]),y[`source],y[`inst],y[`chan],`$"");
        path upsert .Q.en[`:db;] flip[y];
      }[outpath]'[x]; 
  };


.worker.persistBatch :{[args]
	h:.ipc.connect[args`port];  
	batch:h("getbatch";args`batchsize);
	$[count[batch]>0;[
				.worker.write[args`outpath;batch]
			];[
				show "Empty Batch";	
			]];
	h("ackbatch";batch[`eid]);
	};

while[1b;@[.worker.persistBatch;args;show]];
