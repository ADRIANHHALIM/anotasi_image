-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping data for table reviewer_db.reviewer_anotasi: ~31 rows (approximately)
INSERT INTO `reviewer_anotasi` (`id_anotasi`, `koordinat_x`, `koordinat_y`, `lebar`, `tinggi`, `id_gambar`, `id_segmentasi`) VALUES
	(1, 624, 460, 207, 167, 1, 1),
	(2, 470, 479, 56, 43, 1, 1),
	(3, 342, 473, 50, 99, 1, 2),
	(4, 131, 481, 28, 59, 1, 2),
	(5, 20, 488, 34, 65, 1, 2),
	(6, 464, 168, 243, 260, 1, 3),
	(7, 726, 11, 382, 346, 1, 3),
	(8, 59, 19, 392, 378, 1, 3),
	(9, 19, 495, 1116, 196, 1, 4),
	(10, 368, 242, 86, 92, 5, 5),
	(11, 425, 185, 56, 55, 5, 5),
	(12, 388, 141, 34, 31, 5, 5),
	(13, 339, 144, 28, 25, 5, 5),
	(14, 229, 116, 22, 19, 5, 5),
	(15, 493, 227, 31, 58, 5, 6),
	(16, 185, 282, 37, 76, 5, 6),
	(17, 73, 328, 38, 81, 5, 6),
	(18, 104, 298, 36, 74, 5, 6),
	(19, 21, 294, 36, 81, 5, 6),
	(20, 97, 240, 28, 56, 5, 6),
	(21, 162, 217, 27, 45, 5, 6),
	(22, 257, 204, 26, 41, 5, 6),
	(23, 230, 177, 20, 29, 5, 6),
	(24, 24, 122, 375, 500, 4, 7),
	(25, 323, 44, 276, 578, 4, 7),
	(26, 550, 105, 280, 516, 4, 7),
	(27, 220, 101, 176, 166, 8, 8),
	(28, 400, 60, 129, 134, 8, 8),
	(29, 106, 171, 92, 88, 8, 8),
	(30, 0, 181, 74, 138, 8, 8),
	(31, 51, 128, 74, 71, 8, 8);

-- Dumping data for table reviewer_db.reviewer_gambar: ~8 rows (approximately)
INSERT INTO `reviewer_gambar` (`id_gambar`, `id_pengguna`, `id_direktori`, `id_dataset`, `nama_file`, `ukuran_file`, `tanggal_dibuat`, `format_file`, `tanggal_pengambilan`, `model_kamera`, `lebar`, `tinggi`, `lokasi_pengambilan`, `id_pembuat`, `tanggal_buat`) VALUES
	(1, 1, 10, 100, '1.jpg', 972, '2025-06-05', 'jpg', '2024-06-01', 1234, 1155, 710, 5678, 3, '2025-06-10 13:45:56.000000'),
	(2, 1, 10, 100, '2.jpeg', 136, '2025-06-05', 'jpeg', '2024-06-01', 1234, 1600, 1143, 5678, 3, '2025-06-10 13:45:56.000000'),
	(3, 2, 10, 100, '3.jpg', 364, '2025-06-05', 'jpg', '2024-06-01', 1234, 1167, 571, 5678, 3, '2025-06-10 13:45:56.000000'),
	(4, 2, 10, 100, '4.jpg', 89, '2025-06-05', 'jpg', '2024-06-01', 1234, 830, 622, 5678, 3, '2025-06-10 13:45:56.000000'),
	(5, 1, 10, 100, '5.jpg', 72, '2025-06-06', 'jpg', '2024-06-01', 1234, 640, 427, 5678, 3, '2025-06-12 12:08:48.000000'),
	(6, 1, 10, 100, '6.jpg', 192, '2025-06-06', 'jpg', '2024-06-01', 1234, 1263, 831, 5678, 3, '2025-06-12 12:08:48.000000'),
	(7, 2, 10, 100, '7.jpg', 128, '2025-06-06', 'jpg', '2024-06-01', 1234, 640, 424, 5678, 3, '2025-06-12 12:08:48.000000'),
	(8, 2, 10, 100, '8.jpg', 44, '2025-06-06', 'jpg', '2024-06-01', 1234, 600, 400, 5678, 3, '2025-06-12 12:08:48.000000');

