# asu-cse-520
**Computer Architecture II at Arizona State University Summer of 2019**

Professor: Aviral Shrivastava

TA: Mahesh Balasubramanian

Grade: B

---

This was effectively a chip design class where in addition to quizzes, two mid-terms test, and a final exam we:

- refreshed our understanding of MIPS Assembly Language including:
    - pipelining
    - structural, data, and control hazards and workarounds such as:
    - delayed decision, predication, reducing branches, branch hinting, out of order execution, and speculative execution

- used the [gem5 Simulator](https://www.gem5.org/) to mimic an on-chip environment where we studied on-chip memory including:
  - direct-mapped caches
  - set-associate cachesvirtual memory
- ultimately we were assigned three programming projects which were written in C/C++ and run using the [gem5 Simulator](https://www.gem5.org/):
  - Project 1 - becoming familiar with gem5 and learning the implications of different cache configurations
  - Project 2 - understanding gem5 branch predictor structure
  - Project 3 - understanding gem5 cache structure where we were tasked to write a cache replacement program that implemented the "tree-based pseudoLRU replacement" concept set forth in - *but not formulated in* - [Insertion and Promotion for Tree-Based PsueudoLRU Last-Level Caches](https://www.bing.com/ck/a?!&&p=ff2b7446df13c6afJmltdHM9MTY5MTAyMDgwMCZpZ3VpZD0wYzhhMWY5Ni1jNjdkLTZmMzYtMDhjMS0wZGVkYzc4ODZlMzAmaW5zaWQ9NTE5MA&ptn=3&hsh=3&fclid=0c8a1f96-c67d-6f36-08c1-0dedc7886e30&psq=Insertion+and+Promotion+for+Tree-Based+PseudoLRU+Last-Level+Caches+Daniel+A.+Jim%c3%a9nez&u=a1aHR0cHM6Ly9wZW9wbGUuZW5nci50YW11LmVkdS9kamltZW5lei9wZGZzL3AyODQtamltZW5lei5wZGY&ntb=1) by Daniel A. Jimenez
