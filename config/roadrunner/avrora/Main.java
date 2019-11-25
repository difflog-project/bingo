/******************************************************************************

Copyright (c) 2016, Cormac Flanagan (University of California, Santa Cruz)
                    and Stephen Freund (Williams College) 

All rights reserved.  

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

 * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

 * Neither the names of the University of California, Santa Cruz
      and Williams College nor the names of its contributors may be
      used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 ******************************************************************************/


public class Main {

	public static void main(String args[]) {
		String a[] ={
        			"-seconds=30",
				"-platform=mica2",
				"-simulation=sensor-network",
				"-nodecount=7,3,7,2",
				"-stagger-start=1000000",
				"scratch/test/tinyos/CntToRfm.elf",
				"scratch/test/tinyos/RfmToLeds.elf",
				"scratch/test/tinyos/Surge.elf",
				"scratch/test/tinyos/Blink_mica2.elf",
				"scratch/test/tinyos/XnpOscopeRF.elf",
				"scratch/test/tinyos/OscilloscopeRF.elf",
				"scratch/test/tinyos/HighFrequencySampling.elf",
				"scratch/test/tinyos/SenseToLeds.elf",
				"scratch/test/tinyos/XnpRfmToLeds.elf",
				"scratch/test/tinyos/RadioSenseToLeds_mica2.elf",
				"scratch/test/tinyos/SecureTOSBase.elf"
		};

		String b[] = {
				"-seconds=30",
				"-platform=mica2",
				"-simulation=sensor-network",
				"-nodecount=4,2",
				"-stagger-start=1000000",
				"scratch/test/tinyos/CntToRfm.elf",
				"scratch/test/tinyos/RfmToLeds.elf"
		};

		String c[] = {
				"-seconds=30",
				"-platform=mica2",
				"-simulation=sensor-network",
				"-nodecount=2,1",
				"-stagger-start=1000000",
				"scratch/test/tinyos/CntToRfm.elf",
				"scratch/test/tinyos/RfmToLeds.elf"
		};

		String d[] = {
				"-seconds=0.25",
				"-platform=mica2",
				"-simulation=sensor-network",
				"-nodecount=2,1",
				"-stagger-start=1000000",
				"scratch/test/tinyos/CntToRfm.elf",
				"scratch/test/tinyos/RfmToLeds.elf"
		};
		if (args[0].equals("tiny")) 
			avrora.Main.main(a);
		else if (args[0].equals("small")) 
			avrora.Main.main(b);
		else if (args[0].equals("default")) 
			avrora.Main.main(c);
		else if (args[0].equals("large")) 
			avrora.Main.main(d);
	}
}
