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

problem: cap destroy: not fixed size operation, have to go through all processes and purge bit
what if instead of destination map, there was a source map, one for each domain? yeah, seems to make sense, though not 100% sure
what implications does this have for limits? can only be referred to by 64, but same is true otherwise
currently, bitmap limits NUMBER OF DOMAINS in system!

New problem: if it isn't completely flat, can't write code
create code from own memory, then unchangeable?
have to clarify alloc semantics
should/can VM operate only on sharp representation?

have to ensure that header/caps aren't overwritten
if target isn't flat, can't write code
unify code and data again?
TODO man, this is weird semantics

btw, NAND makes copying values have 2x overhead if memory not initialized with -1

cap semantics on creation
should it be able to read/write/call itself immediately?

allow for reduction of caps?

could also wrap around IP % len(code) for shits and giggles

TODO can only transfer 1 cap per call
only relative indices?
how do you say "do you have cap for x" otherwise?
