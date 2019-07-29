# Bytecode

| Instruction | Description |
|-------------|-------------|
| CREATE | Create a new process from the given <memory> |
| ALLOC | Allocate <size> words at the end of <memory> |
| TRANSFERKEY | Transfer the key <transferkeyindex> to the process pointed to by <targetkeyindex>			Should probably be renamed, because it rather "copies" the key |
| RECURSE |  |
| MEMSIZE |  |
| MEMWRITE |  |
| MEMCREATE |  |
| ADD |  |
| SUB |  |
| MUL |  |
| DIV |  |
| JUMP |  |
| JUMPIF |  |
| CODEREAD |  |
| CODELEN |  |
| PUSH |  |
| DUP |  |
| MEMPUSH |  |
| FORK | memory = pop1() |
| HALT |  |
| RETURN |  |
| RANDOM |  |



For more, see instructions.py
