package chord.analyses.mln.datarace;

import static chord.util.RelUtil.pRel;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import chord.analyses.alias.Ctxt;
import chord.analyses.alias.DomC;
import chord.analyses.mln.ConstraintItem;
import chord.analyses.mln.MLNAnalysisDriver;
import chord.analyses.ursa.classifier.AllFalseClassifier;
import chord.analyses.ursa.classifier.BaggedClassifier;
import chord.analyses.ursa.classifier.Classifier;
import chord.analyses.ursa.classifier.datarace.DynamicAnalysisClassifier;
import chord.analyses.ursa.classifier.datarace.HandCraftedClassifier;
import chord.bddbddb.Dom;
import chord.project.Chord;
import chord.project.ClassicProject;
import chord.project.Config;
import chord.project.ITask;
import chord.project.analyses.ProgramRel;
import chord.project.analyses.provenance.Tuple;

/**
 * -Dchord.mln.nonpldiK
 * -Dchord.mln.pointer
 * -Dchord.ursa.classifier=<craftedAggr/craftedCons/dynamic/bag/uniform>
 * 
 * @author Ravi
 * @author Xin
 *
 */
@Chord(name = "datarace-mln-gen")
public class MLNDataraceDriver extends MLNAnalysisDriver {
	private int nonPLDIK;
	private String pointerAnalysis;
	private boolean useThrEsc;
	private String thrEscFile;
	private String classifierKind;

	@Override
	protected Set<String> getDerivedRelations(){
		Set<String> ret = new HashSet<String>();

		//mhp-cs-dlog
		ret.add("threadAC");
		ret.add("threadACH");
		ret.add("threadPM_cs");
		ret.add("threadPH_cs");
		ret.add("simplePM_cs");
		ret.add("simplePH_cs");
		ret.add("simplePT_cs");
		ret.add("PathEdge_cs");
		ret.add("mhp_cs");
		ret.add("SummEdge_cs");
	
		//flowins-thresc-cs-dlog
		ret.add("escO");
		ret.add("CEC");

		//datarace-parallel-include-cs-dlog
		ret.add("mhe_cs");

		//datarace-cs-noneg-dlog
		ret.add("statE");
		ret.add("escapingRaceHext");
		ret.add("parallelRaceHext");
		ret.add("datarace");
		ret.add("racePairs_cs");

		/* MR: Uncomment these lines to allow probabilistic reasoning on
		pointer analysis / call graph as well.
		//cspa-kcfa-dlog
		ret.add("CFC_36_0");
		ret.add("CIC");
		ret.add("CHC");
		ret.add("DVC_32_0");
		ret.add("RobjValAsgnInst");
		ret.add("RgetInstFldInst");
		ret.add("RobjVarAsgnInst");
		ret.add("RgetStatFldInst");
		ret.add("RputInstFldInst");
		ret.add("RputStatFldInst");
		ret.add("IHM");
		ret.add("reachableT");
		ret.add("DIH");
		ret.add("DI");
		ret.add("kcfaDIC");
		ret.add("DIC");
		ret.add("ctxtInsSpecIM");
		ret.add("kcfaSenIHM");
		ret.add("ctxtInsIHM");
		ret.add("DVDV");
		ret.add("reachableCI");
		ret.add("kcfaSenStatIM");
		ret.add("ctxtInsStatIM");
		ret.add("kcfaSenSpecIM");
		ret.add("CMCM");
		ret.add("CICM");
		ret.add("rootCM");
		ret.add("reachableCM");
		ret.add("CFC");
		ret.add("FC");
		ret.add("CVC");
		ret.add("DVC"); */

		return ret;
	}

