-- CreateTable
CREATE TABLE `Equipped_Weapons` (
    `weapon_id` INTEGER NOT NULL,
    `character_id` INTEGER NOT NULL,
    `slot_type` ENUM('KINETIC', 'ENERGY', 'POWER') NOT NULL,
    `main_stat` VARCHAR(20) NOT NULL DEFAULT '0',

    PRIMARY KEY (`character_id`, `weapon_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Equipped_Armor` (
    `armor_id` INTEGER NOT NULL,
    `character_id` INTEGER NOT NULL,
    `slot_type` ENUM('HELMET', 'GAUNTLETS', 'CHEST', 'BOOTS', 'CLASS_ITEM') NOT NULL,

    PRIMARY KEY (`character_id`, `armor_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Equipped_Weapons` ADD CONSTRAINT `Equipped_Weapons_weapon_id_fkey` FOREIGN KEY (`weapon_id`) REFERENCES `Weapon`(`weapon_id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Equipped_Weapons` ADD CONSTRAINT `Equipped_Weapons_character_id_fkey` FOREIGN KEY (`character_id`) REFERENCES `Character`(`character_id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Equipped_Armor` ADD CONSTRAINT `Equipped_Armor_armor_id_fkey` FOREIGN KEY (`armor_id`) REFERENCES `Armor`(`armor_id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Equipped_Armor` ADD CONSTRAINT `Equipped_Armor_character_id_fkey` FOREIGN KEY (`character_id`) REFERENCES `Character`(`character_id`) ON DELETE RESTRICT ON UPDATE CASCADE;
