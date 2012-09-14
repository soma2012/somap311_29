package test;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class SimpleTime {
	

	public static String getPrevTime(int hour){
		SimpleDateFormat formatter = new SimpleDateFormat ( "yyyyMMddHHmmss", Locale.KOREA );
		Date currentTime = new Date ( );
		Calendar cal = Calendar.getInstance();
		cal.setTime(currentTime);
		cal.add(Calendar.HOUR, -hour);
		currentTime = cal.getTime();
		return formatter.format ( currentTime );	
	}
	
	public static String getPrevDay(int day){
		SimpleDateFormat formatter = new SimpleDateFormat ( "yyyyMMddHHmmss", Locale.KOREA );
		Date currentTime = new Date ( );
		
		currentTime.setHours(0);
		currentTime.setMinutes(0);
		currentTime.setSeconds(0);		
		Calendar cal = Calendar.getInstance();
		cal.setTime(currentTime);

		cal.add(Calendar.DAY_OF_MONTH, -day);
		currentTime = cal.getTime();
		return formatter.format ( currentTime );	
	}
}
