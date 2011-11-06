SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `drawrawr`
--

-- --------------------------------------------------------

--
-- Table structure for table `journals-rp`
--

CREATE TABLE IF NOT EXISTS `journals-rp` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `slug` varchar(75) NOT NULL COMMENT 'URL accessor',
  `owner` int(11) unsigned NOT NULL COMMENT 'UserID reference',
  `published` tinyint(1) NOT NULL DEFAULT '1',
  `title` varchar(50) DEFAULT NULL,
  `timestamp.created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `timestamp.edited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT 'Timestamp of last edit',
  `content.source` text NOT NULL COMMENT 'Source BBCode',
  `content` text NOT NULL COMMENT 'Compiled BBCode -> HTML',
  `attachments.files` text COMMENT 'JSON list of attached files',
  `attachments.modules` text COMMENT 'JSON list of attached modules',
  `attachments.modules.data` text COMMENT 'JSON data',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `owner` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `journals-users`
--

CREATE TABLE IF NOT EXISTS `journals-users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `slug` varchar(75) NOT NULL COMMENT 'URL accessor',
  `owner` int(11) unsigned NOT NULL COMMENT 'UserID reference',
  `published` tinyint(1) NOT NULL DEFAULT '1',
  `title` varchar(50) DEFAULT NULL,
  `timestamp.created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `timestamp.edited` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT 'Timestamp of last edit',
  `content.source` text NOT NULL COMMENT 'Source BBCode',
  `content` text NOT NULL COMMENT 'Compiled BBCode -> HTML',
  `attachments.files` text COMMENT 'JSON list of attached files',
  `attachments.modules` text COMMENT 'JSON list of attached modules',
  `attachments.modules.data` text COMMENT 'JSON data',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `owner` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` binary(64) NOT NULL,
  `email` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `timestamp.join` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=40 ;

-- --------------------------------------------------------

--
-- Table structure for table `users-rp`
--

CREATE TABLE IF NOT EXISTS `users-rp` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `creator` int(10) unsigned NOT NULL,
  `username` varchar(50) NOT NULL,
  `realname` varchar(50) NOT NULL,
  `email` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `timestamp.created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

