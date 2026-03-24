SATLIB - Benchmark Problems

# Uniform Random-3-SAT

Uniform Random-3-SAT is a family of SAT problems distributions obtained by randomly generating 3-CNF formulae in the following way: For an instance with _n_ variables and _k_ clauses, each of the _k_ clauses is constructed from 3 literals which are randomly drawn from the _2n_ possible literals (the _n_ variables and their negations) such that each possible literal is selected with the same probability of _1/2n_. Clauses are not accepted for the construction of the problem instance if they contain multiple copies of the same literal or if they are tautological (i.e., they contain a variable and its negation as a literal). Each choice of _n_ and _k_ thus induces a distribution of Random-3-SAT instances. Uniform Random-3-SAT is the union of these distributions over all _n_ and _k_.

#### Forced vs. unforced generation

Random-3-SAT instances can be satisfiable or unsatisfiable. Since the behaviour of SAT algorithms can be expected to differ significantly between satisfiable and unsatisfiable instances, we seperated these into different test-sets using a complete algorithm. As complete SAT algorithms have usually considerable higher run-times than (incomplete) SLS algorithms, this approach for generating benchmark problems is computationally very expensive, especially when dealing with larger problem sizes. Therefore, especially when dealing with satisfiable instances, it would be preferable to generate the instances in a way such that their satisfiability (or unsatisfiability) is guaranteed by construction.

For generating satisfiable instances, one possibility for achieving this is to randomly determine a variable assignment _B_ at the beginning of the generation process. Then, the clauses are generated as before, but only clauses which are compatible with _B_ (i.e., clauses which have _B_ as a model) are accepted for the formula _F_ to be constructed. Thus, _F_ has at least one model (namely _B_). The problem distributions thus obtained are called \`\`forced'' uniform Random-3-SAT problems; earlier literature on SLS algorithms for SAT used these for evaluating algorithms, until it was noticed that these problems tend to be much easier to solve for SLS algorithms then \`\`unforced'' problems obtained as described before. It has been speculated for some time that the reason for this phenomenon might be that in forced formulae, the clause are somehow guiding the SLS algorithm into the right direction.

#### Phase transitions

One particularly interesting property of uniform Random-3-SAT is the occurence of a phase transition phenomenon \[CKT91\], i.e., a rapid change in solubility which can be observed when systematically increasing (or decreasing) the number of _k_ clauses for fixed problem size _n_. More precisely, for small _k_ almost all formulae are satisfiable; at some critical _k=k'_, the probability of generating a satisfiable instance drops sharply to almost zero. Beyond _k'_, almost all instances are unsatisfiable. Intuitively, _k'_ characterises the transition between a region of underconstrained instances which are almost certainly soluble, to overconstrained instanced which are mostly insoluble. For Random-3-SAT, this phase transition occurs approximately at _k' = 4.26 n_ for large _n_; for smaller _n_, the critical clauses/variable ratio _k'/n_ is slightly higher. Furthermore, for growing _n_ the transition becomes increasingly sharp. The phase transition would not be very interesting in the context of evaluating SLS algorithms, didn't empirical analyses show that problems from the phase transition region of uniform Random-3-SAT tend to be particularly hard for both systematic SAT solvers and SLS algorithms . Striving for testing their algorithms on hard problem instances, many researchers used test-sets sampled from the phase transition region of uniform Random-3-SAT (see for some examples). Although, similar phase transition phenomena have been observed for other subclasses of SAT, including uniform Random-_k_\-SAT with _k >= 4_, but these have never gained the popularity of uniform Random-3-SAT . Maybe, one of the reasons for this is the the prominent role of 3-SAT as a prototypical and syntactically particularly simple NP-complete problem.  

#### The benchmark test-sets

The test-sets provided here are sampled from the phase transition region of uniform Random-3-SAT. The instances were generated in an unforced way and were separated into test-sets of satisfiable and unsatisfiable instances . The characteristics of these test-sets are shown in Table 1. The smallest problems (20 variables) are typically used for studying scaling properties. Due to limited computational resources, only the test-sets for n=20,50,100 contain 1000 instances, while for larger problem sizes each test-set contains 100 instances.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **test-set** | **instances** | **clause-len** | **vars** | **clauses** |
| uf20-91 | 1000 | 3   | 20  | 91  |
| uf50-218 / uuf50-218 | 1000 | 3   | 50  | 218 |
| uf75-325 / uuf75-325 | 100 | 3   | 75  | 325 |
| uf100-430 / uuf100-430 | 1000 | 3   | 100 | 430 |
| uf125-538 / uuf125-538 | 100 | 3   | 125 | 538 |
| uf150-645 / uuf150-645 | 100 | 3   | 150 | 645 |
| uf175-753 / uuf175-753 | 100 | 3   | 175 | 753 |
| uf200-860 / uuf200-860 | 100 | 3   | 200 | 860 |
| uf225-960 / uuf225-960 | 100 | 3   | 225 | 960 |
| uf250-1065 / uuf250-1065 | 100 | 3   | 250 | 1065 |

**Table 1:** Uniform Random-3-SAT test-sets; test-sets uf\* contain only satisfiable instances, uuf\* only unsatisfiable instances.

  

#### Bibliography

|     |     |
| --- | --- |
| \[CKT91\] | _Peter Cheeseman and Bob Kanefsky and William M. Taylor_ **[Where the really hard problems are](http://ic-www.arc.nasa.gov/fia/projects/bayes-group/group/NP/ijcai91/paper/IJCAI91-paper.html).** Proc. IJCAI-91, pages 331--337, 1991 |