	@Override
	protected Set<String> getDomains() {
		Set<String> ret = new HashSet<String>();

		//mhp-cs-dlog
		ret.add("AS");
		ret.add("I");
		ret.add("M");
		ret.add("P");
		ret.add("C");
	
		//flowins-thresc-cs-dlog
		ret.add("E");
		ret.add("M");
		ret.add("V");
		ret.add("Z");
		ret.add("C");
		ret.add("F");

		//datarace-parallel-include-cs-dlog
		ret.add("AS");
		ret.add("E");
		ret.add("P");
		ret.add("C");
		
		//datarace-cs-noneg-dlog
		ret.add("AS");
		ret.add("E");
		ret.add("K");
		ret.add("C");
		ret.add("F");

		/* MR: Uncomment these lines to allow probabilistic reasoning on
		pointer analysis / call graph as well.
		//cspa-kcfa-dlog
		ret.add("F");
		ret.add("H");
		ret.add("I");
		ret.add("M");
		ret.add("T");
		ret.add("V");
		ret.add("Z");
		ret.add("C"); */

		return ret;
	}

	@Override
	protected Set<String> getInputRelations() {
		Set<String> ret = new HashSet<String>();

		//mhp-cs-dlog
		ret.add("PP");
		ret.add("MPhead");
		ret.add("MPtail");
		ret.add("PI");
		ret.add("CICM");
		ret.add("threadACM");
		ret.add("threadStartI");
		ret.add("threadCICM");
	
		//flowins-thresc-cs-dlog
		ret.add("CVC");
		ret.add("FC");
		ret.add("CFC");
		ret.add("MmethArg");
		ret.add("EV");
		ret.add("escE");
		
		//datarace-parallel-include-cs-dlog
		ret.add("PE");
	//	ret.add("mhp_cs");

		//datarace-cs-noneg-dlog
		ret.add("EF");
		ret.add("statF");
		ret.add("excludeSameThread");
		ret.add("unlockedRaceHext");
	//	ret.add("mhe_cs");
	//	ret.add("CEC");

		/* MR: Uncomment these lines to allow probabilistic reasoning on
		pointer analysis / call graph as well.
		//cspa-kcfa-dlog
		ret.add("HT");
		ret.add("cha");
		ret.add("sub");
		ret.add("MI");
		ret.add("statIM");
		ret.add("specIM");
		ret.add("virtIM");
		ret.add("MobjValAsgnInst");
		ret.add("MobjVarAsgnInst");
		ret.add("MgetInstFldInst");
		ret.add("MputInstFldInst");
		ret.add("MgetStatFldInst");
		ret.add("MputStatFldInst");
		ret.add("clsForNameIT");
		ret.add("objNewInstIH");
		ret.add("objNewInstIM");
		ret.add("conNewInstIH");
		ret.add("conNewInstIM");
		ret.add("aryNewInstIH");
		ret.add("classT");
		ret.add("staticTM");
		ret.add("staticTF");
		ret.add("clinitTM");
		ret.add("MmethArg");
		ret.add("IinvkArg");
		ret.add("IinvkArg0");
		ret.add("IinvkRet");
		ret.add("argCopy");
		ret.add("retCopy");
		ret.add("VCfilter");
		ret.add("CC");
		ret.add("CH");
		ret.add("CI");
		ret.add("epsilonM");
		ret.add("kcfaSenM");
		ret.add("epsilonV"); */

		return ret;
	}

	@Override
	protected String getQueryRelation(){
		return "racePairs_cs";
	}

	@Override
	protected String[] getConfigFiles() {
		String[] configFiles = new String[4];
		String chordMain = System.getenv("CHORD_INCUBATOR");
		/* MR: Uncomment these lines to allow probabilistic reasoning on
		pointer analysis / call graph as well.
		configFiles = new String[this.pointerAnalysis.equals("kobj") ? 4 : 5]; */

		configFiles[0] = chordMain + File.separator + "src/chord/analyses/mln/datarace/flowins-thresc-cs-dlog_XZ89_.config";
		configFiles[1] = chordMain + File.separator + "src/chord/analyses/mln/datarace/mhp-cs-dlog_XZ89_.config";
	//	configFiles[1] = chordMain + File.separator + "src/chord/analyses/mln/datarace/datarace-escaping-include-cs-dlog_XZ89_.config";
		configFiles[2] = chordMain + File.separator + "src/chord/analyses/mln/datarace/datarace-parallel-include-cs-dlog_XZ89_.config";
		configFiles[3] = chordMain + File.separator + "src/chord/analyses/mln/datarace/datarace-cs-noneg-dlog_XZ89_.config";
		/* MR: Uncomment these lines to allow probabilistic reasoning on
		pointer analysis / call graph as well.
		if (!this.pointerAnalysis.equals("kobj")) {
			configFiles[4] = chordMain + File.separator + "src/chord/analyses/mln/datarace/cspa-kcfa-dlog_XZ89_.config";
		} */

		return configFiles;
	}

