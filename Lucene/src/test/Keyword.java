package test;

public class Keyword implements Comparable<Keyword> {
	String keyword;
	Double pmi;
	
	public Keyword(String keyword, Double pmi){
		this.keyword = keyword;
		this.pmi = pmi;
	}
	
	@Override
	public int compareTo(Keyword o) {
		// TODO Auto-generated method stub

		return o.pmi.compareTo(this.pmi);
		
	}


	
}
