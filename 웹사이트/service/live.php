<?
$conn = mysql_pconnect('twit.tprpc.com','twit','1rmdwjd') or die('test');
mysql_query('SET NAMES utf8;');
mysql_select_db('twit_manager',$conn);

$q = "SELECT count(*) FROM `tweet_data` WHERE `update_time` >= DATE_ADD(NOW(), interval -1 second)";
$result = mysql_query($q, $conn);
$row = mysql_fetch_row($result);
$ret['cnt'] = $row[0];

$q = "SELECT * FROM `tweet_data` ORDER BY `no` DESC LIMIT 1";
$result = mysql_query($q, $conn);
$row = mysql_fetch_assoc($result);
$ret['total_cnt'] = $row['no'];

echo json_encode($ret);

?>