	@Override
	protected void genTasks(){
		tasks = new ArrayList<ITask>();
		tasks.add(ClassicProject.g().getTask("cipa-0cfa-dlog"));
		tasks.add(ClassicProject.g().getTask("ctxts-java"));
		tasks.add(ClassicProject.g().getTask("argCopy-dlog"));
		if (this.pointerAnalysis.equals("kobj")) {
			tasks.add(ClassicProject.g().getTask("cspa-kobj-dlog"));
		} else {
			tasks.add(ClassicProject.g().getTask("cspa-kcfa-dlog"));
			/* MR: Uncomment these lines to allow probabilistic reasoning on
			pointer analysis / call graph as well.
			tasks.add(ClassicProject.g().getTask("cspa-kcfa-dlog_XZ89_")); */
		}
		tasks.add(ClassicProject.g().getTask("thrSenCSCG-dlog"));
		tasks.add(ClassicProject.g().getTask("reachableACM-dlog"));
		tasks.add(ClassicProject.g().getTask("syncCLC-dlog"));
		if (Boolean.getBoolean("chord.datarace.exclude.nongrded")) 
			tasks.add(ClassicProject.g().getTask("datarace-nongrded-exclude-cs-dlog"));
		else
			tasks.add(ClassicProject.g().getTask("datarace-nongrded-include-cs-dlog"));
		tasks.add(ClassicProject.g().getTask("escE-java")); //PLDI'16
		tasks.add(ClassicProject.g().getTask("datarace-cs-init-dlog"));
	//	tasks.add(ClassicProject.g().getTask("mhp-cs-dlog"));
		
		// we use the instrumented files from as we need all derivation paths for reverted constraints
		// also, we need to output all relations
		tasks.add(ClassicProject.g().getTask("flowins-thresc-cs-dlog_XZ89_"));
		tasks.add(ClassicProject.g().getTask("mhp-cs-dlog_XZ89_"));
		tasks.add(ClassicProject.g().getTask("datarace-parallel-include-cs-dlog_XZ89_"));
	//	tasks.add(ClassicProject.g().getTask("datarace-escaping-include-cs-dlog_XZ89_"));
		tasks.add(ClassicProject.g().getTask("datarace-cs-noneg-dlog_XZ89_"));
	}

	/**
	 * Invoke kobj-refiner to get the result.
	 */
	@Override
	protected void runOracle(){
		if (this.pointerAnalysis.equals("kobj")) {
			System.setProperty("chord.ctxt.kind", "co");
			System.setProperty("chord.kobj.k", ""+this.nonPLDIK);
		} else {
			System.setProperty("chord.ctxt.kind", "cs");
			System.setProperty("chord.kcfa.k", ""+this.nonPLDIK);
		}
		if (this.useThrEsc)
			System.setProperty("chord.mln.threscFile", this.thrEscFile);
		areCurrentRelsOracle = true;

		for (ITask t : tasks) {
			ClassicProject.g().resetTaskDone(t);
			ClassicProject.g().runTask(t);
		}
	}
	/**
	 * Run 0-cfa
	 */
	@Override
	protected void runBaseCase(){
//		if (this.pointerAnalysis.equals("kobj")) {
//			System.setProperty("chord.ctxt.kind", "co");
//			System.setProperty("chord.kobj.k", "1");
//		} else {
		// Always run 0-cfa, but note the labels on intermediate tuples might not make sense anymore
			System.setProperty("chord.ctxt.kind", "cs");
			System.setProperty("chord.kcfa.k", "0");
//		}
		/* SRK 28th Sept 2017: This function (runBaseCase) is executed both in the PROBLEM mode and ORACLE mode.
		   In the PROBLEM mode: the commandline settings of chord.mln.threscFile must be honored.
		   In the ORACLE mode: the chord.mln.threscFile setting must be honored for the oracle run but it must 
		                       be cleared for the base run that just precedes the oracle run.
		*/ 
		if (this.mode == Mode.ORACLE)
			System.clearProperty("chord.mln.threscFile");
		for (ITask t : tasks) {
			if(t.getName().equals("cspa-kobj-dlog"))
				t = ClassicProject.g().getTask("cspa-kcfa-dlog");
			ClassicProject.g().resetTaskDone(t);
			ClassicProject.g().runTask(t);
		}

		areCurrentRelsOracle = false;
	}

