only metering relation is hierarchical, processes are created in the same space - but can't call each other? how will that work
reify access via capabilities - but cap system should be implemented within, not on the substrate
can only call parent meter?
or DO provide simple cap system? what else other than access is needed?
RECURSE instruction has memory cost! (say, 3 words for overhead->index,gas,mem)
but only if theres metadata that isnt contained in process snapshot, which there isn't!
ideally, not only memory requirements of process image, but runtime representation as well, if its worse
vm implemented in itself, then measure?

creator gets cap: which is index!
so RECURSE gets cap argument!!!
the (only) problem i see here is the non-fixed-size header which makes this a bit awkward
UNLESS
it's a bit field!
then every process could have, say 64 caps/references
ah, keykos had capability to capability table
ah, i see, a fixed limit kind of, but not really limits the number of subprocs a process can create in sequence, without passing down other caps

read vs write caps

flat vs hierarchy
not sure what advantages of hierarchy are

TODO research dynamic instruction format optimization, e.g. omit caps
