-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Sep 14, 2012 at 05:50 PM
-- Server version: 5.5.24
-- PHP Version: 5.3.10-1ubuntu3.2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `twit_manager`
--

-- --------------------------------------------------------

--
-- Table structure for table `tweet_data`
--

CREATE TABLE IF NOT EXISTS `tweet_data` (
  `no` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `twitid` char(50) NOT NULL,
  `username` char(50) NOT NULL COMMENT '트위터 아이디',
  `timestamp` bigint(20) NOT NULL COMMENT '트윗한시각',
  `tweet` varchar(2048) NOT NULL COMMENT '트윗내용',
  `tweet_analysis` mediumtext,
  `worker` char(40) NOT NULL COMMENT '긁어온아이',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '긁어온시간',
  PRIMARY KEY (`no`),
  KEY `twitid` (`twitid`),
  KEY `username` (`username`),
  KEY `timestamp` (`timestamp`),
  KEY `update_time` (`update_time`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=33464937 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
