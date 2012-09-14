package test;

import java.io.File;
import java.io.IOException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

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

public class IClassifyReader extends IReaderBase{
	protected static IndexSearcher searcher=null;
	public IClassifyReader() throws IOException{
		if(searcher==null)
		searcher = this.open("/home/xorox90/subject/");
	}
	
	public String getSubject(String querystr) throws CorruptIndexException, IOException, ParseException, InvalidTokenOffsetsException{
		/*
		String[] sprite = querystr.split(" ");
		querystr="";
		
		

		for(int i=0; (i<900 && i<sprite.length); ++i){
			querystr+=sprite[i] + " ";
			//querystr+=sprite[i] + " OR ";
		}
		querystr = querystr.trim();
		//querystr = querystr.substring(0, querystr.length()-3);
		querystr = "content:" + querystr;
		ScoreDoc[] score = this.search(parser.parse(querystr));
		
		
		
		Map<String, Integer> map = new HashMap<>();

		String[] arr = new String[]{"adult","animation", "book", "car", "childcare", "commercial", "economy", "fashion", "food", "game", "health", "it", "love", "movie", "pet", "politics", "science", "sports", "travel", "world"};
		for (int i = 0; i < arr.length; i++) {
			map.put(arr[i], 0);
		}
		

		/*
		String sub="none";
		float temp=1;
		for (ScoreDoc scoreDoc : score) {
			 
			//float buf=scoreDoc.score*100/(map.get(searcher.doc(scoreDoc.doc).get("subject")));
			//if(temp>buf)
			//{
			//	System.out.println(String.format("%10f", buf));
			//	temp=buf;
			//	sub=searcher.doc(scoreDoc.doc).get("subject");
			//}
			 
		}
		
		
		System.out.println("end!");
		if(temp!=1){
		Document doc = searcher.doc(score[0].doc);
		return sub + " " + String.format("%20f", temp);
		//return doc.get("subject");
		}else{
		return "none 1.0";
		}
		*/
		
		
		/*
		System.out.println(score.length);
		for(int i=0; i<score.length; ++i){
			Document doc = searcher.doc(score[i].doc);
			//System.out.println(doc.get("subject") + String.format("%20f",score[i].score*100 + 0.00001/map.get(doc.get("subject"))));
			System.out.println(doc.get("subject") + String.format("%20f",score[i].score*100));
			
		}
		System.out.println("#####");
		*/
		/*
		Integer max=0;
		String sub="none";
		for(int i=0; (i<20 && i<score.length); ++i){
			Document doc = searcher.doc(score[i].doc);
			//System.out.println(doc.get("subject"));
			Integer s = map.get(doc.get("subject"))+1;
			if(s>max){
				s=max;
				sub=doc.get("subject");
			}
			map.put(doc.get("subject"), s);
		}
		
		return sub;
		/*
		if(score.length>=1 && score[0].score*100>0.000020){
		Document doc = searcher.doc(score[0].doc);
		return doc.get("subject") + " " + String.format("%20f", score[0].score);
		//return doc.get("subject");
		}else{
		return "none 0.1";
		}
		*/
		return "";
	}
	
	
	//data test
	

}
