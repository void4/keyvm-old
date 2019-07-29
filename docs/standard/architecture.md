# Architecture

## General properties

KeyVM is a stack-based architecture, single-threaded (control only resides at one place at a time) and deterministic (a copy of the program state with the same input will always create the same results, down to the bit). The runtime state is a list of processes. The VM is ''stateless'', all data necessary to restore a process resides in the process image.

## Distinguishing features

The CREATE instruction is used to create a new process from one of the processes' memories. The creating process receives a key to the newly created process.

The RECURSE instruction can be invoked to transfer control to another process image in the list. Each process is assigned resource limits: instruction steps/time ('gas') and a memory allocation limit and/or memory-time cost (cost per word per timestep).

The TRANSFERKEY instruction can be used to give another process the right to call a process the current domain already has access to.
