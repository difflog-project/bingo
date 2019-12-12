The Bingo Interactive Alarm Prioritization System
=================================================

This is the public release of the Bingo interactive alarm prioritization system. The system is presented in the paper
presented at PLDI 2018: [User-Guided Program Reasoning Using Bayesian Inference](https://dl.acm.org/citation.cfm?id=3192417).
In this readme file, we will describe the system architecture, its constituent scripts, and instructions to use them.

**NOTE 1:** The Bingo system is agnostic of the underlying static analysis. Per our description in the PLDI 2018 paper,
we nominally assume that the analysis is expressed in Datalog, but the code distributed here can more generally work
with any analysis that can be conceptualized as consisting of derivation rules, which are repeatedly instantiated until
fixpoint, thus producing output conclusions (a subset of which are the analysis alarms) and a derivation graph linking
them. In the terminology that follows, the set of rules is specified in a file called `rule_dict.txt`, and the
derivation graph is contained in a file called `named_cons_all.txt`.

**NOTE 2:** The PLDI 2018 paper describes the operation of Bingo with two backend static analyses. Actually running
these analyses is somewhat involved. Furthermore, this intial analysis run is unimportant to anyone wishing to port
Bingo to a new analysis of their choice. In this code distribution, we therefore only include the portion of the
workflow after the analysis run has been completed and the derivation graph has been extracted. We assume that
`rule_dict.txt` and `named_cons_all.txt` already exist.

**NOTE 3:** This respository is still being cleaned up. This will be completed over the next few days. The contents of
this repository are being forked from a previous private repository hosted at
https://bitbucket.org/rmukundroot/commands/src/master/.
