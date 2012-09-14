package test;

import java.io.File;
import java.io.IOException;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
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

public class IReaderBase {
	
	
	protected static IndexSearcher open(String indexPath) throws IOException{
		Directory dir =FSDirectory.open(new File(indexPath));
		return new IndexSearcher(IndexReader.open(dir));
	}
	
	protected ScoreDoc[] search(IndexSearcher searcher, Query query) throws CorruptIndexException, IOException, ParseException, InvalidTokenOffsetsException {
		/*
		Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
		QueryParser parser = new QueryParser(Version.LUCENE_36, "", analyzer);
	    //make query from queryparser
	    
		Query query = parser.parse(queryStr);
	    */
	    //System.out.println(query.)
	    int hitsPerPage=1000;
	   
	    
	    TopDocs results;
	    
	    //searcher.s
	    //System.out.println(reader.numDocs() + " total docs");
	    //if(sort==null)
	    //

	    results = searcher.search(query, searcher.maxDoc());
	    //else
	    //results = searcher.search(query, 5 * hitsPerPage, sort);
	    
	    ScoreDoc[] hits = results.scoreDocs;
	    return hits;
	}
}
