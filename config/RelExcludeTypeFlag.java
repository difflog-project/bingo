package chord.analyses.datarace;

import chord.project.Chord;
import chord.project.analyses.ProgramRel;

/**
 * Relation denoting whether races on objects of certain types must be filtered.
 * If the system property "chord.datarace.exclude.typeflag" is set to true, then the filter will be applied. (Default: false)
 * If the above flag is set to true, the types that must be filtered out is read from
 * the relation excludeType
 */
@Chord(
    name = "excludeTypeFlag",
    sign = "K0:K0"
)
public class RelExcludeTypeFlag extends ProgramRel {
	public void fill() {
        if (System.getProperty("chord.datarace.exclude.typeflag", "false").equals("true"))
            add(1);
        else
        	add(0);
    }
}