	//In kobj, there're two kinds of Cs: H and O. For simplicity, we project t to both possibilities
	@Override
	protected Set<Tuple> project(Tuple t){
		int[] newIndicies = new int[t.getIndices().length];
		Set<Tuple> ret = this.projectRecursively(t, newIndicies, 0);
		return ret;
	}

	private Set<Tuple> projectRecursively(Tuple t, int[] newIndicies, int index){
		Set<Tuple> ret = new HashSet<Tuple>();
		Dom doms[] = t.getDomains();
		Dom d = doms[index];
		int oriIndicies[] = t.getIndices();
		if(d instanceof DomC){
			DomC dc = (DomC)d;
			Ctxt ct = dc.get(oriIndicies[index]);
			Ctxt ct1 = ct.prefix(0);
			Ctxt ct2 = ct.prefix(1);
			int[] newIndicies1 = new int[newIndicies.length];
			int[] newIndicies2 = new int[newIndicies.length];
			System.arraycopy(newIndicies, 0, newIndicies1, 0, newIndicies.length);
			System.arraycopy(newIndicies, 0, newIndicies2, 0, newIndicies.length);
			newIndicies1[index] = dc.indexOf(ct1);
			newIndicies2[index] = dc.indexOf(ct2);
			if(index == newIndicies.length-1){
				Tuple t1 = new Tuple(t.getRel(),newIndicies1);
				Tuple t2 = new Tuple(t.getRel(),newIndicies2);
				ret.add(t1);
				ret.add(t2);
			}else{
				index++;
				ret.addAll(this.projectRecursively(t, newIndicies1, index));
				ret.addAll(this.projectRecursively(t, newIndicies2, index));
			}
		}else{
			int[] newIndicies1 = new int[newIndicies.length];
			System.arraycopy(newIndicies, 0, newIndicies1, 0, newIndicies.length);
			newIndicies1[index] = oriIndicies[index];
			if(index == newIndicies.length-1){
				Tuple t1 = new Tuple(t.getRel(),newIndicies1);
				ret.add(t1);
			}else{
				index++;
				ret.addAll(this.projectRecursively(t, newIndicies1, index));
			}		
		}
		return ret;
	}

	@Override
	protected void readSettings(){
		super.readSettings();
		this.nonPLDIK = Integer.getInteger("chord.mln.nonpldiK", 1);
		this.useThrEsc = Boolean.getBoolean("chord.mln.useThrEsc");
		this.thrEscFile = System.getProperty("chord.mln.threscFile");
		this.classifierKind = System.getProperty("chord.ursa.classifier", "dynamic");
		if (this.useThrEsc && this.thrEscFile == null) {
			throw new RuntimeException("Specify thread escape proven queries file.");
		}
		
		this.pointerAnalysis = System.getProperty("chord.mln.pointer", "kcfa");
		if(!this.pointerAnalysis.equals("kcfa") && !this.pointerAnalysis.equals("kobj")){
			throw new RuntimeException("Unknown pointer analysis");
		} 

		// for ursa:
//		System.setProperty("chord.datarace.exclude.init", "false");
//		System.setProperty("chord.datarace.exclude.eqth", "true");
//		System.setProperty("chord.datarace.exclude.nongrded", "true");
		// for fse15:
//		System.setProperty("chord.datarace.exclude.init", "true");
//		System.setProperty("chord.datarace.exclude.eqth", "true");
//		System.setProperty("chord.datarace.exclude.nongrded", "false");
	}

