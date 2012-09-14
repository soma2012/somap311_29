package test;


import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.LinkedList;
import java.util.Locale;
import java.util.Set;
import java.util.List;
import java.util.Vector;
import java.util.regex.Pattern;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.Field.Index;
import org.apache.lucene.document.Field.Store;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.TermEnum;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
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
import org.apache.lucene.store.LockObtainFailedException;
import org.apache.lucene.util.Version;


import javax.naming.spi.DirStateFactory.Result;

public class IWrite extends IWriterBase {
	
	/**
	 * @param args
	 * @throws IOException
	 * @throws LockObtainFailedException
	 * @throws CorruptIndexException
	 */
	
	
	Postgres db = new Postgres();
	
	public IWrite(){
		indexPath="/home/xorox90/blog/";
	}
	
	
	public int days=1;
	public String type="";
	public int freq=30;
	public int max_freq;

	public void update() throws SQLException, InterruptedException, IOException, ParseException{
		
		this.open();
		
		while(true){
			ResultSet rst = db.Query("select * from lucene_update order by date desc limit 1");
			rst.next();
			
			
			BigDecimal last_update = rst.getBigDecimal("date");
			BigDecimal last_index = rst.getBigDecimal("indexed");
			BigDecimal current_update = new BigDecimal(SimpleTime.getPrevTime(6));
			
			
			

			//마지막 업데이트로 6시간 지나면 업데이트 함 <0으로 수정할 것!
			if(last_update.compareTo(current_update)<0){
				System.out.println("Update need! " + SimpleTime.getPrevTime(0));		
				
				
				
				//erase too old data
				
				
				this.indexing(last_index);
				//this.clean(7);
				//pmi between from now to 14 days
				this.pmi(7);
				pmi_classify();
				
				//cache relate doc
				//this.cache()
			}
			
			
			
			//60 seconds 
			Thread.sleep(1000); 
			
		}
		
	}
	
	public void get_last() throws IOException{
		Directory dir =FSDirectory.open(new File(indexPath));	
		IndexReader reader = IndexReader.open(dir);
		IndexSearcher searcher = new IndexSearcher(reader);
		//System.out.prisearcher.doc(reader.numDocs())
		
		
	}
	
	public void pmi_classify() throws SQLException{
		
			ResultSet rs=db.Query("select * from pmi_keyword" + type +" where subject is null order by date");
			while(rs.next()){
				String word = rs.getString("word");
				String day = rs.getBigDecimal("date").toString();
				
				System.out.println(word);
				Vector<HashMap<String, String>> ret = Lucene.client.query(word, "all", "", "");
				String subject="none";

				HashMap<String, Integer> score = new HashMap<>();
				int index=0;
				int max=0;
				String best="none";
				for (HashMap<String, String> hashMap : ret) {
					String c=hashMap.get("subject");
					Integer cur = score.get(c);
					if(cur==null)
						cur=0;
					
					
					score.put(c, cur+1);

					if(max<cur+1){
						max=cur+1;
						subject=c;
					}
					
					if(index==0)
						best = c;

					index++;
					
					if(index>3)
						break;
				}
				
				if(max==1)
					subject=best;
				

				
				db.execute("update pmi_keyword" + type+" set subject='" + subject + "' where id=" + rs.getInt("id"));
				db.Commit();
				
			}

	}
	
	public void clean(int day) throws CorruptIndexException, IOException, ParseException{
		Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
		QueryParser parser = new QueryParser(Version.LUCENE_36,"", analyzer);
		System.out.println("before clean " + writer.numDocs());
		writer.deleteDocuments(parser.parse("post_date:[20000000000000 TO " + SimpleTime.getPrevDay(day+1) + "]"));
		writer.commit();
		System.out.println("cleaned! " + writer.numDocs());
		
		
	}
	
