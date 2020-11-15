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

.worker.persistBatch :{[]
				h""
				  
				  
				};

while[1b;.worker.persistBatch[]];
