#pragma once

#include <boost/functional/hash.hpp>
#include <boost/lexical_cast.hpp>
using boost::hash_range;
using boost::lexical_cast;

#include <chrono>
#include <ctime>
#include <iostream>
#include <vector>
using namespace std;

string nowstr() {
    auto today = chrono::system_clock::now();
    time_t tt = chrono::system_clock::to_time_t(today);
    string ans = ctime(&tt);
    return ans.substr(0, ans.size() - 1);
}

#define __LOGSTR__ (nowstr() + " " + __FILE__ + ": " + lexical_cast<string>(__LINE__) + ". ")

template <typename T>
struct vector_hash {
    size_t operator()(const vector<T>& v) const {
        return hash_range(v.begin(), v.end());
    }
};

template <typename T>
ostream& operator<<(ostream& stream, const vector<T>& v) {
    for (size_t i = 0; i + 1 < v.size(); i++) {
        stream << v[i] << ", ";
    }

    if (v.size() > 0) {
        stream << v[v.size() - 1];
    }

    return stream;
}

template <typename T>
T setPop(unordered_set<T> *u) {
    T t = *u->begin();
    u->erase(u->begin());
    return t;
}
