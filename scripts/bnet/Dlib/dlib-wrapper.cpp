// Input file format:

// N [Number of nodes]
// N lines follow:
// Line i describes node v_{i - 1}.
// * T p k v1 v2 ... vk, or
// + T p k v1 v2 ... vk
// * or + indicates whether node is a conjunction or disjunction
// T = Q or L indicates whether node is a latent node or a query node, i.e. one on which inference may be performed
// p indicates probability of node correctly firing
// k >= 0 is the number of parents: numbers v1, v2, ..., vk indicate identities of parents

// Any number of query + observation lines may follow:

// A query line is of the form: Q i, indicating a query of the node v_i. v_i has to be a query node.
// An observation line is of the form: O i b, where b = true or false indicates an observation of the node i

#include <cassert>
#include <iostream>
#include <istream>
#include <tuple>
#include <vector>
using namespace std;

#include <dlib/bayes_utils.h>
#include <dlib/graph_utils.h>
#include <dlib/graph.h>
#include <dlib/directed_graph.h>

size_t numNodes;

enum NodeType { AND, OR };

vector<tuple<NodeType, double, vector<size_t>>> nodes;

vector<dlib::assignment> getParentAssignments(size_t i) {
    assert(i < nodes.size());
    const auto& node = nodes[i];
    const auto& parents = get<2>(node);

    vector<vector<bool>> allAssignments = { vector<bool>() };
    for (size_t j = 0; j < parents.size(); j++) {
        const auto& parent = parents[j];
        vector<vector<bool>> newAllAssignments;
        for (const auto& assignment : allAssignments) {
            auto assnT = assignment;
            assnT.push_back(true);
            newAllAssignments.push_back(assnT);
            auto assnF = assignment;
            assnF.push_back(false);
            newAllAssignments.push_back(assnF);
        }
        allAssignments = newAllAssignments;
    }

    vector<dlib::assignment> ans;
    for (const auto& assn : allAssignments) {
        dlib::assignment dassn;
        if (parents.size() != assn.size()) {
            cout << __FILE__ << ": " << __LINE__ << ". " << parents.size() << " " << assn.size() << " " << i << endl;
        }
        assert(parents.size() == assn.size());
        for (size_t i = 0; i < parents.size(); i++) {
            dassn.add(parents[i], assn[i] ? 1 : 0);
        }
        ans.push_back(dassn);
    }
    return ans;
}

int main(int argc, char *argv[]) {
    cin >> numNodes;
    for (size_t i = 0; i < numNodes; i++) {
        NodeType nodeType;
        string typeStr;
        string queryNodeStr;
        double prob;
        size_t numParents;
        vector<size_t> parents;

        cin >> typeStr >> queryNodeStr >> prob >> numParents;
        nodeType = (typeStr == "*") ? AND : OR;
        for (size_t j = 0; j < numParents; j++) {
            size_t parent;
            cin >> parent;
            parents.push_back(parent);
        }

        nodes.push_back(make_tuple(nodeType, prob, parents));
    }

    dlib::directed_graph<dlib::bayes_node>::kernel_1a_c bn;
    bn.set_number_of_nodes(numNodes);
    for (size_t i = 0; i < numNodes; i++) {
        const auto& parents = get<2>(nodes[i]);
        for (size_t j = 0; j < parents.size(); j++) {
            bn.add_edge(parents[j], i);
        }
    }

    for (size_t i = 0; i < numNodes; i++) {
      dlib::bayes_node_utils::set_node_num_values(bn, i, 2);
    }

    for (size_t i = 0; i < numNodes; i++) {
        const auto& node = nodes[i];
        const auto& nodeType = get<0>(node);
        const auto& prob = get<1>(node);

        vector<dlib::assignment> allParentAssignments = getParentAssignments(i);
        assert(allParentAssignments.size() > 0);

        using namespace dlib::bayes_node_utils;

        if (nodeType == AND) {
            set_node_probability(bn, i, 1, allParentAssignments[0], prob);
            set_node_probability(bn, i, 0, allParentAssignments[0], 1 - prob);
            for (size_t j = 1; j < allParentAssignments.size(); j++) {
                set_node_probability(bn, i, 1, allParentAssignments[j], 0);
                set_node_probability(bn, i, 0, allParentAssignments[j], 1);
            }
        } else {
            assert(nodeType == OR);
            for (size_t j = 0; j + 1 < allParentAssignments.size(); j++) {
                set_node_probability(bn, i, 1, allParentAssignments[j], prob);
                set_node_probability(bn, i, 0, allParentAssignments[j], 1 - prob);
            }
            set_node_probability(bn, i, 1, allParentAssignments[allParentAssignments.size() - 1], 0);
            set_node_probability(bn, i, 0, allParentAssignments[allParentAssignments.size() - 1], 1);
        }
    }

    typedef dlib::set<ulong>::compare_1b_c Set;
    typedef dlib::graph<Set, Set>::kernel_1a_c JoinTree;
    JoinTree joinTree;

    create_moral_graph(bn, joinTree);
    create_join_tree(joinTree, joinTree);
    dlib::bayesian_network_join_tree *solution = new dlib::bayesian_network_join_tree(bn, joinTree);

    string commandType;
    while (cin >> commandType) {
        if (commandType == "Q") {
            size_t nodeIndex;
            cin >> nodeIndex;
            cout << solution->probability(nodeIndex)(1) << endl;
        } else if (commandType == "O") {
            size_t nodeIndex;
            string valueStr;
            cin >> nodeIndex >> valueStr;
            int value = valueStr == "true" ? 1 : 0;

            dlib::bayes_node_utils::set_node_value(bn, nodeIndex, value);
            dlib::bayes_node_utils::set_node_as_evidence(bn, nodeIndex);
            delete solution;
            solution = new dlib::bayesian_network_join_tree(bn, joinTree);
        } else if (commandType == "NL") {
            cout << endl;
        } else {
            assert(false);
        }
    }

    delete solution;
    solution = nullptr;
    return 0;
}
