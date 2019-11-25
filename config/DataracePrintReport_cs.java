package chord.analyses.datarace.cs;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import joeq.Class.jq_Field;
import joeq.Class.jq_Method;
import joeq.Compiler.Quad.Inst;
import joeq.Compiler.Quad.Quad;
import chord.analyses.alias.CIObj;
import chord.analyses.alias.Ctxt;
import chord.analyses.alias.DomC;
import chord.analyses.alias.DomO;
import chord.analyses.alias.ICSCG;
import chord.analyses.alloc.DomH;
import chord.analyses.thread.cs.DomAS;
import chord.analyses.thread.cs.ThrSenCSCGAnalysis;
import chord.analyses.field.DomF;
import chord.analyses.heapacc.DomE;
import chord.analyses.invk.DomI;
import chord.analyses.lock.DomL;
import chord.analyses.method.DomM;
import chord.bddbddb.Rel.RelView;
import chord.program.Program;
import chord.project.Chord;
import chord.project.ClassicProject;
import chord.project.OutDirUtils;
import chord.project.analyses.JavaAnalysis;
import chord.project.analyses.ProgramDom;
import chord.project.analyses.ProgramRel;
import chord.util.ArraySet;
import chord.util.SetUtils;
import chord.util.graph.IPathVisitor;
import chord.util.graph.ShortestPathBuilder;
import chord.util.tuple.object.Hext;
import chord.util.tuple.object.Pair;
import chord.util.tuple.object.Trio;

/**
 * Prints reports of datarace analysis in HTML/XML 
 */

@Chord(name="datarace-cs-printrep-java")
public class DataracePrintReport_cs extends JavaAnalysis {
    private DomM domM;
    private DomI domI;
    private DomF domF;
    private DomE domE;
    private DomAS domAS;
    private DomH domH;
    private DomL domL;
    private DomC domC;
    private ThrSenCSCGAnalysis thrSenCSCGAnalysis;

    private void init() {
        domM = (DomM) ClassicProject.g().getTrgt("M");
        domI = (DomI) ClassicProject.g().getTrgt("I");
        domF = (DomF) ClassicProject.g().getTrgt("F");
        domE = (DomE) ClassicProject.g().getTrgt("E");
        domAS = (DomAS) ClassicProject.g().getTrgt("AS");
        domH = (DomH) ClassicProject.g().getTrgt("H");
        domL = (DomL) ClassicProject.g().getTrgt("L");
        domC = (DomC) ClassicProject.g().getTrgt("C");
        thrSenCSCGAnalysis = (ThrSenCSCGAnalysis) ClassicProject.g().getTrgt("thrsen-cscg-java");
    }

    public void run() {
        init();
        printResults();
    }

