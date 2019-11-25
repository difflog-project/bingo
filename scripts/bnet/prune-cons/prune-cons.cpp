#include <boost/algorithm/string/predicate.hpp>
using boost::starts_with;

#include <algorithm>
#include <cassert>
#include <chrono>
#include <ctime>
#include <iostream>
#include <iterator>
#include <limits>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <fstream>
using namespace std;

#include "util.h"

string lit2Tuple(const string& literal) {
    if (starts_with(literal, "NOT ")) { return literal.substr(4); }
    else { return literal; }
}

vector<string> clause2Antecedents(const vector<string>& clause) {
    if (clause.size() > 1) {
        vector<string> ans(&clause[0], &clause[clause.size() - 1]);
        assert(clause.size() == ans.size() + 1);
        transform(ans.begin(), ans.end(), ans.begin(), &lit2Tuple);
        return ans;
    } else { return vector<string>(); }
}

string clause2Consequent(const vector<string>& clause) {
    string ans = clause[clause.size() - 1];
    assert(!starts_with(ans, "NOT "));
    return ans;
}

size_t maxAntecedentDob(const vector<string>& clause, const unordered_map<string, size_t>& tupleDob) {
    size_t ans = 0;
    for (const auto& literal : clause2Antecedents(clause)) {
        ans = max(ans, tupleDob.at(lit2Tuple(literal)));
    }
    return ans;
}

unordered_map<string, size_t> computeTupleDob(const set<vector<string>>& allClauses,
                                              const set<string>& allTuples,
                                              const set<string>& allInputTuples) {
    unordered_map<string, size_t> tupleDob;
    for (const auto& t : allTuples) {
        tupleDob[t] = allInputTuples.find(t) == allInputTuples.end() ? numeric_limits<size_t>::max() : 0;
    }

    size_t numChanged = 1;
    while (numChanged > 0) {
        numChanged = 0;
        for (const auto& clause : allClauses) {
            auto consequent = clause2Consequent(clause);
            size_t newDob = maxAntecedentDob(clause, tupleDob);
            if (newDob < numeric_limits<size_t>::max()) { newDob++; }
            if (newDob < tupleDob[consequent]) {
                numChanged++;
                tupleDob[consequent] = newDob;
            }
        }
    }

    size_t maxDob = 0, unreachableTuples = 0;
    for (const auto& tupleDobPair : tupleDob) {
        maxDob = max(maxDob, tupleDobPair.second);
        if (tupleDobPair.second == numeric_limits<size_t>::max()) {
            unreachableTuples++;
        }
    }
    clog << __LOGSTR__ << "Last (not necessarily useful) tuple birted at epoch " << maxDob << "." << endl;
    assert(unreachableTuples == 0);

    return tupleDob;
}

// The ancestors of a clause includes its antecedents
// The descendants of a clause includes its consequents
template <typename T, typename U, typename V>
bool ancestorsDescendantsDisjoint(
        const vector<vector<string>>& rootClauses,
        const unordered_set<vector<string>, T>& augFwdClauses,
        const unordered_map<string, unordered_set<vector<string>, U>>& tuple2AntecedentClauses,
        const unordered_map<string, unordered_set<vector<string>, V>>& tuple2ConsequentClauses,
        __attribute__((unused)) const string& indent
) {
    unordered_set<string> processedAncestors;
    unordered_set<string> unprocessedAncestors;
    for (const auto& clause : rootClauses) {
        for (const auto& t : clause2Antecedents(clause)) {
            unprocessedAncestors.insert(t);
        }
    }

    unordered_set<string> processedDescendants;
    unordered_set<string> unprocessedDescendants;
    for (const auto& clause : rootClauses) {
        auto consequent = clause2Consequent(clause);
        unprocessedDescendants.insert(consequent);
        if (unprocessedAncestors.find(consequent) != unprocessedAncestors.end()) { return false; }
    }

    while (!unprocessedAncestors.empty() || !unprocessedDescendants.empty()) {
        size_t numAncestors = processedAncestors.size() + unprocessedAncestors.size();
        size_t numDescendants = processedDescendants.size() + unprocessedDescendants.size();
        bool dequeueAncestor = unprocessedDescendants.empty() ||
                             (!unprocessedAncestors.empty() && numAncestors < numDescendants);

        if (dequeueAncestor) {
            const auto t = setPop(&unprocessedAncestors);

            for (const auto& clause : tuple2ConsequentClauses.at(t)) {
                if (augFwdClauses.find(clause) != augFwdClauses.end()) {
                    for (const auto& antecedent : clause2Antecedents(clause)) {
                        if (processedAncestors.find(antecedent) == processedAncestors.end() &&
                            unprocessedAncestors.find(antecedent) == unprocessedAncestors.end()) {
                            if (processedDescendants.find(antecedent) != processedDescendants.end() ||
                                unprocessedDescendants.find(antecedent) != unprocessedDescendants.end()) {
                                return false;
                            }
                            unprocessedAncestors.insert(antecedent);
                        }
                    }
                }
            }

            processedAncestors.insert(t);
        } else {
            const auto t = setPop(&unprocessedDescendants);

            for (const auto& clause : tuple2AntecedentClauses.at(t)) {
                if (augFwdClauses.find(clause) != augFwdClauses.end()) {
                    const auto consequent = clause2Consequent(clause);
                    if (processedDescendants.find(consequent) == processedDescendants.end() &&
                        unprocessedDescendants.find(consequent) == unprocessedDescendants.end()) {
                        if (processedAncestors.find(consequent) != processedAncestors.end() ||
                            unprocessedAncestors.find(consequent) != unprocessedAncestors.end()) {
                            return false;
                        }
                        unprocessedDescendants.insert(consequent);
                    }
                }
            }

            processedDescendants.insert(t);
        }
    }

    return true;
}