-- Dumping data for table reviewer_db.reviewer_isuanotasi: ~0 rows (approximately)

-- Dumping data for table reviewer_db.reviewer_isuimage: ~0 rows (approximately)

-- Dumping data for table reviewer_db.reviewer_jobitem: ~8 rows (approximately)
INSERT INTO `reviewer_jobitem` (`id_job_item`, `id_job_assignment_annotator`, `id_job_assignment_reviewer`, `status_pekerjaan`, `id_gambar`, `id_profile_job`) VALUES
	(1, 3, 1, 'P', 1, 1),
	(2, 3, 1, 'P', 5, 1),
	(3, 3, 2, 'P', 2, 2),
	(4, 3, 2, 'P', 6, 2),
	(5, 3, 2, 'P', 3, 3),
	(6, 3, 2, 'P', 7, 3),
	(7, 3, 1, 'P', 4, 4),
	(8, 3, 1, 'P', 8, 4);

-- Dumping data for table reviewer_db.reviewer_member: ~3 rows (approximately)
INSERT INTO `reviewer_member` (`tanggal_registrasi`, `id_member`, `email_member`, `no_hp_member`, `afiliasi`, `peran`, `id_pengguna`) VALUES
	('2025-06-08 19:01:46.223464', 1, '064002200018@std.trisakti.ac.id', 0, '-', '3', 1),
	('2025-06-08 19:02:08.386843', 2, '064002200017@std.trisakti.ac.id', 0, '-', '3', 2),
	('2025-06-09 10:46:21.665227', 3, '064002200013@std.trisakti.ac.id', 0, '-', '2', 3);

-- Dumping data for table reviewer_db.reviewer_memberrole: ~3 rows (approximately)
INSERT INTO `reviewer_memberrole` (`id_member_role`, `is_active`, `id_member`, `id_tipe_role`) VALUES
	(1, 1, 1, 3),
	(2, 1, 2, 3),
	(3, 1, 3, 2);

-- Dumping data for table reviewer_db.reviewer_pengguna: ~3 rows (approximately)
INSERT INTO `reviewer_pengguna` (`id_pengguna`, `nama_pengguna`, `nama_lengkap`, `email`, `password`, `is_active`) VALUES
	(1, 'Priyonoo', 'Agi Priyono', '064002200018@std.trisakti.ac.id', 'pbkdf2_sha256$870000$u70SkTU5guiJ6S4YFpE6bC$KqYfC/yFHP8qi+ig1MctgYdKQxLFXBqu8uSydZilito=', 1),
	(2, 'AdamH', 'Adam Hidayat', '064002200017@std.trisakti.ac.id', 'pbkdf2_sha256$870000$cfvrLoigSDY410hPRLBSWf$KPgYr6s+kJeGWf1xfOCKXcn3IMARqpBhhYawOoG1vp0=', 1),
	(3, 'EvanM', 'Evanda Manggani', '064002200013@std.trisakti.ac.id', 'pbkdf2_sha256$870000$y9mIgNljxWwrWiYL8TaR73$F4QizJRgo3QSQdH4JLpS6NyKcicYpZr5CxtxRP24RYE=', 1);