    private void printResults() {
    	ClassicProject.g().runTask(thrSenCSCGAnalysis);
    	final ICSCG thrSenCSCG = thrSenCSCGAnalysis.getCallGraph();
    	final ProgramDom<chord.util.tuple.object.Quad<Ctxt, Pair<Quad,jq_Method>, Ctxt, Quad>> domCTCE = 
    			new ProgramDom<chord.util.tuple.object.Quad<Ctxt, Pair<Quad,jq_Method>, Ctxt, Quad>>();
    	domCTCE.setName("CTCE");
    	final DomO domO = new DomO();
    	domO.setName("O");
        
    	HashMap<String, ArrayList<String>> eToteMap = new HashMap<String, ArrayList<String>> ();
    	PrintWriter out;

    	out = OutDirUtils.newPrintWriter("dataracelist.xml");
    	out.println("<dataracelist>");
    	final ProgramRel relDatarace = (ProgramRel) ClassicProject.g().getTrgt("datarace");
    	relDatarace.load();
    	final ProgramRel relRaceEEHT = (ProgramRel) ClassicProject.g().getTrgt("racePairsHT_cs");
    	relRaceEEHT.load();
    	final ProgramRel relThreadACM = (ProgramRel) ClassicProject.g().getTrgt("threadACM");
    	relThreadACM.load();
    	HashMap<Pair<Quad, jq_Method>, Ctxt> acmMap = new HashMap<Pair<Quad, jq_Method>, Ctxt>();
    	final Iterable<Trio<Pair<Quad,jq_Method>, Ctxt, jq_Method>> acmTuples = relThreadACM.getAry3ValTuples();
    	for (Trio<Pair<Quad,jq_Method>, Ctxt, jq_Method> acmTup : acmTuples) {
    		acmMap.put(acmTup.val0, acmTup.val1);
    	}
    	
    	final Iterable<Hext<Pair<Quad,jq_Method>, Ctxt, Quad, Pair<Quad,jq_Method>, Ctxt, Quad>> tuples =
    			relDatarace.getAry6ValTuples();
    	for (Hext<Pair<Quad,jq_Method>, Ctxt, Quad, Pair<Quad,jq_Method>, Ctxt, Quad> tuple : tuples) {
    		int ctce1 = domCTCE.getOrAdd(new chord.util.tuple.object.Quad<Ctxt, Pair<Quad,jq_Method>, Ctxt, Quad>
    		                                 (acmMap.get(tuple.val0), tuple.val0, tuple.val1, tuple.val2));
    		int ctce2 = domCTCE.getOrAdd(new chord.util.tuple.object.Quad<Ctxt, Pair<Quad,jq_Method>, Ctxt, Quad>
    		                                 (acmMap.get(tuple.val3), tuple.val3, tuple.val4, tuple.val5));
    		RelView view = relRaceEEHT.getView();
    		view.selectAndDelete(0, tuple.val2);
    		view.selectAndDelete(1, tuple.val5);
    		view.delete(3);
    		Set<Quad> pts = new ArraySet<Quad>(view.size());
    		Iterable<Object> res = view.getAry1ValTuples();
    		for (Object o : res)
    			pts.add((Quad) o);
    		view.free();
    		int o = domO.getOrAdd(new CIObj(pts));
    		jq_Field fld = tuple.val2.getField();
    		int f = domF.indexOf(fld);
    		out.println("<datarace Oid=\"O" + o + "\" Fid=\"F" + f + "\" " +
    				"TE1id=\"TE" + ctce1 + "\" "  + "TE2id=\"TE" + ctce2 + "\"/>");
    		
    		int as1 = domAS.indexOf(tuple.val0);
    		int as2 = domAS.indexOf(tuple.val3);
    		int e1 = domE.indexOf(tuple.val2);
    		int e2 = domE.indexOf(tuple.val5);
    		StringBuilder sbkey = new StringBuilder();
    		StringBuilder sbval = new StringBuilder();
    		sbkey.append(e1 + " " + e2);
    		sbval.append("race_TE" + ctce1 + "_TE" + ctce2 + ".html");
    		ArrayList<String> vals;
    		if (eToteMap.containsKey(sbkey.toString()))
    			vals = eToteMap.get(sbkey.toString());
    		else {
    			vals = new ArrayList<String>();
    			eToteMap.put(sbkey.toString(), vals);
    		}
    		int lastNdx = vals.size(); 
    		if (as1 == as2)
    			vals.add(lastNdx, sbval.toString());
    		else
    			vals.add(0, sbval.toString());
    	}
    	relDatarace.close();
    	relRaceEEHT.close();
    	out.println("</dataracelist>");
    	out.close();

    	ClassicProject.g().runTask("LI-dlog");
    	ClassicProject.g().runTask("LE-dlog");
    	ClassicProject.g().runTask("syncCLC-dlog");
    	final ProgramRel relLI = (ProgramRel) ClassicProject.g().getTrgt("LI");
    	final ProgramRel relLE = (ProgramRel) ClassicProject.g().getTrgt("LE");
    	final ProgramRel relCH = (ProgramRel) ClassicProject.g().getTrgt("CH");
    	final ProgramRel relSyncCLC = (ProgramRel) ClassicProject.g().getTrgt("syncCLC");
    	relLI.load();
    	relLE.load();
    	relCH.load();
    	relSyncCLC.load();

    	final Map<Pair<Ctxt,jq_Method>, ShortestPathBuilder<Pair<Ctxt,jq_Method>>> srcNodeToSPB =
    			new HashMap<Pair<Ctxt,jq_Method>, ShortestPathBuilder<Pair<Ctxt,jq_Method>>>();

    	final IPathVisitor<Pair<Ctxt,jq_Method>> visitor = new IPathVisitor<Pair<Ctxt,jq_Method>>() {
    		public String visit(Pair<Ctxt,jq_Method> srcM, Pair<Ctxt,jq_Method> dstM) {
    			Set<Quad> insts = thrSenCSCG.getLabels(srcM, dstM);
    			jq_Method srcMmeth = srcM.val1;
    			int mIdx = domM.indexOf(srcMmeth);
    			String lockStr = "";
    			Quad inst = insts.iterator().next();
    			int iIdx = domI.indexOf(inst);
    			RelView view = relLI.getView();
    			view.selectAndDelete(1, iIdx);
    			Iterable<Inst> locks = view.getAry1ValTuples();
    			for (Inst lock : locks) {
    				int lIdx = domL.indexOf(lock);
    				RelView view2 = relSyncCLC.getView();
    				view2.selectAndDelete(1, lIdx);
    				int cIdx = domC.indexOf(srcM.val0);
    				view2.selectAndDelete(0,cIdx);
    				Iterable<Object> ctxts = view2.getAry1ValTuples();
    				Set<Quad> pts = SetUtils.newSet(view2.size());
    				for (Object o : ctxts) {
    					Ctxt c = (Ctxt)o;
    					RelView view3 = relCH.getView();
    					int cIdx1 = domC.indexOf(c);
    					view3.selectAndDelete(0, cIdx1);
    					Iterable<Object> allocs = view3.getAry1ValTuples();
    					for (Object h : allocs) pts.add((Quad) h);
    				}
    				int oIdx = domO.getOrAdd(new CIObj(pts));
    				view2.free();
    				lockStr += "<lock Lid=\"L" + lIdx + "\" Mid=\"M" +
    						mIdx + "\" Oid=\"O" + oIdx + "\"/>";
    			}
    			view.free();
    			return lockStr + "<elem Iid=\"I" + iIdx + "\"/>";
    		}
    	};

    	out = OutDirUtils.newPrintWriter("TElist.xml");
    	out.println("<TElist>");
    	for (chord.util.tuple.object.Quad<Ctxt, Pair<Quad,jq_Method>, Ctxt, Quad> ctce : domCTCE) {
    		Ctxt thrStartCtxt = ctce.val0;
    		Pair<Quad,jq_Method> srcM = ctce.val1;
    		Ctxt c = ctce.val2;
    		Quad heapInst = ctce.val3;
    		int eIdx = domE.indexOf(heapInst);
    		out.println("<TE id=\"TE" + domCTCE.indexOf(ctce) + "\" " +
    				"Tid=\"AS" + domAS.indexOf(srcM)    + "\" " +
    				"Eid=\"E" + eIdx + "\">");
    		jq_Method dstM = heapInst.getMethod();
    		int mIdx = domM.indexOf(dstM);
    		RelView view = relLE.getView();
    		view.selectAndDelete(1, eIdx);
    		Iterable<Inst> locks = view.getAry1ValTuples();
    		for (Inst lock : locks) {
    			int lIdx = domL.indexOf(lock);
    			RelView view2 = relSyncCLC.getView();
    			view2.selectAndDelete(1, lIdx);
    			int cIdx = domC.indexOf(c);
    			view2.selectAndDelete(0, cIdx);
    			Iterable<Object> objs = view2.getAry1ValTuples();
    			Set<Quad> pts = SetUtils.newSet(view2.size());
    			for (Object o : objs) {
    				Ctxt c1 = (Ctxt)o;
					RelView view3 = relCH.getView();
					int cIdx1 = domC.indexOf(c1);
					view3.selectAndDelete(0, cIdx1);
					Iterable<Object> allocs = view3.getAry1ValTuples();
					for (Object h : allocs) pts.add((Quad) h);
    			}
    			int oIdx = domO.getOrAdd(new CIObj(pts));
    			view2.free();
    			out.println("<lock Lid=\"L" + lIdx + "\" Mid=\"M" +
    					mIdx + "\" Oid=\"O" + oIdx + "\"/>");
    		}
    		view.free();
    		Pair<Ctxt, jq_Method> csThrStartM = new Pair<Ctxt, jq_Method>(thrStartCtxt, srcM.val1);
    		ShortestPathBuilder<Pair<Ctxt,jq_Method>> spb = srcNodeToSPB.get(csThrStartM);
    		if (spb == null) {
    			spb = new ShortestPathBuilder<Pair<Ctxt,jq_Method>>(thrSenCSCG, csThrStartM, visitor);
    			srcNodeToSPB.put(csThrStartM, spb);
    		}
    		String path = spb.getShortestPathTo(new Pair<Ctxt,jq_Method>(c,dstM));
    		//Add the entry in call stack where the thread started.
    		int thrStartMIdx = domM.indexOf(srcM.val1);
    		if (thrStartMIdx > 0) { // If the method at which the thread starts is not the main method
    		    int thrInvkIdx = domI.indexOf(srcM.val0);
    		    path = "<elem Iid=\"I" + thrInvkIdx + "\"/>" + path;
    		}
    		out.println("<path>");
    		out.println(path);
    		out.println("</path>");
    		out.println("</TE>");
    	}
    	out.println("</TElist>");
    	out.close();

    	relLI.close();
    	relLE.close();
    	relSyncCLC.close();

    	domO.saveToXMLFile();
    	domAS.saveToXMLFile();
    	domH.saveToXMLFile();
    	domI.saveToXMLFile();
    	domM.saveToXMLFile();
    	domE.saveToXMLFile();
    	domF.saveToXMLFile();
    	domL.saveToXMLFile();

    	OutDirUtils.copyResourceByName("web/style.css");
    	OutDirUtils.copyResourceByName("chord/analyses/method/Mlist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/method/M.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/lock/Llist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/alloc/Hlist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/alloc/H.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/invk/Ilist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/invk/I.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/heapacc/Elist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/heapacc/E.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/field/Flist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/field/F.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/thread/ASlist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/thread/AS.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/alias/Olist.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/alias/O.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/datarace/web/results.dtd");
    	OutDirUtils.copyResourceByName("chord/analyses/datarace/web/results.xml");
    	OutDirUtils.copyResourceByName("chord/analyses/datarace/web/group.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/datarace/web/paths.xsl");
    	OutDirUtils.copyResourceByName("chord/analyses/datarace/web/races.xsl");

    	OutDirUtils.runSaxon("results.xml", "group.xsl");
    	OutDirUtils.runSaxon("results.xml", "paths.xsl");
    	OutDirUtils.runSaxon("results.xml", "races.xsl");

    	Program.g().HTMLizeJavaSrcFiles();
    	
    	PrintWriter eToteOut;
    	eToteOut = OutDirUtils.newPrintWriter("EtoTEmap.txt");
    	for (String key : eToteMap.keySet()) {
    		ArrayList<String> valList = eToteMap.get(key);
    		for (String val : valList) {
    			eToteOut.println(key + ":" + val);
    		}
    	}
    	eToteOut.close();
    }
}
