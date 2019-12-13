The Bingo Interactive Alarm Prioritization System
=================================================

This is the public release of the Bingo interactive alarm prioritization system. The system is presented in the paper
presented at PLDI 2018: [User-Guided Program Reasoning Using Bayesian Inference](https://dl.acm.org/citation.cfm?id=3192417).
In this readme file, we will describe the system workflow, its constituent scripts, and instructions to use them.

**NOTE 1:** The Bingo system is agnostic of the underlying static analysis. Per our description in the PLDI 2018 paper,
we nominally assume that the analysis is expressed in Datalog. However, the code we provide here can more generally work
with any analysis that can be conceptualized as consisting of derivation rules which are repeatedly instantiated until
fixpoint. In particular, we require that the analysis produces a set of output conclusions (a subset of which are
reported to the user as warnings) and a derivation graph which connects them together. In the terminology that follows,
the alarms are reported in a file named `base_queries.txt`, the analysis rules are listed in a file called
`rule_dict.txt`, and the derivation graph is contained in a file called `named_cons_all.txt`.

**NOTE 2:** The PLDI 2018 paper describes the operation of Bingo with two backend static analyses: a datarace analysis
for Java programs and a taint analysis for Android apps. Running these specific analyses is a somewhat involved process.
Furthermore, this intial analysis run is unimportant to anyone wishing to port Bingo to a new analysis of their choice.
In this code distribution, we therefore only include the portion of the workflow after the analysis run has been
completed, the alarms have been reported, and the derivation graph has been extracted.

**NOTE 3:** This respository is still being cleaned up. This will be completed over the next few days. The contents of
this repository are being forked from a previous repository which is privately hosted at
https://bitbucket.org/rmukundroot/commands/src/master/.

Building Bingo
--------------

Bingo is mostly written in Python. A few small performance-critical pieces of code have been written in C++. The core of
Bingo crucially depends on the LibDAI inference library, which the build script will clone itself. Ensure that you have
the Boost C++ libraries and the gmpxx wrapper to the GMP library installed. On Ubuntu, the appropriate dependencies can
be installed by running:
```
sudo apt install libboost-dev libboost-program-options-dev libboost-test-dev libgmp-dev
```
Now, build Bingo by running:
```
./scripts/build.sh
```
from the main Bingo directory.

System Workflow
---------------

Bingo is architected as a sequence of small scripts intended to be run one after the other. We assume that all data
related to the program being analyzed are stored in a directory named `PROBLEM_DIR`. These scripts comprising Bingo
communicate by creating several files in `PROBLEM_DIR` whose purpose we will now describe. We have provided an example
`PROBLEM_DIR` directory for the `lusearch` benchmark, available by navigating to the path `bingo/examples/lusearch/`:
these are the warnings generated by a static datarace detector when applied to a program from the Dacapo benchmark
suite.

0. **Analysis Run:** After the analysis run is complete, we assume that the `PROBLEM_DIR` directory contains the
   following files:

   1. `base_queries.txt`. This file contains the list of alarms reported by the analysis. Note that each alarm is
      listed in the form of a tuple, rather than as the warning message string presented to the user. Each tuple is of
      the form `RelName(v1,v2,v3,...,vk)`, for some relation name `RelName`, and where `v1`, `v2`, ..., `vk` are the
      fields of the tuple. However, note that this format is merely conventional: the only concrete requirements that
      Bingo makes are that each tuple is represented by a globally unique string, and that there are no spaces in this
      string.

      See the `base_queries.txt` file included with the `lusearch` example. This file contains a list of tuples of the
      form `racePairs_cs(x,y)`. Each of these tuples indicates a possible datarace between source location `x` and
      source location `y`. For example, the alarm tuple `racePairs_cs(15562,15645)` may be decoded into the following
      human-readable warning message: "There may be a datarace between the field accesses at line 40 of the file
      `org/apache/lucene/analysis/LowerCaseFilter.java` and at line 685 of the file
      `org/apache/lucene/analysis/Token.java`." The file `racePairs_cs.txt` contains the corresponding human-readable
      warning messages. In general, how the alarm tuples map to the actual warning message is an analysis-specific
      design decision.

      Of the 237 alarms in the `lusearch` example, only the four alarms listed in `oracle_queries.txt` are real bugs. Of
      course, when analyzing a new program, the user is unaware of which alarms are real bugs and which are false
      positives: we can only provide `oracle_queries.txt` for the example problem because we have laboriously triaged
      each of the alarms.

   2. `rule_dict.txt`. Each derivation rule of the analysis is assigned a name, conventionally of the form `Rn`, for
      some number n. The `rule_dict.txt` file contains a mapping between the rule name and the underlying rule. Each
      line of this file contains an element of this mapping in the form `Rn: rule description`. This file is for human
      consumption only, and is not strictly required, and the format is not strictly regulated.

   3. `named_cons_all.txt`. This file contains the derivation graph. Each line of the form
      `Rn: NOT h1, NOT h2, ..., NOT hk, t`. Here `Rn` is the name of the rule, which can be instantiated to produce the
      concrete constraint (not `h1` or not `h2` or ... or not `hk` or `t`). This is equivalent to writing (`h1` and `h2`
      and ... and `hk`) => `t`. In other words, the rule `Rn` can be instantiated to produce the output conclusion `t`
      from the input hypotheses `h1`, `h2`, ..., `hk`. We assume that tuples which are not the conclusion of any rule
      instantiation are facts about the program which have been supplied as input to the analysis (also called the EDB).

1. **Cycle Elimination (prune-cons):** The constraints in `named_cons_all.txt` can be visualized as forming a derivation
   graph, such as those shown in Figures 3, 4 and 6 of the PLDI 2018 paper. The nature of Datalog fixpoints means that
   the graph routinely contains multiple ways to derive a single output tuple and various pathological structures such
   as cycles. The first step is to eliminate these cycles

2. **Converting the Derivation Graph into a Bayesian Network (cons_all2bnet.py):** Makes disjunctions explicit.

3. **Converting the Bayesian Network into a Factor Graph (bnet2fg.py):**

4. **Main Bingo Interaction Loop (driver.py):**

**NOTE:** `build-bnet.sh`