template <typename T1, typename T2, typename T3, typename T4>
void augmentInt(
        const set<vector<string>>& allClauses,
        const unordered_set<vector<string>, T1>& fwdClauses,
        const unordered_map<string, unordered_set<vector<string>, T2>>& tuple2AntecedentClauses,
        const unordered_map<string, unordered_set<vector<string>, T3>>& tuple2ConsequentClauses,
        const vector<vector<string>>& nonFwdClauses,
        size_t beginIndex, size_t endIndex,
        unordered_set<vector<string>, T4> *augmentedFwdClauses,
        string indent = ""
) {
    assert(beginIndex < nonFwdClauses.size());
    assert(beginIndex <= endIndex);
    assert(endIndex <= nonFwdClauses.size());
    clog << __LOGSTR__ << indent << "augmentInt(" << beginIndex << ", "
                                                  << endIndex << ": "
                                                  << endIndex - beginIndex << ")" << endl;
    clog << __LOGSTR__ << indent << "augmentedFwdClauses->size(): " << augmentedFwdClauses->size() << endl;

    if (beginIndex == endIndex) { return; }

    vector<vector<string>> rootClauses(nonFwdClauses.begin() + beginIndex, nonFwdClauses.begin() + endIndex);

    if (ancestorsDescendantsDisjoint(rootClauses, *augmentedFwdClauses,
                                     tuple2AntecedentClauses, tuple2ConsequentClauses, indent)) {
        clog << __LOGSTR__ << indent << "augFwdClauses remains non-circular." << endl;
        copy(rootClauses.begin(), rootClauses.end(), inserter(*augmentedFwdClauses, augmentedFwdClauses->end()));
    } else {
        clog << __LOGSTR__ << indent << "augFwdClauses would become circular." << endl;
        if (beginIndex + 1 == endIndex) {
            clog << __LOGSTR__ << indent << "Discovered backward clause: " << nonFwdClauses[beginIndex] << endl;
            return;
        }

        size_t mid = (beginIndex + endIndex) / 2;
        augmentInt(allClauses, fwdClauses, tuple2AntecedentClauses, tuple2ConsequentClauses, nonFwdClauses,
                   beginIndex, mid, augmentedFwdClauses, indent + "  ");
        augmentInt(allClauses, fwdClauses, tuple2AntecedentClauses, tuple2ConsequentClauses, nonFwdClauses,
                   mid, endIndex, augmentedFwdClauses, indent + "  ");
    }
}

template <typename T1, typename T2, typename T3>
unordered_set<vector<string>, vector_hash<string>> augment(
        const set<vector<string>>& allClauses,
        const unordered_set<vector<string>, T1>& fwdClauses,
        const unordered_map<string, unordered_set<vector<string>, T2>>& tuple2AntecedentClauses,
        const unordered_map<string, unordered_set<vector<string>, T3>>& tuple2ConsequentClauses
) {
    vector<vector<string>> nonFwdClauses;
    for (const auto& clause : allClauses) {
        if (fwdClauses.find(clause) == fwdClauses.end()) { nonFwdClauses.push_back(clause); }
    }

    unordered_set<vector<string>, vector_hash<string>> augmentedFwdClauses(fwdClauses.begin(), fwdClauses.end());
    // for (const auto& clause : fwdClauses) { ans.insert(clause); }
    augmentInt(allClauses, fwdClauses, tuple2AntecedentClauses, tuple2ConsequentClauses, nonFwdClauses,
               0, nonFwdClauses.size(), &augmentedFwdClauses);
    return augmentedFwdClauses;
}