-- Dumping data for table reviewer_db.reviewer_polygontool: ~47 rows (approximately)
INSERT INTO `reviewer_polygontool` (`id_polygon_tool`, `koordinat_xn`, `koordinat_yn`, `id_anotasi`) VALUES
	(1, 464, 177, 6),
	(2, 651, 168, 6),
	(3, 681, 231, 6),
	(4, 705, 236, 6),
	(5, 706, 416, 6),
	(6, 464, 428, 6),
	(7, 726, 11, 7),
	(8, 1097, 13, 7),
	(9, 1108, 356, 7),
	(10, 987, 351, 7),
	(11, 919, 305, 7),
	(12, 801, 318, 7),
	(13, 737, 337, 7),
	(14, 451, 367, 8),
	(15, 451, 46, 8),
	(16, 401, 19, 8),
	(17, 265, 44, 8),
	(18, 255, 209, 8),
	(19, 83, 210, 8),
	(20, 59, 396, 8),
	(21, 597, 495, 9),
	(22, 574, 508, 9),
	(23, 541, 506, 9),
	(24, 509, 522, 9),
	(25, 461, 518, 9),
	(26, 393, 524, 9),
	(27, 394, 577, 9),
	(28, 326, 577, 9),
	(29, 331, 531, 9),
	(30, 103, 541, 9),
	(31, 19, 602, 9),
	(32, 24, 690, 9),
	(33, 1135, 699, 9),
	(34, 1122, 635, 9),
	(35, 938, 586, 9),
	(36, 918, 555, 9),
	(37, 950, 537, 9),
	(38, 986, 537, 9),
	(39, 962, 526, 9),
	(40, 846, 528, 9),
	(41, 843, 565, 9),
	(42, 846, 641, 9),
	(43, 707, 639, 9),
	(44, 638, 637, 9),
	(45, 599, 611, 9),
	(46, 608, 542, 9),
	(47, 614, 512, 9);

-- Dumping data for table reviewer_db.reviewer_profilejob: ~4 rows (approximately)
INSERT INTO `reviewer_profilejob` (`id_profile_job`, `id_pengguna`, `nama_profile_job`, `deskripsi`, `start_date`, `end_date`, `isu`) VALUES
	(1, 1, 'Annotate project: dataset_kendaraan', 'Segmentasi kendaraan', '2025-06-11', '2025-07-31', 'Tidak ada'),
	(2, 2, 'Annotate project: dataset_buah', 'Segmentasi buah-buahan', '2025-06-11', '2025-08-20', 'Perbedaan label'),
	(3, 2, 'Annotate project: dataset_hewan', 'Segmentasi hewan liar', '2025-06-11', '2025-09-19', 'Resolusi gambar rendah'),
	(4, 1, 'Annotate project: dataset_tanaman', 'Segmentasi tanaman dan tumbuhan', '2025-06-11', '2025-11-08', 'Kurang data latih');

-- Dumping data for table reviewer_db.reviewer_segmentasi: ~8 rows (approximately)
INSERT INTO `reviewer_segmentasi` (`id_segmentasi`, `id_tipe_segmentasi`, `label_segmentasi`, `warna_segmentasi`, `koordinat`, `id_job_item`) VALUES
	(1, 2, 'Mobil', '#FF0000', 0, 1),
	(2, 2, 'Manusia', '#FFFF00', 0, 1),
	(3, 1, 'Gedung', '#0047FF', 0, 1),
	(4, 1, 'Jalanan', '#0058FF', 0, 1),
	(5, 2, 'Mobil', '#FF0000', 0, 2),
	(6, 2, 'Motor', '#994C00', 0, 2),
	(7, 2, 'Pohon Kelapa', '#99FF99', 0, 7),
	(8, 2, 'Bunga Matahari', '#FF99FF', 0, 8);

-- Dumping data for table reviewer_db.reviewer_tiperole: ~4 rows (approximately)
INSERT INTO `reviewer_tiperole` (`id_tipe_role`, `nama_tipe_role`) VALUES
	(0, 'guest'),
	(1, 'master'),
	(2, 'annotator'),
	(3, 'reviewer');

-- Dumping data for table reviewer_db.reviewer_tipesegmentasi: ~3 rows (approximately)
INSERT INTO `reviewer_tipesegmentasi` (`id_tipe_segmentasi`, `nama_tipe_segmentasi`) VALUES
	(1, 'semantic'),
	(2, 'instance'),
	(3, 'panoptic');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
