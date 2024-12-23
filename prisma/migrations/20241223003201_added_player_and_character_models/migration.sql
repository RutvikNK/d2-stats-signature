-- CreateTable
CREATE TABLE `Player` (
    `player_id` INTEGER NOT NULL AUTO_INCREMENT,
    `destiny_id` BIGINT UNSIGNED NOT NULL,
    `bng_id` BIGINT UNSIGNED NOT NULL,
    `bng_username` VARCHAR(255) NOT NULL,
    `date_created` DATETIME(3) NOT NULL DEFAULT '1991-05-07T00:00:00+00:00',
    `date_last_played` DATETIME(3) NULL DEFAULT '1991-05-07T00:00:00+00:00',
    `platform` ENUM('XBOX', 'PSN', 'STEAM', 'BLIZZARD') NOT NULL,
    `character_ids` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `Player_destiny_id_key`(`destiny_id`),
    UNIQUE INDEX `Player_bng_id_key`(`bng_id`),
    UNIQUE INDEX `Player_character_ids_key`(`character_ids`),
    PRIMARY KEY (`player_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Character` (
    `character_id` INTEGER NOT NULL AUTO_INCREMENT,
    `bng_character_id` BIGINT UNSIGNED NOT NULL,
    `class` ENUM('HUNTER', 'TITAN', 'WARLOCK') NOT NULL DEFAULT 'HUNTER',
    `player_id` INTEGER NOT NULL,
    `date_last_played` DATETIME(3) NULL DEFAULT CURRENT_TIMESTAMP(3),

    UNIQUE INDEX `Character_bng_character_id_key`(`bng_character_id`),
    PRIMARY KEY (`character_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Character` ADD CONSTRAINT `Character_player_id_fkey` FOREIGN KEY (`player_id`) REFERENCES `Player`(`player_id`) ON DELETE RESTRICT ON UPDATE CASCADE;