	//indexing from index<start to last
	public void indexing(BigDecimal start) throws CorruptIndexException, IOException{

		BigDecimal chunk_size= new BigDecimal(10000);
		
		BigDecimal current= start;
		
			try{
				ResultSet rs =null;
				
				rs = db.Query("select count(*) from blog");
				rs.next();
				int num = rs.getInt(1);

				System.out.println("total number of rows.. " + num );
				
				long oldt=System.currentTimeMillis(),newt=System.currentTimeMillis();
				while(true){
					System.out.println("current row is " + current);
					System.out.println("elasped time.. "  + (newt-oldt));
					oldt = System.currentTimeMillis();
					
					
					rs =db.Query("select * from blog where id > " + current + " order by id asc limit "+ chunk_size.toString());
					if(!rs.next()){
						break;
					}else{
						do{
								
							 Document doc = new Document();
							
								int id=rs.getInt("id");
								BigDecimal post_date = rs.getBigDecimal("post_date");
								String post_title = rs.getString("post_title");
								String post_content = rs.getString("post_content");
								String segmented = rs.getString("segmented");
								String subject = rs.getString("subject");
								String url = rs.getString("post_url");
								String score = String.format("%04d", Math.round(rs.getFloat("score")));
								
								if(segmented==null)
									segmented="";
								
								if(subject==null)
									subject="";
								
							 Field field = new Field("id", Integer.toString(id), Store.YES,Index.NO);
							 doc.add(field);
							 field = new Field("post_date", post_date.toString(), Store.YES,Index.NOT_ANALYZED);
							 doc.add(field);
							 field = new Field("post_title", post_title, Store.YES,Index.NO);
							 doc.add(field);
							 field = new Field("post_content", post_content, Store.YES,Index.NO);
							 doc.add(field);
							 field = new Field("segmented", segmented, Store.YES,Index.ANALYZED);
							 doc.add(field);
							 field = new Field("subject", subject, Store.YES, Index.NOT_ANALYZED);
							 doc.add(field);
							 field = new Field("url", url, Store.YES, Index.NO);
							 doc.add(field);
							 field = new Field("sub_score", score, Store.YES, Index.NOT_ANALYZED);
							 doc.add(field);
							 writer.addDocument(doc);
							 
							current = current.add(new BigDecimal(1));
								
								
								
					}while(rs.next());
					newt = System.currentTimeMillis();
					}
					
					rs.close();

					db.execute("insert into lucene_update (date,indexed) values (" + SimpleTime.getPrevTime(0) + ", " + current.toString() + ")");
					writer.commit();
					db.Commit();
					
				}
				}
				catch (SQLException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
	}
	
	
	public void classify(int date) throws IOException, ParseException, SQLException{
		
		Directory dir =FSDirectory.open(new File(indexPath));	
		IndexReader reader = IndexReader.open(dir);
		IndexSearcher searcher = new IndexSearcher(reader);
		
		Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
		QueryParser parser = new QueryParser(Version.LUCENE_36,"", analyzer);

		
		TermEnum terms_enum =  reader.terms();
		List<String> words = new LinkedList<>();
		int count=0;
		while(terms_enum.next()){
			//System.out.println(terms_enum.term().text());
			//erase too low frequency words
			if(terms_enum.docFreq()>10 && terms_enum.term().text().matches("[가-힣]+")){
				words.add(terms_enum.term().text());
				count++;
			}
	
		}
		
		
		System.out.println("pmi keyword updated! total keyword number " + count);
		
		Query query;
		TopDocs result;
		
		for(int p=0; p<date; p+=days){
			String from = SimpleTime.getPrevDay((p+7));
			String to = SimpleTime.getPrevDay(p);
			

			ResultSet rs = db.Query("select * from pmi_index where date=" + to);
			if(!rs.next()){
				db.execute("insert into pmi_index (date,indexed,days) VALUES(" + to + ",0," + days + ")");
				db.Commit();
				rs = db.Query("select * from pmi_index where date=" + to);
				rs.next();
			}
			
			
			int num= searcher.maxDoc();
			int last_indexed = rs.getInt("indexed");
			
			query = parser.parse("post_date:[" + from + " TO " + to + "]");
			result = searcher.search(query, searcher.maxDoc());
			int current_indexed = result.totalHits;
			

			//refresh if indexed doc changed 
			if(current_indexed > last_indexed+100){
				
				System.out.println("pmi update " + to + " number of docs " + current_indexed + " " + SimpleTime.getPrevTime(0));
				
				
				
				ResultSet old = db.Query("select * from pmi_keyword where date=" + to);
				while(old.next()){
					int id = old.getInt("id");
					db.execute("delete from pmi_relate where pmi_id=" + id);
				}
				db.execute("delete from pmi_keyword where date=" + to);
				db.Commit();
				
				int total = reader.numDocs();
				
				PreparedStatement st = db.getPreparedStatement("insert into pmi_keyword (word,date,pmi) values (?,?,?)");
				
				
				System.out.println("pmi keyword update start! " + SimpleTime.getPrevTime(0));
				
				List<String> t = new ArrayList<String>();
				count = 0;
				for (String key : words) {
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + key);
					result = searcher.search(query, searcher.maxDoc());
					if(result.totalHits>10){
						t.add(key);
						count++;
					}
				}
				
				System.out.println("pmi keyword updated! total selected keyword number " + count);
				
				PMI.from = from;
				PMI.to = to;
				PMI.total = total;
				
				Vector<Keyword> ret = new Vector<>();
				
				int start=0;
				int core=8;
				int words_size = t.size();
				int chunk=words_size%core==0?words_size/core:words_size/core+1;
				
				Thread[] thread = new Thread[8];
				
				for(int i=0; i<core; ++i){
					thread[i] = new PMI(searcher, t.subList(start, start+chunk), ret);
					thread[i].start();
					
					start+=chunk;
					if((start+chunk)>t.size()){
						chunk = t.size()-start;
					}
				}
				
				for(int i=0; i<core; ++i){
					try {
						thread[i].join();
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}

				
				System.out.println("size of array " + ret.size());
				List<Keyword> today = new ArrayList<>(ret);
				Collections.sort(today);
				//today = today.subList(0, today.size()<200?today.size():200);
				
				String[] arr = new String[today.size()];
				
				for (int i=0; i<today.size();++i) {
					Keyword key = today.get(i);
				
					st.setString(1, key.keyword);
					st.setBigDecimal(2, new BigDecimal(to));
					st.setDouble(3, key.pmi);
					st.executeUpdate();
					arr[i] = key.keyword;
				}
				
				
						
				System.out.println("pmi keyword updated! " + SimpleTime.getPrevTime(0));
				System.out.flush();
				db.Commit();
				
				/*
				//pmi 
				st = db.getPreparedStatement("insert into pmi_relate (pmi_id, word, pmi) values (?,?,?)");
				PreparedStatement st2 = db.getPreparedStatement("select * from pmi_keyword where date=? and word=?");
				for(int i=0; i<arr.length; ++i){
					
					st2.setBigDecimal(1, new BigDecimal(to));
					st2.setString(2, arr[i]);
					rs = st2.executeQuery();
					if(!rs.next())
						continue;
					int id = rs.getInt("id");
					
				
					for(int j=i+1; j<arr.length; ++j){
						//phrase search
						query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:\"" + arr[i] + " " + arr[j] + "\"~3");
						result = searcher.search(query, searcher.maxDoc());
						int x_y = result.totalHits;
						
						query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[i]);
						result = searcher.search(query, searcher.maxDoc());
						int x = result.totalHits;
						
						query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[j]);
						result = searcher.search(query, searcher.maxDoc());
						int y = result.totalHits;
						
						double pmi;
						if(x_y!=0 && (x*y)!=0 && (pmi=Math.log((double)((x_y*total/(x*y)))))>=4){


							st.setInt(1, id);
							st.setString(2, arr[j]);
							st.setDouble(3, pmi);
							st.executeUpdate();
							db.Commit();

							
							
							
						}
					}
				}
				*/
				
				System.out.println("pmi relate updated! " + SimpleTime.getPrevTime(0));
				
				db.execute("update pmi_index set indexed=" + current_indexed + " where date=" + to);
			}
		}
	}

	public void pmi(int date) throws IOException, ParseException, SQLException{
		
		Directory dir =FSDirectory.open(new File(indexPath));	
		IndexReader reader = IndexReader.open(dir);
		IndexSearcher searcher = new IndexSearcher(reader);
		
		Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
		QueryParser parser = new QueryParser(Version.LUCENE_36,"", analyzer);

		
		TermEnum terms_enum =  reader.terms();
		
	   max_freq=searcher.maxDoc()/100;
		
		List<String> words = new LinkedList<>();
		int count=0;
		while(terms_enum.next()){
			//System.out.println(terms_enum.term().text());
			//erase too low frequency words
			if(terms_enum.docFreq()>freq && terms_enum.docFreq()<max_freq &&  terms_enum.term().text().length()>1 && terms_enum.term().text().matches("[가-힣]+")){
	
				
				words.add(terms_enum.term().text());
				count++;
			}
	
		}
		
		
		System.out.println("pmi keyword updated! total keyword number " + count);
		
		Query query;
		TopDocs result;
				
		for(int p=0; p<date; p+=days){
			String from = SimpleTime.getPrevDay((p+days));
			String to = SimpleTime.getPrevDay(p);
			
			ResultSet rs= db.Query("select * from pmi_index" + type+" where date=" + to);

			
			
			if(!rs.next()){

				db.execute("insert into pmi_index" +type+" (date,indexed,days) VALUES(" + to + ",0," + days+ ")");

				db.Commit();

				rs = db.Query("select * from pmi_index"+type+" where date=" + to);
				
				rs.next();
			}
			
			
			int num= searcher.maxDoc();
			int last_indexed = rs.getInt("indexed");
			
			query = parser.parse("post_date:[" + from + " TO " + to + "]");
			result = searcher.search(query, searcher.maxDoc());
			int current_indexed = result.totalHits;
			
			System.out.println("pmi update " + to + " number of docs " + current_indexed + " " + SimpleTime.getPrevTime(0));
			//refresh if indexed doc changed 
			if(current_indexed > last_indexed+1000){
				
				
				System.out.println("pmi update start!");
				
				
				ResultSet old = db.Query("select * from pmi_keyword"+ type +" where date=" + to);
				while(old.next()){
					int id = old.getInt("id");
					db.execute("delete from pmi_relate where pmi_id=" + id);
				}
				db.execute("delete from pmi_keyword"+type+" where date=" + to);
				db.Commit();
				
				int total = reader.numDocs();
				
				PreparedStatement st = db.getPreparedStatement("insert into pmi_keyword"+type+" (word,date,pmi) values (?,?,?)");
				
				
				System.out.println("pmi keyword update start! " + SimpleTime.getPrevTime(0));
				
				/*
				List<String> t = new ArrayList<String>();
				count = 0;
				for (String key : words) {
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + key);
					result = searcher.search(query, searcher.maxDoc());
					if(result.totalHits>10){
						t.add(key);
						count++;
					}
				}
				*/
				
				
				PMI.from = from;
				PMI.to = to;
				PMI.total = total;
				
				Vector<Keyword> ret = new Vector<>();
				
				int start=0;
				int core=8;
				int words_size = words.size();
				int chunk=words_size%core==0?words_size/core:words_size/core+1;
				
				Thread[] thread = new Thread[8];
				
				for(int i=0; i<core; ++i){
					thread[i] = new PMI(searcher, words.subList(start, start+chunk), ret);
					thread[i].start();
					
					start+=chunk;
					if((start+chunk)>words.size()){
						chunk = words.size()-start;
					}
				}
				
				for(int i=0; i<core; ++i){
					try {
						thread[i].join();
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}

				
				System.out.println("size of array " + ret.size());
				List<Keyword> today = new ArrayList<>(ret);
				Collections.sort(today);
				today = today.subList(0, today.size()<200?today.size():200);
				
				String[] arr = new String[today.size()];
				
				for (int i=0; i<today.size();++i) {
					Keyword key = today.get(i);
				
					st.setString(1, key.keyword);
					st.setBigDecimal(2, new BigDecimal(to));
					st.setDouble(3, key.pmi);
					st.executeUpdate();
					arr[i] = key.keyword;
				}
				
				
						
				System.out.println("pmi keyword updated! " + SimpleTime.getPrevTime(0));
				System.out.flush();
				db.Commit();
				
				/*
				//pmi 
				st = db.getPreparedStatement("insert into pmi_relate (pmi_id, word, pmi) values (?,?,?)");
				PreparedStatement st2 = db.getPreparedStatement("select * from pmi_keyword where date=? and word=?");
				for(int i=0; i<arr.length; ++i){
					
					st2.setBigDecimal(1, new BigDecimal(to));
					st2.setString(2, arr[i]);
					rs = st2.executeQuery();
					if(!rs.next())
						continue;
					int id = rs.getInt("id");
					
				
					for(int j=i+1; j<arr.length; ++j){
						//phrase search
						query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:\"" + arr[i] + " " + arr[j] + "\"~3");
						result = searcher.search(query, searcher.maxDoc());
						int x_y = result.totalHits;
						
						query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[i]);
						result = searcher.search(query, searcher.maxDoc());
						int x = result.totalHits;
						
						query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[j]);
						result = searcher.search(query, searcher.maxDoc());
						int y = result.totalHits;
						
						double pmi;
						if(x_y!=0 && (x*y)!=0 && (pmi=Math.log((double)((x_y*total/(x*y)))))>=4){


							st.setInt(1, id);
							st.setString(2, arr[j]);
							st.setDouble(3, pmi);
							st.executeUpdate();
							db.Commit();

							
							
							
						}
					}
				}
				*/
				
				System.out.println("pmi relate updated! " + SimpleTime.getPrevTime(0));
				
				db.execute("update pmi_index"+ type + " set indexed=" + current_indexed + " where date=" + to);
			}
		}
	}
	
	public void pmi_test(int date) throws IOException, ParseException, SQLException{
		
	Directory dir =FSDirectory.open(new File(indexPath));	
	IndexReader reader = IndexReader.open(dir);
	IndexSearcher searcher = new IndexSearcher(reader);
	TermEnum terms_enum =  reader.terms();
	Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
	QueryParser parser = new QueryParser(Version.LUCENE_36,"", analyzer);
	ResultSet rs;
	Query query;
	TopDocs result;
	
	String from = SimpleTime.getPrevDay((date+1));
	String to = SimpleTime.getPrevDay(date);
		
	System.out.println(from);
	
		int num= searcher.maxDoc();
		
		System.out.println("pmi update " + to + " num docs " + num + " " + SimpleTime.getPrevTime(0));

			

			
			int total = reader.numDocs();
			
			PreparedStatement st = db.getPreparedStatement("insert into pmi_keyword (word,date,pmi) values (?,?,?)");
			
			long terms =0;
			
			List<String> words = new LinkedList<>();
			
			while(terms_enum.next()){
				//System.out.println(terms_enum.term().text());
				//erase too low frequency words
				if(terms_enum.docFreq()>20){
					
					terms++;
					if(terms_enum.term().field().equals("segmented"))
					words.add(terms_enum.term().toString());

		
				}
				
			}
			
			System.out.println("pmi keyword updated! total keyword number " + terms);
			PMI.from = from;
			PMI.to = to;
			PMI.total = total;
			
			Vector<Keyword> ret = new Vector<>();
			
			int start=0;
			int core=8;
			int words_size = words.size();
			int chunk=words_size%core==0?words_size/core:words_size/core+1;
			
			Thread[] thread = new Thread[8];
			
			for(int i=0; i<core; ++i){
				thread[i] = new PMI(searcher, words.subList(start, start+chunk), ret);
				thread[i].start();
				
				start+=chunk;
				if((start+chunk)>words.size()){
					chunk = words.size()-start;
				}
			}
			
			for(int i=0; i<core; ++i){
				try {
					thread[i].join();
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}

			
			System.out.println("size of array " + ret.size());
			List<Keyword> today = new ArrayList<>(ret);
			Collections.sort(today);
			today = today.subList(0, today.size()<100?today.size():100);
			
			for (Keyword key : today) {
				System.out.println(key.keyword + " " + key.pmi);
			}
			System.out.println("pmi keyword updated! total keyword number " + terms + " " + SimpleTime.getPrevTime(0));
			System.out.flush();
			

			String[] arr = new String[today.size()];
			
			for(int i=0; i<today.size(); ++i){
				Keyword key = today.get(i);
				st.setString(1, key.keyword);
				st.setBigDecimal(2, new BigDecimal(to));
				st.setDouble(3, key.pmi);
				st.executeUpdate();
				arr[i] = key.keyword;
			}
					
			System.out.println("pmi keyword updated! total keyword number " + terms + " " + SimpleTime.getPrevTime(0));
			db.Commit();
			
			
			//pmi 
			st = db.getPreparedStatement("insert into pmi_relate (pmi_id, word, pmi) values (?,?,?)");
			PreparedStatement st2 = db.getPreparedStatement("select * from pmi_keyword where date=? and word=?");
			for(int i=0; i<arr.length; ++i){
				
				st2.setBigDecimal(1, new BigDecimal(to));
				st2.setString(2, arr[i]);
				rs = st2.executeQuery();
				if(!rs.next())
					continue;
				int id = rs.getInt("id");
				
			
				for(int j=i+1; j<arr.length; ++j){
					//phrase search
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:\"" + arr[i] + " " + arr[j] + "\"~3");
					result = searcher.search(query, searcher.maxDoc());
					int x_y = result.totalHits;
					
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[i]);
					result = searcher.search(query, searcher.maxDoc());
					int x = result.totalHits;
					
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[j]);
					result = searcher.search(query, searcher.maxDoc());
					int y = result.totalHits;
					
					double pmi;
					if(x_y!=0 && (x*y)!=0 && (pmi=Math.log((double)((x_y*total/(x*y)))))>=5){

						
						
						//rs = db.Query("select count(*) from pmi_relate where pmi_id=" + id + " and word='" + (String)arr[j] + "' and date=" + to + " limit 1");
						//rs.next()
						//if(!rs.next()){
						
						st.setInt(1, id);
						st.setString(2, arr[j]);
						st.setDouble(3, pmi);
						st.executeUpdate();
						db.Commit();
						//}else{
						//st = db.getPreparedStatement("update pmi_relate set pmi=? where pmi_id=" + id + " and word='" + (String)arr[j] + "' and date=" + to);
						//st.setDouble(1, pmi);
						//st.executeUpdate();
						//}
						
						
						
					}
				}
			}
			
			System.out.println("pmi relate updated! " + SimpleTime.getPrevTime(0));
			

	}
	

	
	
private void back_pmi(int date) throws IOException, ParseException, SQLException{
		
	Directory dir =FSDirectory.open(new File(indexPath));	
	IndexReader reader = IndexReader.open(dir);
	IndexSearcher searcher = new IndexSearcher(reader);
	TermEnum terms_enum =  reader.terms();
	Analyzer analyzer = new WhitespaceAnalyzer(Version.LUCENE_36);
	QueryParser parser = new QueryParser(Version.LUCENE_36,"", analyzer);

	Query query;
	TopDocs result;
			
	for(int p=0; p<date; ++p){
		String from = SimpleTime.getPrevDay((p+1));
		String to = SimpleTime.getPrevDay(p);
		

		ResultSet rs = db.Query("select * from pmi_index where date=" + to);
		if(!rs.next()){
			db.execute("insert into pmi_index (date,indexed) VALUES(" + to + ",0)");
			db.Commit();
			rs = db.Query("select * from pmi_index where date=" + to);
			rs.next();
		}
		
		
		int num= searcher.maxDoc();
		int last_indexed = rs.getInt("indexed");
		
		query = parser.parse("post_date:[" + from + " TO " + to + "]");
		result = searcher.search(query, searcher.maxDoc());
		int current_indexed = result.totalHits;
		

		//refresh if indexed doc changed 
		if(current_indexed > last_indexed+1000){
			List<Keyword> today = new ArrayList<>();
			
			System.out.println("pmi update " + to + " number of docs " + current_indexed + " " + SimpleTime.getPrevTime(0));
			
			db.execute("update pmi_index set indexed=" + current_indexed + " where date=" + to);
			
			ResultSet old = db.Query("select * from pmi_keyword where date=" + to);
			while(old.next()){
				int id = old.getInt("id");
				db.execute("delete from pmi_relate where pmi_id=" + id);
			}
			db.execute("delete from pmi_keyword where date=" + to);
			db.Commit();
			
			int total = reader.numDocs();
			
			PreparedStatement st = db.getPreparedStatement("insert into pmi_keyword (word,date,pmi) values (?,?,?)");
			
			long terms =0;
			
			while(terms_enum.next()){
				//System.out.println(terms_enum.term().text());
				//erase too low frequency words
				if(terms_enum.docFreq()>20){
					
					terms++;
					//System.out.println(terms_enum.term().text());
		
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
					//System.out.println((total / specify));
						//System.out.println("WW");
						
						today.add(new Keyword(terms_enum.term().text(), pmi));

						
						
						//rs = db.Query("select count(*) from pmi_keyword where word='" + word + "' and date=" + to + " limit 1");
						//rs.next();
						
						//if(rs.getInt(0)!=0){
						

						/*
						}else{
						PreparedStatement st =db.getPreparedStatement("update pmi_keyword set pmi=? where word=? and date=?");
						st.setDouble(1, pmi);
						st.setString(2, word);
						st.setBigDecimal(3, new BigDecimal(to));
						st.executeUpdate();
						}
						*/
					}
		
				}
				
			}
			
			
			Collections.sort(today);
			today = today.subList(0, today.size()<20?today.size():20);
			
			
			String[] arr = new String[today.size()];
			
			for(int i=0; i<today.size(); ++i){
				Keyword key = today.get(i);
				st.setString(1, key.keyword);
				st.setBigDecimal(2, new BigDecimal(to));
				st.setDouble(3, key.pmi);
				st.executeUpdate();
				arr[i] = key.keyword;
			}
					
			System.out.println("pmi keyword updated! total keyword number " + terms + " " + SimpleTime.getPrevTime(0));
			db.Commit();
			
			
			//pmi 
			st = db.getPreparedStatement("insert into pmi_relate (pmi_id, word, pmi) values (?,?,?)");
			PreparedStatement st2 = db.getPreparedStatement("select * from pmi_keyword where date=? and word=?");
			for(int i=0; i<arr.length; ++i){
				
				st2.setBigDecimal(1, new BigDecimal(to));
				st2.setString(2, arr[i]);
				rs = st2.executeQuery();
				if(!rs.next())
					continue;
				int id = rs.getInt("id");
				
			
				for(int j=i+1; j<arr.length; ++j){
					//phrase search
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:\"" + arr[i] + " " + arr[j] + "\"~3");
					result = searcher.search(query, searcher.maxDoc());
					int x_y = result.totalHits;
					
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[i]);
					result = searcher.search(query, searcher.maxDoc());
					int x = result.totalHits;
					
					query = parser.parse("post_date:[" + from + " TO " + to + "] AND segmented:" + arr[j]);
					result = searcher.search(query, searcher.maxDoc());
					int y = result.totalHits;
					
					double pmi;
					if(x_y!=0 && (x*y)!=0 && (pmi=Math.log((double)((x_y*total/(x*y)))))>=5){

						
						
						//rs = db.Query("select count(*) from pmi_relate where pmi_id=" + id + " and word='" + (String)arr[j] + "' and date=" + to + " limit 1");
						//rs.next()
						//if(!rs.next()){
						
						st.setInt(1, id);
						st.setString(2, arr[j]);
						st.setDouble(3, pmi);
						st.executeUpdate();
						db.Commit();
						//}else{
						//st = db.getPreparedStatement("update pmi_relate set pmi=? where pmi_id=" + id + " and word='" + (String)arr[j] + "' and date=" + to);
						//st.setDouble(1, pmi);
						//st.executeUpdate();
						//}
						
						
						
					}
				}
			}
			
			
			System.out.println("pmi relate updated! " + SimpleTime.getPrevTime(0));
			
		}
	}
	searcher.close();
	}
		

}
