<?
$conn = mysql_pconnect('twit.tprpc.com','twit','1rmdwjd') or die('test');
mysql_query('SET NAMES utf8;');
mysql_select_db('twit_manager',$conn);

$q = "SELECT * FROM `tweet_data` ORDER BY `no` DESC LIMIT 20";
$ret = array();
$result = mysql_query($q, $conn);
while($row = mysql_fetch_assoc($result)){
	$q = 'SELECT DATE_ADD(`tweet_time`,INTERVAL +9 HOUR) FROM `tweet_timedata` WHERE `timestamp` <= \''.$row[timestamp].'\' ORDER BY `timestamp` DESC LIMIT 1';	

	$res = mysql_query($q, $conn);
	$data = mysql_fetch_row($res);
	$row['tweet_time'] = $data[0];
	//$row['tweet_time'] = substr($data['tweet_time'],0,10);

	$ret[] = $row;
}

echo json_encode($ret);

?>