int main(int argc, char *argv[]) {
    clog << __LOGSTR__ << "Hello!" << endl;
    if (argc < 3) {
        cerr << __LOGSTR__ << "Insufficient arguments!" << endl
                           << "./prune-cons augment opTupleFileName" << endl
                           << "where augment = \"augment\" or \"noaugment\" indicates whether to "
                           << "augment forward clauses" << endl;
        return 1;
    }
    bool doAugment = (string(argv[1]) == "augment");
    string opTupleFileName = argv[2];

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 1. Accept input

    set<vector<string>> allClauses;
    map<vector<string>, string> allRuleNames;

    string inputLine;
    while (getline(cin, inputLine)) {
        istringstream inputLineStream(inputLine);

        string ruleName;
        inputLineStream >> ruleName;
        ruleName.pop_back();

        vector<string> clause;

        string token;
        bool lastNot = false;
        while (inputLineStream >> token) {
            if (token == "NOT") {
                lastNot = true;
            } else {
                if (token[token.size() - 1] == ',') {
                    token.pop_back();
                }
                clause.push_back(lastNot ? "NOT " + token : token);
                lastNot = false;
            }
        }

        assert(clause.size() >= 1);
        allClauses.insert(clause);
        allRuleNames[clause] = ruleName;
    }
    clog << __LOGSTR__ << "Loaded " << allClauses.size() << " clauses." << endl;

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 2. Compute all tuples and consequents,

    set<string> allTuples;
    set<string> allConsequents;

    for (const auto& clause : allClauses) {
        for (const auto& literal : clause) {
            allTuples.insert(lit2Tuple(literal));
        }

        allConsequents.insert(clause2Consequent(clause));
    }

    clog << __LOGSTR__ << "Discovered " << allTuples.size() << " tuples." << endl;
    clog << __LOGSTR__ << "Discovered " << allConsequents.size() << " consequents." << endl;

    // all input and output tuples,

    set<string> allInputTuples;
    set_difference(allTuples.begin(), allTuples.end(),
                   allConsequents.begin(), allConsequents.end(),
                   inserter(allInputTuples, allInputTuples.end()));
    clog << __LOGSTR__ << "Discovered " << allInputTuples.size() << " input tuples." << endl;

    unordered_set<string> allOutputTuples;
    ifstream opTupleFile(opTupleFileName);
    string tup;
    while (opTupleFile >> tup) allOutputTuples.insert(tup);
    clog << __LOGSTR__ << "Loaded " << allOutputTuples.size() << " output tuples." << endl;

    for (const auto& t : allOutputTuples) {
        assert(allConsequents.find(t) != allConsequents.end());
    }

    // and map each tuple to the clauses in which it appears.

    unordered_map<string, unordered_set<vector<string>, vector_hash<string>>> tuple2AntecedentClauses;
    unordered_map<string, unordered_set<vector<string>, vector_hash<string>>> tuple2ConsequentClauses;

    for (const auto& t : allTuples) {
        tuple2AntecedentClauses[t] = unordered_set<vector<string>, vector_hash<string>>();
        tuple2ConsequentClauses[t] = unordered_set<vector<string>, vector_hash<string>>();
    }

    for (const auto& clause : allClauses) {
        for (size_t i = 0; i + 1 < clause.size(); i++) {
            const auto& t = lit2Tuple(clause[i]);
            tuple2AntecedentClauses[t].insert(clause);
        }
        tuple2ConsequentClauses[clause2Consequent(clause)].insert(clause);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 3. Compute dates of birth of each tuple, and the set of forward clauses

    const auto tupleDob = computeTupleDob(allClauses, allTuples, allInputTuples);
    unordered_set<vector<string>, vector_hash<string>> fwdClauses;
    for (const auto& clause : allClauses) {
        if (maxAntecedentDob(clause, tupleDob) < tupleDob.at(clause2Consequent(clause))) {
            fwdClauses.insert(clause);
        }
    }
    clog << __LOGSTR__ << "Discovered " << fwdClauses.size() << " forward clauses." << endl;

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 4. Augment the set of forward clauses

    const auto augFwdClauses = doAugment ?
                               augment(allClauses, fwdClauses, tuple2AntecedentClauses, tuple2ConsequentClauses) :
                               fwdClauses;
    clog << __LOGSTR__ << "Discovered " << augFwdClauses.size() << " augmented forward clauses." << endl;

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 5. Compute the set of coreachable tuples

    unordered_set<string> coreachableTuples = allOutputTuples;

    unordered_set<string> unprocessedTuples = coreachableTuples;
    while (!unprocessedTuples.empty()) {
        const auto t = setPop(&unprocessedTuples);
        for (const auto& clause : tuple2ConsequentClauses.at(t)) {
            assert(t == clause2Consequent(clause));
            if (augFwdClauses.find(clause) != augFwdClauses.end()) {
                for (const auto& tPrime : clause2Antecedents(clause)) {
                    if (coreachableTuples.find(tPrime) == coreachableTuples.end()) {
                        unprocessedTuples.insert(tPrime);
                    }
                }
            }
        }
        coreachableTuples.insert(t);
    }

    clog << __LOGSTR__ << "Discovered " << coreachableTuples.size() << " coreachable tuples." << endl;

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 6. Compute the set of active clauses

    unordered_set<vector<string>, vector_hash<string>> activeClauses;
    for (const auto& clause : augFwdClauses) {
        const auto consequent = clause2Consequent(clause);
        if (coreachableTuples.find(consequent) != coreachableTuples.end()) {
            activeClauses.insert(clause);
        }
    }
    clog << __LOGSTR__ << "Discovered " << activeClauses.size() << " active clauses." << endl;

    for (const auto& clause : activeClauses) {
        cout << allRuleNames[clause] << ": " << clause << endl;
    }

    clog << __LOGSTR__ << "Bye!" << endl;
    return 0;
}
