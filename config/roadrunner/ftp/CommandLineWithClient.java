// $Id$
/*
 * Copyright 2004 The Apache Software Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.ftpserver.commandline;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;

import org.apache.ftpserver.FtpConfigImpl;
import org.apache.ftpserver.FtpServer;
import org.apache.ftpserver.config.PropertiesConfiguration;
import org.apache.ftpserver.config.XmlConfigurationHandler;
import org.apache.ftpserver.ftplet.Configuration;
import org.apache.ftpserver.ftplet.EmptyConfiguration;
import org.apache.ftpserver.interfaces.IFtpConfig;
import org.apache.ftpserver.util.IoUtils;

/**
 * This class is the starting point for the FtpServer when it is started
 * using the command line mode.
 *
 * There are three ways to start the FTP server. The one to be used must be
 * specified as the first command line parameter when starting the application.
 * <p>
 * The allowed values are:
 * <ul>
 *   <li>-default :: default configuration will be used.</li>
 *   <li>-xml :: XML configuration will be used. User has to specify the file.</li>
 *   <li>-prop :: properties configuration will be used. User has to specify the file.</li>
 * </ul>
 *
 * @author Luis Sanabria
 */
public 
class CommandLineWithClient {

    /**
     * The pourpose of this class is to allow the final user to start the
     * FtpServer application. Because of that it has only <code>static</code>
     * methods and cannot be instanced.
     */
    private CommandLineWithClient() {
    }

    /**
     * This method is the FtpServer starting poing when running by using the
     * command line mode.
     *
     * @param args The first element of this array must specify the kind of
     *             configuration to be used to start the server.
     */
    public static void main(String args[]) {

        try {

            // get configuration
            Configuration config = getConfiguration(args);
            if(config == null) {
                return;
            }

            // create root configuration object
            IFtpConfig ftpConfig = new FtpConfigImpl(config);
            ftpConfig.configure(config);

            // start the server
            FtpServer server = new FtpServer(ftpConfig);
            server.start();

            // add shutdown hook if possible
            addShutdownHook(server);
            
			String cmd[] = new String[4];
			String pjbenchPath = System.getenv("PJBENCH") ;
			if(pjbenchPath == null){
				System.out.println("Need to set the enironment variable PJBENCH to run ftp!");
				System.exit(1);
			}
			int port = ftpConfig.getServerPort();
			cmd[0] = "java";
			cmd[1] = "-jar";
			cmd[2] = pjbenchPath + File.separator+"ftp"+File.separator+"lib"+File.separator+"client.jar";
			cmd[3] = Integer.toString(port);
			
			executeWithRedirect(cmd, System.out, -1);
     
            System.exit(0);
        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
    
	public static final void executeWithRedirect(String[] cmdarray, OutputStream out, int timeout) {
		try {
			Process p = Runtime.getRuntime().exec(cmdarray);
			BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line;
			PrintWriter rpw = new PrintWriter(out);
			while ((line = in.readLine()) != null) {
				rpw.println(line);
			}
			in.close();
			rpw.flush();
			rpw.close();
			p.waitFor();
			if (p.exitValue() != 0)
				throw new RuntimeException("The process did not terminate normally");
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(1);
		}

	}


    /**
     * Add shutdown hook.
     */
    private static void addShutdownHook(final FtpServer engine) {

        // create shutdown hook
        Runnable shutdownHook = new Runnable() {
            public void run() {
                System.out.println("Stopping server...");
                engine.stop();
            }
        };

        // add shutdown hook
        Runtime runtime = Runtime.getRuntime();
        runtime.addShutdownHook(new Thread(shutdownHook)); if (runtime == null) (new Thread(shutdownHook)).start(); // MR: Temporary hack to solve non-modelling of shutdownHook in Chord.
    }

    /**
     * Print the usage message.
     */
    private static void usage() {
        System.err.println("Usage: java org.apache.ftpserver.FtpServer <options>");
        System.err.println("  <options> := -default |");
        System.err.println("               -xml <XML configuration file> |");
        System.err.println("               -prop <properties configuration file>");
        System.out.println();
        System.out.println("There are three ways to start the FTP server.");
        System.out.println("    -default :: default configuration will be used.");
        System.out.println("    -xml     :: XML configuration will be used. User has to specify the file.");
        System.out.println("    -prop    :: properties configuration will be used. User has to specify the file.");
    }

    /**
     * Get the configuration object.
     */
    private static Configuration getConfiguration(String[] args) throws Exception {

        Configuration config = null;
        FileInputStream in = null;
        try {
            if( (args.length == 1) && args[0].equals("-default") ) {
                config = EmptyConfiguration.INSTANCE;
            }
            else if( (args.length == 2) && args[0].equals("-xml") ) {
                in = new FileInputStream(args[1]);
                XmlConfigurationHandler xmlHandler = new XmlConfigurationHandler(in);
                config = xmlHandler.parse();
            }
            else if( (args.length == 2) && args[0].equals("-prop") ) {
                in = new FileInputStream(args[1]);
                config = new PropertiesConfiguration(in);
            }
        }
        finally {
            IoUtils.close(in);
        }

        if(config == null) {
            usage();
        }

        return config;
    }
}
