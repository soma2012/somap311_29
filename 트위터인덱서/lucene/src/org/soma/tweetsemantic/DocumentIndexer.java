package org.soma.tweetsemantic;

import java.io.File;
import java.io.IOException;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.LockObtainFailedException;
import org.apache.lucene.util.Version;

public class DocumentIndexer {

	/**
	 * @param args
	 * @throws IOException
	 * @throws LockObtainFailedException
	 * @throws CorruptIndexException
	 */
	private final String path = "c:\\lucene";
	private static Directory dir;
	private static boolean _initialized = false;
	private static Analyzer analyzer;
	private static IndexWriterConfig iwc;
	private boolean create=false;
	public DocumentIndexer() {
		_initialized = true;
		Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_31);
		IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_31, analyzer);
		//dir = FSDirectory.open(new File(path));
		
		if (create) {
			// Create a new index in the directory, removing any
			// previously indexed documents:
			iwc.setOpenMode(OpenMode.CREATE);
		} else {
			// Add new documents to an existing index:
			iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
		}
	}
	public static void index() throws CorruptIndexException, LockObtainFailedException, IOException {
		
	

		// Optional: for better indexing performance, if you
		// are indexing many documents, increase the RAM
		// buffer.  But if you do this, increase the max heap
		// size to the JVM (eg add -Xmx512m or -Xmx1g):
		//
		// iwc.setRAMBufferSizeMB(256.0);

		IndexWriter writer = new IndexWriter(dir, iwc);
		Document doc = new Document();
		Field pathField = new Field("path", "c:\\java\\test", Field.Store.YES, Field.Index.NOT_ANALYZED_NO_NORMS);
		Field dataField = new Field("data", "this is test", Field.Store.YES, Field.Index.ANALYZED);
		Field dateField = new Field("date", "time", Field.Store.YES, Field.Index.ANALYZED);
		doc.add(pathField);
		doc.add(dataField);
		doc.add(dateField);
		
				
		writer.addDocument(doc);
		
		//       indexDocs(writer, docDir);

		// NOTE: if you want to maximize search performance,
		// you can optionally call optimize here.  This can be
		// a costly operation, so generally it's only worth
		// it when your index is relatively static (ie you're
		// done adding documents to it):
		//
		// writer.optimize();

		writer.close();       
	}
	/*
	private static void searchTest() throws CorruptIndexException, IOException,
	ParseException {
		IndexSearcher searcher = new IndexSearcher(FSDirectory.open(new File(
				indexPath)));
		Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_31);
		String field = "data";
		QueryParser parser = new QueryParser(Version.LUCENE_31, field, analyzer);
		String queryStr = "test";
		Query query = parser.parse(queryStr);
		int hitsPerPage = 10;
		TopDocs results = searcher.search(query, 5 * hitsPerPage);
		ScoreDoc[] hits = results.scoreDocs;

		int numTotalHits = results.totalHits;
		System.out.println(numTotalHits + " total matching documents");

		int start = 0;
		int end = Math.min(numTotalHits, hitsPerPage);

		end = Math.min(hits.length, start + hitsPerPage);
		for (int i = start; i < end; i++) {
			System.out
			.println("doc=" + hits[i].doc + " score=" + hits[i].score);
			Document doc = searcher.doc(hits[i].doc);
			String path = doc.get("path");
			String data = doc.get("data");
			System.out.println(path + ":" + data);
		}
	}*/

}