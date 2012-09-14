-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Sep 14, 2012 at 05:53 PM
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
-- Table structure for table `twitter_user_status`
--

CREATE TABLE IF NOT EXISTS `twitter_user_status` (
  `no` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '고유값',
  `twitid` char(50) NOT NULL COMMENT '사용자아이디',
  `fullname` char(50) NOT NULL COMMENT '이름',
  `location` varchar(400) NOT NULL COMMENT '위치',
  `bio` varchar(2048) NOT NULL COMMENT '자기소개',
  `url` varchar(2048) NOT NULL COMMENT '웹주소',
  `twitcnt` int(10) unsigned NOT NULL COMMENT '트윗수',
  `cnt` int(10) unsigned NOT NULL COMMENT '이번에 긁은 숫자',
  `following` int(10) unsigned NOT NULL COMMENT '팔로잉수',
  `followers` int(10) unsigned NOT NULL COMMENT '팔로워수',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '갱신시각',
  PRIMARY KEY (`no`),
  KEY `twitid` (`twitid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT='사용자 정보를 저장해주는 테이블(증가식)' AUTO_INCREMENT=491166 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
