-- -----------------------------------------------------
-- Sets up and adds people who are invited to the whole day
-- Presumes that make_db has already been ran
-- -----------------------------------------------------
SET @invited_day = 1;
SET @invited_evening = 1;

-- -----------------------------------------------------
-- Copy this section for each group of people who should be invited to the whole evening
-- -----------------------------------------------------
SET @bundle_name = 'Test Evening';
INSERT INTO `wedding`.`Bundle` (`bundle_name`, `bundle_invited_day`, `bundle_invited_evening`) VALUES (@bundle_name, @invited_day, @invited_evening);
INSERT INTO People (person_first, person_last, bundle_id)  VALUES
    ('Test', 'Alan', (SELECT bundle_id FROM Bundle WHERE bundle_name = @bundle_name)),
     ('Test', 'Annette', (SELECT bundle_id FROM Bundle WHERE bundle_name = @bundle_name));