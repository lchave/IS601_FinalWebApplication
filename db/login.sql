CREATE DATABASE loginData;
use loginData;

CREATE TABLE IF NOT EXISTS tblLoginImport (

select * from logininfo;
INSERT INTO `login`.`logininfo`(`id`,`name`,`email`,`password`) VALUES(1,"waseem","waseem@xyz.com","12345");
INSERT INTO `login`.`logininfo`(`id`,`name`,`email`,`password`) VALUES(2,"omkar","omkar@xyz.com","12345");
INSERT INTO `login`.`logininfo`(`id`,`name`,`email`,`password`) VALUES(3,"vishal","vishal@xyz.com","12345");
INSERT INTO `login`.`logininfo`(`id`,`name`,`email`,`password`) VALUES(4,"arvind","arvind@xyz.com","12345");


select * from logininfo