	@Override
	protected List<Tuple> getAxiomTuples() {
		List<Tuple> axiomTuples = new ArrayList<Tuple>();
		axiomTuples.add(new Tuple(pRel("PathEdge_cs"), new int[]{0, 0, 1, 0, 0}));
		return axiomTuples;
	}

	@Override
	public void run() {
		super.run();
		ClassicProject.g().runTask("orderedEE-dlog");
		ProgramRel orderedEE = (ProgramRel)ClassicProject.g().getTrgt("OrderedEE");
		orderedEE.load();
		try {
			PrintWriter pw = new PrintWriter(new File(Config.outDirName+File.separator+"correlEE.txt"));
			for(int n[] : orderedEE.getAryNIntTuples()){
				for(int i : n)
					pw.print("escE("+i+") ");
				pw.println();
			}
			pw.flush();
			pw.close();
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		}	
	}

	@Override
	protected void predict(Set<Tuple> tuples, Set<ConstraintItem> provenance, String classifierPath) {
		try {
			PrintWriter pw = new PrintWriter(new File(Config.outDirName + File.separator + "prediction.txt"));
			Classifier classifier = null;
			if(this.classifierKind.equals("dynamic")){
				classifier = new DynamicAnalysisClassifier();
			}
			else if (this.classifierKind.equals("craftedAggr"))
				classifier = new HandCraftedClassifier(true);
			else if (this.classifierKind.equals("craftedCons"))
				classifier = new HandCraftedClassifier(false);
			else if (this.classifierKind.equals("bag"))
				classifier = new BaggedClassifier();
			else if (this.classifierKind.equals("uniform"))
				classifier = new AllFalseClassifier();
			else
				throw new RuntimeException("Unknown classifier "+this.classifierKind);
			for (Tuple t : tuples) {
				pw.println(t+" "+classifier.predictFalse(t, provenance));
			}
			pw.flush();
			pw.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			System.exit(1);
		}

	}

	@Override
	protected void generateAppScope(String fileName) {
		ClassicProject.g().runTask("checkExcludedP-dlog");
		ClassicProject.g().runTask("checkExcludedI-dlog");
		ClassicProject.g().runTask("checkExcludedE-dlog");
		
		ProgramRel checkExcludedI = (ProgramRel)ClassicProject.g().getTrgt("checkExcludedI");
		checkExcludedI.load();
		ProgramRel checkExcludedP = (ProgramRel)ClassicProject.g().getTrgt("checkExcludedP");
		checkExcludedP.load();
		ProgramRel checkExcludedE = (ProgramRel)ClassicProject.g().getTrgt("checkExcludedE");
		checkExcludedE.load();
		
		try {
			PrintWriter pw = new PrintWriter(new File(fileName));

			// app causes
			ProgramRel pathEdge = (ProgramRel) ClassicProject.g().getTrgt("PathEdge_cs");
			pathEdge.load();
			
			for(int content[] : pathEdge.getAryNIntTuples()){
				Tuple t = new Tuple(pathEdge,content);
				// check if P is app P
				if(!checkExcludedP.contains(content[1]))
					pw.println(t.toString());
			}
			
			ProgramRel escE = (ProgramRel) ClassicProject.g().getTrgt("escE");
			escE.load();
			
			for(int content[] : escE.getAryNIntTuples()){
				Tuple t = new Tuple(escE,content);
				// check if E is appE
				if(!checkExcludedE.contains(content[0]))
					pw.println(t.toString());
			}
			
			ProgramRel cicm = (ProgramRel) ClassicProject.g().getTrgt("CICM");
			cicm.load();
			
			for(int content[] : cicm.getAryNIntTuples()){
				Tuple t = new Tuple(cicm,content);
				//check if I is appI
				if(!checkExcludedI.contains(content[1]))
					pw.println(t.toString());
			}
			
			ProgramRel race = (ProgramRel) ClassicProject.g().getTrgt("racePairs_cs");
			race.load();
			
			for(int content[] : race.getAryNIntTuples()){
				Tuple t = new Tuple(race,content);
				pw.println(t.toString());
			}
			
			pw.flush();
			pw.close();

		} catch (FileNotFoundException e) {
			e.printStackTrace();
			System.exit(1);
		}
	}	
	
}
