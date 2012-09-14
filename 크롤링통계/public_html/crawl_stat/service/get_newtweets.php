<?php

$conn = mysql_connect('twit.tprpc.com','twit','1rmdwjd') or die('test');
mysql_query('SET NAMES utf8;');
mysql_select_db('twit_manager',$conn);

$ret = array();


$result = mysql_query('SELECT * FROM `tweet_data` ORDER BY `update_time` DESC LIMIT 0,50',$conn);
//$result = mysql_query('SELECT * FROM `tweet_data` WHERE `update_time` > DATE_ADD(now(), INTERVAL - 10 second) ORDER BY `update_time` DESC LIMIT 0,50',$conn);

while($row = mysql_fetch_assoc($result))
{
	array_push($ret, $row);
}

echo json_encode($ret);

