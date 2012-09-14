package test;

import java.io.File;
import java.io.IOException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;
import java.util.TreeMap;
import java.util.Vector;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.Sort;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.highlight.Highlighter;
import org.apache.lucene.search.highlight.InvalidTokenOffsetsException;
import org.apache.lucene.search.highlight.QueryScorer;
import org.apache.lucene.search.highlight.SimpleHTMLFormatter;
import org.apache.lucene.search.highlight.TextFragment;
import org.apache.lucene.search.highlight.TokenSources;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

public class ITwitterReader extends IReaderBase{
	static IndexSearcher searcher=null;
	//static Postgres db = new Postgres();
	
	public ITwitterReader() throws IOException{
		if(searcher==null)
		searcher= this.open("/home/tprpc/lucene/script/indexfiles");
	}
	
	/*
	public String[] get_pmi_relate(int prev, String word) throws SQLException{
		String time = SimpleTime.getPrevDay(prev);
		
		ResultSet rs = db.Query("select * from pmi_keyword where date=" + time + " and word='" + word + "'");
		if(!rs.next())
		return new String[0];
		
		int id = rs.getInt("id");
		
		rs = db.Query("select count(*) from pmi_relate where pmi_id=" + id);
		if(!rs.next())
		return new String[0];
		
		String[] ret = new String[rs.getInt(1)];
		
		rs = db.Query("select * from pmi_relate where pmi_id=" + id + " order by pmi desc");
		int i=0;
		while(rs.next()){
			ret[i]= rs.getString("word");
			i++;
		}
		
		return ret;
	}
	
	public int get_pmi_size(int prev) throws SQLException{
		String time = SimpleTime.getPrevDay(prev);
		ResultSet rs = db.Query("select count(*) from pmi_keyword where date=" + time);
		if(!rs.next())
		return 0;
		
		return rs.getInt(1);
	}

	public String[] get_pmi(int prev) throws SQLException{
		
		String time = SimpleTime.getPrevDay(prev);
		ResultSet rs = db.Query("select count(*) from pmi_keyword where date=" + time);
		rs.next();
		String[] ret = new String[rs.getInt(1)];
		
		rs = db.Query("select * from pmi_keyword where date=" + time + " order by pmi desc");
		int i=0;
		while(rs.next()){
			ret[i]= rs.getString("word");
			i++;
		}
		return ret;
	}
	*/
	
	public String safe_get(Document doc, String field){
		String ret ="";
		if(doc.get(field)!=null)
			ret= doc.get(field);
		else
			ret = "";
		//System.out.println(field +" " + ret);
		return ret;
	}
	
	public Vector<Hashtable<String,String> > query(String s, String subject, String from, String to) throws CorruptIndexException, IOException, ParseException, InvalidTokenOffsetsException{
		WhitespaceAnalyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
		
		QueryParser parser  = new QueryParser(Version.LUCENE_36, "segmented", analyzer);
		//s = Lucene.client.autoSegment(s);
		//System.out.println(s);
		String[] sprite = s.split(" ");
		
		ScoreDoc[] docs;
		
		
		
		String q="";
		
		if(from.length()==14 && to.length()==14){
			q+="post_date:["+ from + " TO " + to + "] AND ";
		}else if(from.length()==14){
			q+="post_date:["+ from + " TO " + "21000000000000" + "] AND ";
		}else if(to.length()==14){
			q+="post_date:["+ "20000000000000" + " TO " + to + "] AND ";
		}
		
		
		
		
		if(subject.length()==0)
			q+="segmented:" + s;
		else
			q+="segmented:" + s + " AND subject:" + subject;
		
		docs = this.search(searcher, parser.parse(q));
		
		Vector<Hashtable<String,String> > result = new Vector<>();

		System.out.println(q);
		System.out.println(docs.length);
		
		SimpleHTMLFormatter htmlFormatter = new SimpleHTMLFormatter();
		Highlighter highlighter = new Highlighter(htmlFormatter, new QueryScorer(parser.parse(s)));
		
		//id score search
		
		
		for (int i=0; i<100 && i<docs.length; ++i){
				
			Document doc = searcher.doc(docs[i].doc);
			
			String docResult="";
			
			Hashtable<String, String> ret = new Hashtable<>();
			
			
			
			//docResult +="doc="+docs[i].doc+" score="+docs[i].score + "\n";
			
			TokenStream Stream = TokenSources.getAnyTokenStream(searcher.getIndexReader(), docs[i].doc, "post_content", analyzer);
	       TextFragment[] frag;
	       	
	       String content = doc.get("post_content");
	       for (String tmp : sprite) {
	    	   content = content.replaceAll(tmp, " " + tmp + " ");
	        }

	       //System.out.println(content);
	        //////////주석
	       
	       docResult+=highlighter.getBestFragment(analyzer, "", content);
	       //System.out.println(content);
	       //System.out.println(docResult);
	       
	       docResult = docResult.replaceAll(" (<B>.*?</B>) ", "$1");
	       //System.out.println(docResult);
	       ///try{
		    ret.put("id", safe_get(doc,"twitid"));
		    ret.put("content", docResult);
		    ret.put("url", safe_get(doc,"url"));
		    ret.put("date", safe_get(doc,"post_date"));
		    ret.put("subject", safe_get(doc,"subject"));
		    ret.put("score", Float.toString(docs[i].score));
		    result.add(ret);
	       //}catch(Exception err){
	    	//   continue;
	       //}
		    System.out.println(docResult);
		}
		
		return result;
		
	}
	
}
