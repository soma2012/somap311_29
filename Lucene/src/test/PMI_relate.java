package test;

import java.util.List;

import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.util.Version;

public class PMI_relate extends Thread {
	
	IndexReader reader;
	List<Keyword> words;
	public PMI_relate (IndexReader reader, List<Keyword> words, int start, int end){
		this.reader = reader;
		this.words = words;
	}
	
    public void run() {
    	
    	/*
		QueryParser parser = new QueryParser(Version.LUCENE_36, "", new WhitespaceAnalyzer());
		Query query;
		TopDocs result;
		
		query = parser.parse("post_date:[" + from + " TO " + to + "] AND " + terms_enum.term().toString());
		result = searcher.search(query, searcher.maxDoc());
		int x_y = result.totalHits;
		//System.out.println(specify);

		query = parser.parse("post_date:[" + from + " TO " + to + "]");
		result = searcher.search(query, searcher.maxDoc());
		int x = result.totalHits;
		
		query = parser.parse(terms_enum.term().toString());
		result = searcher.search(query, searcher.maxDoc());
		int y = result.totalHits;
		
		
		
		
		double pmi;
		
		
		//erase too common words
		if(x_y!=0 && (x*y)!=0 && (pmi=Math.log((double)((x_y*total/(x*y)))))>=1.7){
			
			today.add(new Keyword(terms_enum.term().text(), pmi));

		}
		*/

	 }
    
}
