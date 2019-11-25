using MicrosoftResearch.Infer;
using MicrosoftResearch.Infer.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Diagnostics;
using MicrosoftResearch.Infer.Distributions;

namespace InferNetWrapper {

	class MainClass {

		enum NodeType { AND, OR };

		public static void Main(string[] args) {
			var bnetFileName = args[0];
			var dictFileName = args[1];
			var oracleFileName = args[2];

			var dictFile = from line in File.ReadAllLines(dictFileName)
			               let components = line.Split(':')
				           select Tuple.Create(int.Parse(components[0].Trim()), components[1].Trim());
			var dict = dictFile.ToDictionary((indexName) => indexName.Item1, (indexName) => indexName.Item2);

			var tokenStream = new TokenStream(bnetFileName);

			int numNodes = tokenStream.readInt();
			Trace.Assert(numNodes >= 0);

			var allNodeDecls = new List<Tuple<NodeType, double, List<int>>>();
			var queryNodes = new List<int>();
			for (int i = 0; i < numNodes; i++) {
				NodeType nodeType = tokenStream.readString() == "*" ? NodeType.AND : NodeType.OR;
				bool isQueryNode = tokenStream.readString() == "Q";
				double probability = tokenStream.readDouble();
				int numParents = tokenStream.readInt();
				Trace.Assert(numParents >= 0);
				var parents = new List<int> ();
				for (int j = 0; j < numParents; j++) {
					parents.Add(tokenStream.readInt());
				}
				allNodeDecls.Add(Tuple.Create(nodeType, probability, parents));
				if (isQueryNode) {
					queryNodes.Add(i);
				}
			}

			var allNodes = new Dictionary<int, Variable<bool>>();
			var unprocessedNodes = new HashSet<int>();
			for (int i = 0; i < allNodeDecls.Count; i++) {
				unprocessedNodes.Add(i);
			}
			while (unprocessedNodes.Count > 0) {
				var discoveredNode = false;
				foreach (var nodeIndex in unprocessedNodes) {
					var nodeDecl = allNodeDecls[nodeIndex];
					var nodeType = nodeDecl.Item1;
					var probability = nodeDecl.Item2;
					var parents = nodeDecl.Item3;

					if (parents.TrueForAll((parentIndex) => !unprocessedNodes.Contains(parentIndex))) {
						var node = nodeType == NodeType.AND ? Variable.Bernoulli(1) : Variable.Bernoulli(0);
						for (int i = 0; i < parents.Count; i++) {
							var parent = allNodes[parents[i]];
							if (i == 0) {
								node = parent;
							} else {
								node = (nodeType == NodeType.AND) ? (node & parent) : (node | parent);
							}
						}
						if (probability < 1.0) {
							node = parents.Count > 0 ? (node & Variable.Bernoulli(probability)) : Variable.Bernoulli(probability);
						}

						allNodes.Add(nodeIndex, node);
						unprocessedNodes.Remove(nodeIndex);
						discoveredNode = true;
						break;
					}
				}
				Trace.Assert(discoveredNode);
			}
			Console.WriteLine($"Discovered {allNodes.Count} nodes.");

			ExpectationPropagation ep = new ExpectationPropagation();
			InferenceEngine ie = new InferenceEngine(ep);
			Console.WriteLine("IE created!");

			var optimizeForVars = new List<IVariable>();
			foreach (var i in queryNodes) {
				optimizeForVars.Add(allNodes[i]);
			}
			ie.OptimiseForVariables = optimizeForVars;
			Console.WriteLine("Set OptimizeForVariables!");

			while (tokenStream.hasNext()) {
				string queryType = tokenStream.readString();
				if (queryType == "Q") {
					var nodeIndex = tokenStream.readInt();
					var ans = ie.Infer(allNodes[nodeIndex]);
					Console.WriteLine($"{nodeIndex}: ${ans}");
				} else if (queryType == "O") {
					var nodeIndex = tokenStream.readInt();
					var nodeVal = tokenStream.readString();
					if (nodeVal == "true") {
						allNodes[nodeIndex].ObservedValue = true;
					} else if (nodeVal == "false") {
						allNodes[nodeIndex].ObservedValue = false;
					} else {
						Trace.Assert(false);
					}
				} else if (queryType == "NL") {
					Console.WriteLine();
				}
			}
			Console.WriteLine("Observed variables!");

			var sortedAlarms = from nodeIndex in queryNodes
				               let node = allNodes[nodeIndex]
				               let inferAns = (Bernoulli)ie.Infer(node)
				               orderby -inferAns.GetLogProbTrue()
				               select Tuple.Create(nodeIndex, inferAns.GetLogProbTrue());
			var sortedAlarmsList = sortedAlarms.ToList();

			var oracleQueries = File.ReadAllLines(oracleFileName).ToList();

			Console.WriteLine("Rank\tLogProb\tGround\tNodeIndex\tComments\tTuple");
			for (int i = 0; i < sortedAlarmsList.Count; i++) {
				var nodeIndex = sortedAlarmsList[i].Item1;
				var nodeName = dict[nodeIndex];
				var logProb = sortedAlarmsList[i].Item2;

				var ground = oracleQueries.Contains(nodeName) ? "TrueGround" : "FalseGround";
				Console.WriteLine($"{i + 1}\t{logProb}\t{ground}\t{nodeIndex}\tSPOkGoodGood\t{nodeName}");
			}
		}
		
	}

	public class TokenStream {
		
		List<string> tokens;
		int index;

		public TokenStream(string filename) {
			tokens = new List<string>();
			using (var reader = new StreamReader(filename)) {
				string line;
				while ((line = reader.ReadLine()) != null) {
					insertLine(line);
				}
			}
			index = 0;
		}

		void insertLine(string line) {
			var components = line.Split (new char[] { ' ', '\t', '\n' });
			foreach (var c in components.Select((c) => c.Trim()).Where((c) => c.Length > 0)) {
				tokens.Add(c);
			}
		}

		public void populateStdin() {
			/* if (index >= tokens.Count) {
				var nextStdinLine = Console.ReadLine();
				if (nextStdinLine != null) {
					insertLine(nextStdinLine);
				}
			} */
		}

		public bool hasNext() {
			populateStdin();
			return index < tokens.Count;
		}

		public int readInt() {
			return int.Parse(readString());
		}

		public double readDouble() {
			return double.Parse(readString());
		}

		public string readString() {
			populateStdin();
			var ans = tokens[index];
			index++;
			return ans;
		}

	}

}
