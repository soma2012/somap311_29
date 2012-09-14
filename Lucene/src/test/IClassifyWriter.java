package test;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.math.BigDecimal;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.Field.Index;
import org.apache.lucene.document.Field.Store;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexWriter;

public class IClassifyWriter extends IWriterBase{

	public IClassifyWriter(){
		indexPath="/home/xorox90/subject/";
	}
	
	public void update() throws IOException{
		this.open();
		this.indexing();
	}
	
	private void indexing() throws IOException{
		String home = "/home/xorox90/topic/train/";
		
		File dir = new File(home);
		File[] dirs = dir.listFiles();
		for(File temp : dirs){
			if(temp.isDirectory()){
				String txt = temp.getAbsolutePath()+"/"+temp.getName() + ".txt";
				BufferedReader in = new BufferedReader(new FileReader(txt));

				
				
				String subject=temp.getName();
				StringBuilder str = new StringBuilder();
				char buf[] = new char[(int)new File(txt).length()];
				
				in.read(buf);
				str.append(buf);
				String t = str.toString();
				
				System.out.println(subject);
				
				int i=0;
				for (String s : t.split("\n")) {
					s = s.replaceAll("[^0-9 가-힣ㄱ-ㅎㅏ-ㅣ]+", "");
					Document doc = new Document();
					Field field = new Field("content", s, Store.YES,Index.ANALYZED);
					doc.add(field);
					field = new Field("subject", subject, Store.YES,Index.NOT_ANALYZED);
					doc.add(field);
					
					writer.addDocument(doc);
					i++;
					if(i==1000)
						break;
				}
				
				System.out.println(subject + "end");
				
				//temp.getName()
			}
			writer.commit();
		}
		
	}

	
}
