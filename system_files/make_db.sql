-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema wedding
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `wedding` DEFAULT CHARACTER SET utf8mb4 ;
USE `wedding` ;

-- -----------------------------------------------------
-- Table `wedding`.`Configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `wedding`.`Configuration` ;

CREATE TABLE IF NOT EXISTS `wedding`.`Configuration` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Key` VARCHAR(45) NULL DEFAULT NULL,
  `Value` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `wedding`.`Bundle`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `wedding`.`Bundle` ;

CREATE TABLE IF NOT EXISTS `wedding`.`Bundle` (
  `bundle_id` INT(11) NOT NULL AUTO_INCREMENT,
  `bundle_name` VARCHAR(45) NOT NULL,
  `bundle_unique_id` INT(11) NULL DEFAULT NULL,
  `bundle_invited_day` TINYINT(4) NOT NULL DEFAULT 1,
  `bundle_invited_evening` TINYINT(4) NOT NULL DEFAULT 1,
  `bundle_rsvp_day` TINYINT(4) NULL DEFAULT NULL,
  `bundle_rsvp_evening` TINYINT(4) NULL DEFAULT NULL,
  PRIMARY KEY (`bundle_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 30
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `wedding`.`People`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `wedding`.`People` ;

CREATE TABLE IF NOT EXISTS `wedding`.`People` (
  `person_id` INT(11) NOT NULL AUTO_INCREMENT,
  `person_first` VARCHAR(45) NOT NULL,
  `person_last` VARCHAR(45) NOT NULL,
  `person_under18` INT(11) NULL DEFAULT 0,
  `person_requirements` VARCHAR(500) NULL DEFAULT NULL,
  `bundle_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`person_id`),
  INDEX `Bundle_People_FK` (`bundle_id` ASC) VISIBLE,
  CONSTRAINT `Bundle_People_FK`
    FOREIGN KEY (`bundle_id`)
    REFERENCES `wedding`.`Bundle` (`bundle_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 79
DEFAULT CHARACTER SET = utf8mb4;

USE `wedding` ;

-- -----------------------------------------------------
-- function random_code
-- -----------------------------------------------------
USE `wedding`;
DROP function IF EXISTS `wedding`.`random_code`;

DELIMITER $$
USE `wedding`$$
CREATE DEFINER=`wedding_plan`@`%` FUNCTION `random_code`() RETURNS int(11)
BEGIN
RETURN FLOOR(RAND() * (999999 - 100000 + 1)) + 100000;
END$$

DELIMITER ;
USE `wedding`;

DELIMITER $$

USE `wedding`$$
DROP TRIGGER IF EXISTS `wedding`.`Bundle_BEFORE_INSERT` $$
USE `wedding`$$
CREATE
DEFINER=`wedding_plan`@`%`
TRIGGER `wedding`.`Bundle_BEFORE_INSERT`
BEFORE INSERT ON `wedding`.`Bundle`
FOR EACH ROW
BEGIN
    SET NEW.bundle_unique_id = random_code();
END$$
DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
