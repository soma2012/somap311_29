<?php
date_default_timezone_set("Asia/Seoul");

$conn = mysql_connect('twit.tprpc.com','twit','1rmdwjd') or die('test');
mysql_query('SET NAMES utf8;');
mysql_select_db('twit_manager',$conn);

$ret = array();

// 데이터 정리부터!!!!! 

$result = mysql_query('SELECT * FROM `tweet_data_statcnt` WHERE `day` > DATE_ADD(now(), interval -20 day) ORDER BY `day` ASC',$conn);
$calc_data = array();
while($row = mysql_fetch_assoc($result)) {
	$clock = sprintf("%s %02d:00:00",$row['day'],(int)$row['hour']);

	//$calc_data[$row['day'].' '.$row['hour'].':00:00'] = (int)$row['cnt'];
	$calc_data[$clock] = (int)$row['cnt'];
}

$nowh = date("G");

$ret = array();
$ret['hour'] = $nowh;

//echo $nowh;

for($i=0;$i<20;$i++) {
	$today = date("Y-m-d", strtotime('-'.$i.' day'));
	// 세팅 되어 있으면 그만 해도 됨 

	// 그날의 트윗 총 갯수 계산
	for($h=23;$h>=0;$h--) {

		$clock = sprintf("%s %02d:00:00",$today,$h);

		if(isset($calc_data[$clock])) break;
		
		// 오늘 지금 이시간 이후는 만들지 않아요
		if($i == 0 && $nowh <= $h) continue;
		
		$q = "SELECT count(*) FROM `tweet_data` WHERE hour(`update_time`) = '$h' AND date(`update_time`) = '$today'";
		$result = mysql_query($q);
		$row = mysql_fetch_row($result);
		$cnt = (int)$row[0];
		//echo $cnt;	

		$calc_data[$clock] = $cnt;
	

		if($i == 0 && $nowh <= $h) continue;
		$q = "INSERT INTO `tweet_data_statcnt` (`day`,`hour`,`cnt`) values ('$today','$h','$cnt')";
		//echo $q;
		$result = mysql_query($q);
	}
}


ksort($calc_data);
$ret['hour_data'] = $calc_data;
$cnt = 0;
foreach($calc_data as $k => $v) {
	$calc_data[$k] = $cnt + $v;
	$cnt += $v;
}
$ret['total_data'] = $calc_data;


//$str = json_encode($ret);

// 배열로 나오게 하기
$nret = array();
$hour_data = array();
foreach($ret['hour_data'] as $k => $v) {
	$now = array($k,$v);
	$hour_data[] = $now;
}

$total_data = array();
foreach($ret['total_data'] as $k => $v) {
	$now = array($k,$v);
	$total_data[] = $now;
}

$nret['hour_data'] = $hour_data;
$nret['total_data'] = $total_data;


echo json_encode($nret);


//$str = str_replace('{','[',$str);
//$str = str_replace('}',']',$str);

//echo $str;
