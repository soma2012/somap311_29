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
-- Table structure for table `tweet_data_statdailycnt`
--

CREATE TABLE IF NOT EXISTS `tweet_data_statdailycnt` (
  `day` date NOT NULL,
  `cnt` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tweet_data_statdailycnt`
--

INSERT INTO `tweet_data_statdailycnt` (`day`, `cnt`) VALUES
('2012-08-18', 83390),
('2012-08-17', 1037256),
('2012-08-16', 1809629),
('2012-08-15', 1083835),
('2012-08-14', 1434859),
('2012-08-13', 2330117),
('2012-08-12', 2685147),
('2012-08-11', 65379);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
