-- AlterTable
ALTER TABLE `Character` MODIFY `class` ENUM('HUNTER', 'WARLOCK', 'TITAN') NOT NULL DEFAULT 'HUNTER';

-- CreateTable
CREATE TABLE `Activity` (
    `activity_id` INTEGER NOT NULL AUTO_INCREMENT,
    `bng_activity_id` BIGINT NOT NULL,
    `activity_name` VARCHAR(75) NOT NULL,
    `max_fireteam_size` INTEGER NOT NULL DEFAULT 0,
    `type` VARCHAR(100) NOT NULL DEFAULT 'Activity_Type',
    `modifiers` VARCHAR(500) NOT NULL,

    UNIQUE INDEX `Activity_bng_activity_id_key`(`bng_activity_id`),
    PRIMARY KEY (`activity_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Activity_Stats` (
    `character_id` INTEGER NOT NULL,
    `activity_id` INTEGER NOT NULL,
    `instance_id` BIGINT NOT NULL,
    `activity_name` VARCHAR(255) NOT NULL,
    `weapon_id` INTEGER NOT NULL,
    `weapon_name` VARCHAR(255) NOT NULL,
    `kills` INTEGER UNSIGNED NOT NULL DEFAULT 0,
    `precision_kills` INTEGER UNSIGNED NOT NULL DEFAULT 0,
    `precision_kills_percent` DECIMAL(5, 2) NOT NULL DEFAULT 0.0,
    `character_class` ENUM('HUNTER', 'WARLOCK', 'TITAN') NOT NULL,

    PRIMARY KEY (`weapon_id`, `character_id`, `instance_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Activity_Stats` ADD CONSTRAINT `Activity_Stats_activity_id_fkey` FOREIGN KEY (`activity_id`) REFERENCES `Activity`(`activity_id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Activity_Stats` ADD CONSTRAINT `Activity_Stats_weapon_id_fkey` FOREIGN KEY (`weapon_id`) REFERENCES `Weapon`(`weapon_id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Activity_Stats` ADD CONSTRAINT `Activity_Stats_character_id_fkey` FOREIGN KEY (`character_id`) REFERENCES `Character`(`character_id`) ON DELETE RESTRICT ON UPDATE CASCADE;
