<?php

if(isset($_GET['mode'])) $mode = $_GET['mode'];
else $mode = '';

$rss = file_get_contents("http://openapi.naver.com/search?key=1d258a782bd287820c7ef72991972be1&query=nexearch&target=rank");

$naverRes = new SimpleXMLElement($rss);
//echo $rss;
$tags = "";
$sets = array();

for($i=0;$i<sizeof($naverRes->item); $i++)
{
	for($j=1;$j<=10;$j++) 
	{
		$k = $naverRes->item[$i]->{"R{$j}"}->K;
		$k_url = urlencode($k);
		if(in_array($k,$sets)) continue;
		array_push($sets,$k);

		$tags .= " <a href='http://search.naver.com/search.naver?query=$k_url' style='11'  color='0x3258B8'  hicolor='0xF2B512'  > $k </a> ";
	}
}

// 주제별

$query = array('movie','people','foreignactor','perform','drama','broadcast','book');
$color = array('movie' => '228b22',
				'people' => '8b4513',
				'foreignactor' => 'ff1493',
				'perform' => '191970',
				'drama' => '808000',
				'broadcast' => '2f4f4f',
				'book' => '4b0082');

foreach($query as $q) 
{
	$rss = file_get_contents("http://openapi.naver.com/search?key=1d258a782bd287820c7ef72991972be1&query=$q&target=ranktheme");
	
//echo($rss);

	$naver[$q] = new SimpleXMLElement($rss);
	for($i=0;$i<sizeof($naver[$q]->item); $i++)
	{
		for($j=1;$j<=10;$j++) 
		{
			$k = $naver[$q]->item[$i]->{"R{$j}"}->K;
			$k_url = urlencode($k);

			if(in_array($k,$sets)) continue;
			array_push($sets,$k);


			if($mode=='color')
			{

				$tags .= " <a href='http://search.naver.com/search.naver?query=$k_url' style='11'  color='0x$color[$q]'  hicolor='0xF2B512'  > $k </a> ";
			}
			else 
			{
				$tags .= " <a href='http://search.naver.com/search.naver?query=$k_url' style='11'  color='0x3258B8'  hicolor='0xF2B512'  > $k </a> ";
			}

		}
	}

}

?>
<!DOCTYPE>
<html>
<head>
<title>issue cloud by tprpc</title>
<script type="text/javascript" src="./swfobject.js"></script>
</head>
<body>
	<div id="issuecloud">Loading...</div>
</body>
<script type="text/javascript">
		var so = new SWFObject("./tagcloud.swf", "tagcloud", "800", "600", "7", "#ffffff");
		// uncomment next line to enable transparency
		//so.addParam("wmode", "transparent");
		so.addVariable("tcolor", "0x3258B8");
		so.addVariable("mode", "tags");
		so.addVariable("distr", "true");
		so.addVariable("tspeed", "100");
		so.addVariable("tagcloud", "<tags><?=$tags?></tags>");

		so.write("issuecloud");
</script>
</html>
