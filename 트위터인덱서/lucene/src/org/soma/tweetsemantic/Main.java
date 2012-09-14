package org.soma.tweetsemantic;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

public class Main {
	
	private final static String path = "./indexfiles";
	private static Directory dir;
	private static boolean _initialized = false;
	private static Analyzer analyzer;
	private static IndexWriterConfig iwc;
	private static boolean create=false;

	private static int n = 0; // start 
	private static int until = 10000000;
	private static Connection conn;
	private static Statement stmt;
	private static Connection _conn;
	private static Statement _stmt;
	
	/**
	 * @param args
	 * @throws IOException 
	 * @throws ClassNotFoundException 
	 * @throws IllegalAccessException 
	 * @throws InstantiationException 
	 * @throws SQLException 
	 */
	public static void main(String[] args) throws IOException, InstantiationException, IllegalAccessException, ClassNotFoundException, SQLException {
		// TODO Auto-generated method stub
		System.out.println("tprpc indexer Start!");
		
		_initialized = true;
		/* 분리기 */
		String segmentXmlrpcServerUrl="http://twit.tprpc.com:9002";
		//String analyzeXmlrpcServerUrl="http://17.buzzni.com:9002/xmlrpc";		
		String analyzeXmlrpcServerUrl="http://office2.buzzni.com:10013";
		String opinionXmlrpcServerUrl=null;
		String result;
		BuzzniTaggerXmlRpcAPI client = new BuzzniTaggerXmlRpcAPI(segmentXmlrpcServerUrl, analyzeXmlrpcServerUrl,opinionXmlrpcServerUrl);
		/**/ 
		
		Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_31);
		IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_31, analyzer);
		dir = FSDirectory.open(new File(path));
		
		if (create) {
			// Create a new index in the directory, removing any
			// previously indexed documents:
			iwc.setOpenMode(OpenMode.CREATE);
		} else {
			// Add new documents to an existing index:
			iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
		}
		
		IndexWriter writer = new IndexWriter(dir, iwc);
		
		System.out.println("db connect!");

		Class.forName("com.mysql.jdbc.Driver").newInstance();
		conn = DriverManager.getConnection("jdbc:mysql://twit.tprpc.com/twit_manager?useUnicode=true&characterEncoding=UTF-8" ,"twit" ,"1rmdwjd");
		_conn = DriverManager.getConnection("jdbc:mysql://twit.tprpc.com/twit_manager?useUnicode=true&characterEncoding=UTF-8" ,"twit" ,"1rmdwjd");
		stmt = conn.createStatement();
		_stmt = conn.createStatement();
		
		ResultSet rs1 = stmt.executeQuery("SELECT * FROM `lucene_indexer` ORDER BY `no` DESC LIMIT 1"); 
		if(rs1.next()) {
			n = rs1.getInt("done");
		}
		rs1 = stmt.executeQuery("SELECT * FROM `tweet_data` ORDER BY `no` DESC LIMIT 1"); 
		if(rs1.next()) {
			int limit = rs1.getInt("no");
			if((n + 5000000) > limit) {
				until = limit-100;
			}else{
				until = n + 5000000;
			}
		}
		int size = 100;
		while(n < until) {
			System.out.println(String.format("%d",n));
			//System.out.println("read db");
			ResultSet rs = stmt.executeQuery(String.format("SELECT * FROM `tweet_data` WHERE `no` > %d AND %d >= `no` ORDER BY `no` ASC",n,size+n));
			System.out.println("read db done");
			
			while(rs.next())
			{
				String no = rs.getString("no");
				String twitid = rs.getString("twitid");
				String username = rs.getString("username");
				String timestamp = rs.getString("timestamp");
				
				String tweet = rs.getString("tweet");
				//String tweet_analysis = rs.getString("tweet_analysis");
				String tweet_analysis = client.autoSegment(tweet);
				
				String tweet_time = "";
				// 날짜 데이터 가져오기 
				ResultSet _rs = _stmt.executeQuery("SELECT DATE_ADD(`tweet_time`, interval +9 hour) FROM `tweet_timedata` WHERE `timestamp` <= '"+timestamp+"' ORDER BY `timestamp` DESC LIMIT 1");
				if(_rs.next()){
					
					tweet_time = _rs.getString(1);
					
					//System.out.println(tweet_time);
					tweet_time = tweet_time.replace(":", "").replace("-", "").replace(" ", "").substring(0,14);
					//System.out.println(no + "]" + timestamp + " => " + tweet_time);
				}
				
				_rs.close();
				
				// 없으면 그냥 넘김 ㅡㅡ
				if(tweet_analysis == null) continue;
				
				// 데이터 집어넣기
				Document doc = new Document();
				
				doc.add(new Field("id", no, Field.Store.YES, Field.Index.NO));
				doc.add(new Field("twitid", twitid, Field.Store.YES, Field.Index.NOT_ANALYZED));
				doc.add(new Field("post_title", username, Field.Store.YES, Field.Index.NOT_ANALYZED));
				doc.add(new Field("timestamp", timestamp, Field.Store.YES, Field.Index.NOT_ANALYZED));				
				doc.add(new Field("post_content", tweet, Field.Store.YES, Field.Index.NO));
				
				String url = "https://twitter.com/"+twitid+"/status/"+timestamp;
				doc.add(new Field("url", url, Field.Store.YES, Field.Index.NO));
				//System.out.println(url);
				doc.add(new Field("segmented", tweet_analysis, Field.Store.YES, Field.Index.ANALYZED));
				doc.add(new Field("post_date", tweet_time, Field.Store.YES, Field.Index.ANALYZED));
				
						
				writer.addDocument(doc);
				
			}
			n += size;
			
		}
		stmt.executeUpdate(String.format("INSERT INTO `lucene_indexer` (`done`) VALUES ('%d')",n)); 
		stmt.close();
		_stmt.close();
		conn.close();
		_conn.close();
		writer.close();
	}

}
