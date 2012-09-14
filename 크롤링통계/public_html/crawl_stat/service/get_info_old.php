<?php
date_default_timezone_set("Asia/Seoul");

$conn = mysql_connect('twit.tprpc.com','twit','1rmdwjd') or die('test');
mysql_query('SET NAMES utf8;');
mysql_select_db('twit_manager',$conn);

$ret = array();

// 데이터 정리부터!!!!! 

$result = mysql_query('SELECT count(*) FROM `tweet_data`',$conn);
$row = mysql_fetch_row($result);
$total_tweets = $row[0];
$ret['total_tweets'] = $total_tweets;


$result = mysql_query('SELECT count(*) FROM `tweet_data` WHERE `update_time` > DATE_ADD(now(), INTERVAL - 1 hour)',$conn);
$row = mysql_fetch_row($result);
$ret['latest_1hour_tweets'] = $row[0];


$day_crawl = array();
$incremental_crawl = array();
$now_tweet = (int) $total_tweets;
for($i=0;$i<30;$i++) {

	$today = date("Y-m-d", strtotime('-'.$i.' day'));
	
	$q = "SELECT count(*) FROM `tweet_data` WHERE date(`update_time`) = '$today'";
	$result = mysql_query($q);
	//echo $q;
	$row = mysql_fetch_row($result);
	$day_tweet = (int)$row[0];

	$day_crawl[$today] = $day_tweet;
	$incremental_crawl[$today] = $now_tweet;

	$now_tweet -= $day_tweet;

}
$ret['day_crawl'] = $day_crawl;
$ret['inc_crawl'] = $incremental_crawl;
echo json_encode($ret);
