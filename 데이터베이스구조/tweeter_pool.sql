-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Sep 14, 2012 at 05:57 PM
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
-- Table structure for table `tweeter_pool`
--

CREATE TABLE IF NOT EXISTS `tweeter_pool` (
  `twit_id` char(50) NOT NULL COMMENT '트위터아이디',
  `latest_time` bigint(20) NOT NULL DEFAULT '0' COMMENT '최신트윗 시각',
  `crawl_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '크롤링한 시각',
  `ncrawl_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `stat_korean` double NOT NULL DEFAULT '0' COMMENT '한글사용량 통계',
  `weight` float NOT NULL DEFAULT '0' COMMENT '가중치',
  `latest_worker` char(20) NOT NULL DEFAULT '' COMMENT '최근 워커',
  `using` tinyint(1) NOT NULL DEFAULT '0' COMMENT '사용중인지여부',
  PRIMARY KEY (`twit_id`),
  KEY `weight` (`weight`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
