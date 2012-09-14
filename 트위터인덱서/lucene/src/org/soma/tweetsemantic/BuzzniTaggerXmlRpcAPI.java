package org.soma.tweetsemantic;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

public class BuzzniTaggerXmlRpcAPI {
	private XmlRpcClient client;
	private XmlRpcClient analyzeClient;
	private XmlRpcClient opinionClient;
	public BuzzniTaggerXmlRpcAPI(String segmentXmlrpcServerUrl,String analyzeXmlrpcServerUrl,String opinionXmlrpcServerUrl) {
		XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
		config.setEnabledForExtensions(true);
	    try {
			config.setServerURL(new URL(segmentXmlrpcServerUrl));
		} catch (MalformedURLException e1) {
			e1.printStackTrace();
		}
	    client = new XmlRpcClient();
	    client.setConfig(config);
	    
		XmlRpcClientConfigImpl analyzeConfig = new XmlRpcClientConfigImpl();
		analyzeConfig.setEnabledForExtensions(true);
	    try {
	    	analyzeConfig.setServerURL(new URL(analyzeXmlrpcServerUrl));
		} catch (MalformedURLException e1) {
			e1.printStackTrace();
		}
		analyzeClient = new XmlRpcClient();
		analyzeClient.setConfig(analyzeConfig);
	    
		XmlRpcClientConfigImpl opinionConfig = new XmlRpcClientConfigImpl();
		opinionConfig.setEnabledForExtensions(true);
		if(opinionXmlrpcServerUrl!=null) {
			try {
				opinionConfig.setServerURL(new URL(opinionXmlrpcServerUrl));
			} catch (MalformedURLException e1) {
				e1.printStackTrace();
			}
		}
		opinionClient = new XmlRpcClient();
		opinionClient.setConfig(opinionConfig);
	}	
	public String autoSegment(String sentence) {
		
	    Object[] params = new Object[]{sentence};
	    Object resultObjet = null;
	    try {
	    	resultObjet = (Object )client.execute("BuzzniTagger.segmentRpc", params);
		} catch (XmlRpcException e) {
			e.printStackTrace();
		}	
		return (String)resultObjet;
	}	
	public String morphAnalyze(String sentence ) {
		
	    Object[] params = new Object[]{sentence};
	    Object resultObjet = null;
	    try {
	   // 	resultObjet = (Object )analyzeClient.execute("BuzzniTagger.posTaggingRpc", params);
	    	resultObjet = (Object )analyzeClient.execute("BuzzniTagger.postagging", params);
		} catch (XmlRpcException e) {
			e.printStackTrace();
		}	
		return (String)resultObjet;
	}		
	public ArrayList<HashMap<String,String>> opinionAnalysis(String sentence ) {
		
	    Object[] params = new Object[]{sentence};
	    Object[] resultObjet = null;
	    try {
	    	resultObjet = (Object [])opinionClient.execute("BuzzniTagger.opnTaggingRpc", params);
		} catch (XmlRpcException e) {
			e.printStackTrace();
		}
		ArrayList<HashMap<String,String>> resultlist = new ArrayList<HashMap<String,String>>();
		for(Object object : resultObjet) {
			HashMap<String,String> infomap = new HashMap<String, String>();
			String[] strlist = ((String)object).split("\t");
			infomap.put("attribute", strlist[0].split(":")[1]);
			infomap.put("expression", strlist[1].split(":")[1]);
			infomap.put("polarity", strlist[2].split(":")[1]);
			infomap.put("snippet", strlist[3].split(":")[1]);
			infomap.put("score", strlist[4].split(":")[1]);
			resultlist.add(infomap);
		}
		return resultlist;
	}			
}
