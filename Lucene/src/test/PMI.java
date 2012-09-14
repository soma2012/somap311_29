package test;

import java.io.IOException;
import java.util.List;
import java.util.Vector;

import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.util.Version;

public class PMI extends Thread {
	
	IndexSearcher searcher;
	List<String> words;
	static String from,to;
	Vector<Keyword> ret;
	static int total;
	
	public PMI (IndexSearcher searcher, List<String> words, Vector<Keyword> ret){
		this.searcher = searcher;
		this.words = words;
		this.ret = ret;
	}
	
    public void run() {
    	
		QueryParser parser = new QueryParser(Version.LUCENE_36, "", new WhitespaceAnalyzer(Version.LUCENE_36));
		Query query;
		TopDocs result;
		
		int idx=0;
		int goal=100;
		
		System.out.println("PMI Proccess start... ");
		
		for (String key : words) {
			
			
			int x_y=0, x=0, y=0;
			
			try {
				query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + key);
				result = searcher.search(query, searcher.maxDoc()/10);
				x_y = result.totalHits;
				//System.out.println(specify);

				query = parser.parse("post_date:[" + from + " TO " + to + "]");
				result = searcher.search(query, searcher.maxDoc()/10);
				x = result.totalHits;
				
				query = parser.parse("segmented:" + key);
				result = searcher.search(query, searcher.maxDoc()/10);
				y = result.totalHits;
				
			} catch (ParseException | IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
			idx+=1;
			//System.out.println("PMI Proccessing... " + Integer.toString(x_y) + " " + Integer.toString(x) + " " + Integer.toString(y));
			if(idx>=goal){
				System.out.println("PMI Proccessing... " + Integer.toString(idx));
				goal+=100;
			}
			
			double pmi;
			
			//erase too common words
			if(x_y!=0 && (x*y)!=0 && (pmi=Math.log((double)((x_y*total/(x*y)))))>=1.9 && pmi<=4.0){
				System.out.println(key + " " + Double.toString(pmi));
				ret.add(new Keyword(key, pmi));

			}else{
				//System.out.println("GGG");
			}
		}

	 }
    
}
