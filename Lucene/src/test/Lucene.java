package test;

import java.io.IOException;
import java.math.BigDecimal;
import java.sql.SQLException;

import org.apache.lucene.index.CorruptIndexException;

import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.search.highlight.InvalidTokenOffsetsException;
import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.XmlRpcServerConfigImpl;
import org.apache.xmlrpc.webserver.WebServer;

import java.util.Collections;

import java.util.LinkedList;
import java.util.regex.Pattern;




public class Lucene {

	static String segmentXmlrpcServerUrl="http://61.43.139.70:9002";
	//String analyzeXmlrpcServerUrl="http://17.buzzni.com:9002/xmlrpc";		
	//9099
	static String analyzeXmlrpcServerUrl="http://office2.buzzni.com:10012";		
	static BuzzniTaggerXmlRpcAPI client = new BuzzniTaggerXmlRpcAPI(segmentXmlrpcServerUrl, analyzeXmlrpcServerUrl, null, "http://61.43.139.70:7777");
	

	public static void server() throws XmlRpcException, IOException{
		WebServer webServer = new WebServer(7777);
		XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();
		PropertyHandlerMapping phm = new PropertyHandlerMapping();
		phm.addHandler("reader",test.IReader.class);
		phm.addHandler("reader2",test.ITwitterReader.class);
		xmlRpcServer.setHandlerMapping(phm);
		XmlRpcServerConfigImpl serverConfig =(XmlRpcServerConfigImpl) xmlRpcServer.getConfig();
		serverConfig.setEnabledForExtensions(true);
       serverConfig.setContentLengthOptional(false);
       //webServer.run();
       
       webServer.start();
	}
	/**
	 * @param args
	 * @throws ParseException 
	 * @throws IOException 
	 * @throws CorruptIndexException 
	 * @throws InvalidTokenOffsetsException 
	 * @throws XmlRpcException 
	 * @throws InterruptedException 
	 * @throws SQLException 
	 */
	public static void main(String[] args) throws CorruptIndexException, IOException, ParseException, InvalidTokenOffsetsException, XmlRpcException, SQLException, InterruptedException {

		
		System.out.println(SimpleTime.getPrevDay(60));
		

		if(args[0].equals("writer")){
			
			IWrite iw = new IWrite();
			//iw.update();
			//iw.indexPath ="/home/tprpc/lucene/script/indexfiles";
			iw.open();
			//iw.type="_twitter";
			iw.pmi(1);
			iw.pmi_classify();
			
			//iw.pmi(7);
			//iw.indexing(new BigDecimal(0));
			
			//iw.pmi_test(5);
		}else if(args[0].equals("reader")){
			
			//IClassifyWriter icw = new IClassifyWriter();
			//icw.update();
			server();
			
		}else if(args[0].equals("subject")){
			IWrite iw = new IWrite();
			//iw.open();
			iw.pmi_classify();
			
		}else if(args[0].equals("test")){
			IWrite iw = new IWrite();
			iw.open();
			iw.pmi_classify();
			/*
			IWrite iw = new IWrite();
			iw.open();
			iw.indexing(new BigDecimal(0));
			*/
		}else if(args[0].equals("update")){
			IWrite iw = new IWrite();
			iw.open();
			iw.indexing(new BigDecimal(0));
		}else if(args[0].equals("iw")){
			IWrite iw = new IWrite();
			iw.indexPath ="/home/tprpc/lucene/script/indexfiles";
			iw.days=1;
			iw.freq=100;
			iw.max_freq=10000;
			iw.type="_twitter";
			iw.pmi(2);
			iw.pmi_classify();
			
		}
		
		//Thread t = new Thread()
		//
		//동
		
		
				
		//server();

        

		//String r = "          ssdfwef adf sadfsdf                   ";
		//r = r.replaceFirst("\\s+", "");
		//System.out.println(client.morphAnalyze("안녕하세요?"));
		
		
		//String r = "	";
		//System.out.println(Integer.toHexString(r.getBytes("UTF-8")[0]));
		//System.out.println(Integer.toHexString(" ".getBytes("UTF-8")[0]));
		//r = r.trim();
		//build indexer from db
		//UpdateIndexer(0);
		
		//System.out.println("End Work!");
		//indexer.count();
		//long newt = System.currentTimeMillis();
		
		//System.out.println((newt-oldt));
		//normal search
		//indexer.search("", "segmented:독도 세레머니", null);
		
		//range search..
		//indexer.search("", "post_date:[19920614074126 TO 20130614074136] AND post_content:사람", null);
		
		//phrase search
		//indexer.search("title", "\"IOS\"~30", null);
		
		//search & sort by date
		//indexer.search("title", "\"content:신곡\"~30", new Sort(new SortField("update_date", SortField.STRING)));
	}

}
