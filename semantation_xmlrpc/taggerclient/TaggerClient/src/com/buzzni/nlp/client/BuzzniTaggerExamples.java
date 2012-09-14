package com.buzzni.nlp.client;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;

import com.mysql.jdbc.PreparedStatement;

public class BuzzniTaggerExamples {

	public static void main(String[] args) throws InstantiationException, IllegalAccessException, ClassNotFoundException {
		int cnt = 10000000;
		int term = 100;
		int until = 15000000;
		String segmentXmlrpcServerUrl="http://twit.tprpc.com:9004/xmlrpc";
		//String analyzeXmlrpcServerUrl="http://17.buzzni.com:9002/xmlrpc";		
		String analyzeXmlrpcServerUrl="http://office2.buzzni.com:10013";
		//String analyzeXmlrpcServerUrl="http://office2.buzzni.com:10013";
		//String analyzeXmlrpcServerUrl="http://office2.buzzni.com:10014";
		String opinionXmlrpcServerUrl=null;
		String result;
		BuzzniTaggerXmlRpcAPI client = new BuzzniTaggerXmlRpcAPI(segmentXmlrpcServerUrl, analyzeXmlrpcServerUrl,opinionXmlrpcServerUrl);
		
		System.out.println("initialize done");
		try
		{
			Class.forName("com.mysql.jdbc.Driver").newInstance();
			Connection conn = DriverManager.getConnection("jdbc:mysql://twit.tprpc.com/twit_manager?useUnicode=true&characterEncoding=UTF-8" ,"twit" ,"1rmdwjd");
			Connection outconn = DriverManager.getConnection("jdbc:mysql://twit.tprpc.com/twit_manager?useUnicode=true&characterEncoding=UTF-8" ,"twit" ,"1rmdwjd");
			Statement stmt = conn.createStatement();
			java.sql.PreparedStatement output_stmt;
			
			while(cnt < until) {
				System.out.println("read db");

				ResultSet rs = stmt.executeQuery(String.format("SELECT * FROM `tweet_data` WHERE `no` > %d ORDER BY `no` ASC LIMIT %d",cnt,term));

				System.out.println("read db done");
				System.out.println(String.format("%d",cnt));
				while(rs.next())
				{
					String no = rs.getString("no");
					String tweet = rs.getString("tweet");
					//System.out.print(String.format("%d[%s] : ",cnt,no));
					//System.out.print(tweet + " -> ");
					
					result = client.autoSegment(tweet);
					//System.out.println("auto segmentation demo");
					//System.out.println(result);
					//System.out.println("morph analyzer demo");
					//result = client.morphAnalyze(tweet);
					//System.out.println(result);
					
					output_stmt = outconn.prepareStatement("UPDATE `tweet_data` SET `tweet_analysis` = ? WHERE `no` = ?");
					output_stmt.setString(1, result);
					output_stmt.setString(2, no);
					output_stmt.executeUpdate();
					//System.out.println("ok!");
					
				}
				cnt += term;
			}
			
		}catch(Exception e)
		{
			e.printStackTrace();
		}finally
		{
			
		}
		
//		System.out.println("opinion analyzer demo");
//		ArrayList<HashMap<String,String>> resultlist = client.opinionAnalysis("");
//		for (HashMap<String, String> hashMap : resultlist) {
//			System.out.println("attribute:"+hashMap.get("attribute"));
//			System.out.println("expression:"+hashMap.get("expression"));
//			System.out.println("polarity:"+hashMap.get("polarity"));
//			System.out.println("snippet:"+hashMap.get("snippet"));
//			System.out.println("score:"+hashMap.get("score"));
//		}
		
	}

}
