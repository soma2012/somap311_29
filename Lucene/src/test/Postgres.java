package test;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class Postgres {
	
	private Connection con = null;

	
	public ResultSet Query(String sql){
		Statement st;
		try {
			st = con.createStatement();
		
			st.setFetchSize(1000);
			return st.executeQuery(sql);
			
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
	}
	
	public void execute(String sql){
		Statement st;
		try {
			st = con.createStatement();
		
			st.setFetchSize(1000);
			st.executeUpdate(sql);
			
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public PreparedStatement getPreparedStatement(String sql){
		try {
			PreparedStatement pstmt=  con.prepareStatement(sql);
			pstmt.setFetchSize(1000);
			return pstmt;
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
		
	}
	
	public void Commit(){
		try {
			con.commit();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	Postgres(){
    
        String url = "jdbc:postgresql://61.43.139.70";
        String user = "postgres";
        String password = "postgres";
        try {
            con = DriverManager.getConnection(url, user, password);
            con.setAutoCommit(false);

        } catch (SQLException e) {
        		e.printStackTrace();

        }
	}
	
}
