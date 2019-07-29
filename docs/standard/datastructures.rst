Data Structures
===============

The world consists of a list of processes.

A process consists of a

* read-only header (contains status, available resources, and instruction pointer)
* read-only key list (a list of all processes it can call)
* code (a list of instructions)
* data (a list of linear memories)
* a stack (used for computation)
