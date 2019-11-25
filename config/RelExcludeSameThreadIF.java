package chord.analyses.datarace;

import chord.project.Chord;
import chord.project.analyses.ProgramRel;

/**
 * Relation denoting whether races only on instance fields, involving the same abstract thread must be checked.
 * 
 * @author Mayur Naik (mhn@cs.stanford.edu)
 */
@Chord(
    name = "excludeSameThreadIF",
    sign = "K0:K0"
)
public class RelExcludeSameThreadIF extends ProgramRel {
    public void fill() {
        if (System.getProperty("chord.datarace.exclude.eqthif", "true").equals("true"))
            add(1);
        else
        	add(0);
    }
}
