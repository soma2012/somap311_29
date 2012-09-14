package test;

import java.io.File;
import java.io.IOException;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.RAMDirectory;
import org.apache.lucene.util.Version;

public class IWriterBase {
	
	
	protected String indexPath;
	public IndexWriter writer = null;

	
	protected void open() throws IOException{
		//RAMDirectory dir = RAMDirectory.open(new File(indexPath));
	    Directory dir = FSDirectory.open(new File(indexPath));
	    Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
	        IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_36, analyzer);
	        
	        boolean create=false;
	        if (create) {
	          // Create a new index in the directory, removing any
	          // previously indexed documents:
	          iwc.setOpenMode(OpenMode.CREATE);
	        } else {
	          // Add new documents to an existing index:
	          iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
	        }
	        writer = new IndexWriter(dir, iwc);
	}
	

}
