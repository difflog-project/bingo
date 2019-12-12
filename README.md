The Bingo Interactive Alarm Prioritization System
=================================================

This is the public release of the Bingo interactive alarm prioritization system. The system is presented in the paper
presented at PLDI 2018: [User-Guided Program Reasoning Using Bayesian Inference](https://dl.acm.org/citation.cfm?id=3192417).
In this readme file, we will describe the system workflow, its constituent scripts, and instructions to use them.

**NOTE 1:** The Bingo system is agnostic of the underlying static analysis. Per our description in the PLDI 2018 paper,
we nominally assume that the analysis is expressed in Datalog, but the code distributed here can more generally work
with any analysis that can be conceptualized as consisting of derivation rules, which are repeatedly instantiated until
fixpoint, thus producing output conclusions (a subset of which are the analysis alarms) and a derivation graph linking
them. In the terminology that follows, the alarms are reported in a file named `base_queries.txt`, the analysis rules
are listed in a file called `rule_dict.txt`, and the derivation graph is contained in a file called
`named_cons_all.txt`.

**NOTE 2:** The PLDI 2018 paper describes the operation of Bingo with two backend static analyses: a datarace analysis
for Java programs and a taint analysis for Android apps. Actually running these analyses is somewhat involved.
Furthermore, this intial analysis run is unimportant to anyone wishing to port Bingo to a new analysis of their choice.
In this code distribution, we therefore only include the portion of the workflow after the analysis run has been
completed, the alarms have been reported, and the derivation graph has been extracted.

**NOTE 3:** This respository is still being cleaned up. This will be completed over the next few days. The contents of
this repository are being forked from a previous private repository hosted at
https://bitbucket.org/rmukundroot/commands/src/master/.

System Workflow
---------------

Bingo is architected as a sequence of scripts intended to be run one after the other, where each script performs a small
operation. We assume that all data related to the program being analyzed are stored in a directory named `PROBLEM_DIR`.
These scripts comprising Bingo communicate by creating several files in `PROBLEM_DIR` whose purpose we will now
describe. We have provided an example `PROBLEM_DIR` directory for the `lusearch` benchmark, available by navigating to
the path `bingo/examples/lusearch/`.

Most of the constituent scripts are written in Python. A few small performance-critical pieces of code have been written
in C++.

0. **Analysis Run:** After the analysis run is complete, we assume that the `PROBLEM_DIR` directory contains the
   following files:

   1. `base_queries.txt`. This file contains the list of alarms reported by the analysis. Note that each alarm is
      reported as a tuple, rather than as an error message string. How these tuples map to the actual error message
      presented to the user is an analysis-specific design decision.

      See the `base_queries.txt` file included with the `lusearch` example. This file contains a list of tuples of the
      form `racePairs_cs(x,y)`. Each of these tuples indicates a possible datarace between source location `x` and
      source location `y`. For example, the alarm tuple `racePairs_cs(15502,15503)` may be decoded into the following
      human-readable warning message: "There might be a datarace between bytecode locations 19 and 23 of the method
      `add()` in the class `org.apache.lucene.analysis.CharArraySet`."

      Observe that each tuple is conventionally of the form `RelName(v1,v2,v3,...,vk)`, for some relation name
      `RelName`, and where `v1`, `v2`, ..., `vk` are the fields of the tuple. However, note that this format is merely
      conventional: the only concrete requirements that Bingo makes are that each tuple is represented by a globally
      unique string, and that there are no spaces in this string.

  2. `rule_dict.txt`. Each derivation rule of the analysis is assigned a name, conventionally of the form `Rn`, for some
     number n. The `rule_dict.txt` file contains a mapping between the rule name and the underlying rule. Each line of
     this file contains an element of this mapping in the form `Rn: rule description`. This file is for human
     consumption only, and is not strictly required, and the format is not strictly regulated.

1. **Cycle Elimination (prune-cons):**
