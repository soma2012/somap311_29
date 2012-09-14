package org.soma.tweetsemantic;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import com.mysql.jdbc.PreparedStatement;


public class DB {
	private int until = 2000000;
	private Connection conn;
	private Statement stmt;

	public DB() throws Exception
	{
		// TODO
		Class.forName("com.mysql.jdbc.Driver").newInstance();
		conn = DriverManager.getConnection("jdbc:mysql://twit.tprpc.com/twit_manager?useUnicode=true&characterEncoding=UTF-8" ,"twit" ,"1rmdwjd");
		stmt = conn.createStatement();
	}
	private void getTweetDate(String tweetUid) {
		
	}
	public void getData(int limit, int size) throws Exception
	{
		while(limit < until) {
			System.out.println("read db");

			ResultSet rs = stmt.executeQuery(String.format("SELECT * FROM `tweet_data` WHERE `no` > %d ORDER BY `no` ASC LIMIT %d",limit,size));

			System.out.println("read db done");
			
			while(rs.next())
			{
				String no = rs.getString("no");
				String tweet = rs.getString("tweet");


			}
		}

	}

}
