SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `drawrawr`
--

-- --------------------------------------------------------

--
-- Table structure for table `journals`
--

CREATE TABLE IF NOT EXISTS `journals` (
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
  `username` char(50) DEFAULT NULL,
  `hash` char(125) DEFAULT NULL,
  `email` varchar(200) NOT NULL,
  `lastLogin` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=39 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
