-- GELIS MongoDB to SQL Export\n-- Generated: 2025-12-11T05:35:07.149750\n-- Database: test_database\n\nSET FOREIGN_KEY_CHECKS=0;\n\n-- =============================================\n-- CREATE TABLES\n-- =============================================\n\n-- Table: roles\nDROP TABLE IF EXISTS `roles`;\n
CREATE TABLE IF NOT EXISTS `roles` (
  `id` INT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `description` TEXT,
  `permissions` JSON,
  `created_at` DATETIME NOT NULL,
  INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- Table: users\nDROP TABLE IF EXISTS `users`;\n
CREATE TABLE IF NOT EXISTS `users` (
  `id` VARCHAR(36) PRIMARY KEY,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20),
  `address` TEXT,
  `role_id` INT NOT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `last_login` DATETIME,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  FOREIGN KEY (role_id) REFERENCES roles(id),
  INDEX idx_username (username),
  INDEX idx_email (email),
  INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- Table: businesses\nDROP TABLE IF EXISTS `businesses`;\n
CREATE TABLE IF NOT EXISTS `businesses` (
  `id` VARCHAR(36) PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `category` VARCHAR(50) NOT NULL,
  `description` TEXT,
  `address` TEXT,
  `phone` VARCHAR(20),
  `email` VARCHAR(100),
  `settings` JSON,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_by` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  FOREIGN KEY (created_by) REFERENCES users(id),
  INDEX idx_category (category),
  INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- Table: orders\nDROP TABLE IF EXISTS `orders`;\n
CREATE TABLE IF NOT EXISTS `orders` (
  `id` VARCHAR(36) PRIMARY KEY,
  `order_number` VARCHAR(50) UNIQUE NOT NULL,
  `business_id` VARCHAR(36) NOT NULL,
  `customer_name` VARCHAR(100) NOT NULL,
  `customer_phone` VARCHAR(20),
  `customer_email` VARCHAR(100),
  `service_type` VARCHAR(50) NOT NULL,
  `order_details` JSON NOT NULL,
  `total_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `paid_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `status` ENUM('pending','processing','completed','cancelled') NOT NULL DEFAULT 'pending',
  `payment_status` ENUM('unpaid','partial','paid','refunded') NOT NULL DEFAULT 'unpaid',
  `payment_method` VARCHAR(50),
  `assigned_to` VARCHAR(36),
  `completion_date` DATETIME,
  `notes` TEXT,
  `created_by` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id),
  FOREIGN KEY (created_by) REFERENCES users(id),
  FOREIGN KEY (assigned_to) REFERENCES users(id),
  INDEX idx_order_number (order_number),
  INDEX idx_business_id (business_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- Table: transactions\nDROP TABLE IF EXISTS `transactions`;\n
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` VARCHAR(36) PRIMARY KEY,
  `transaction_code` VARCHAR(50) UNIQUE NOT NULL,
  `order_id` VARCHAR(36),
  `business_id` VARCHAR(36) NOT NULL,
  `transaction_type` ENUM('income','expense','transfer','commission') NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `amount` DECIMAL(15,2) NOT NULL,
  `payment_method` VARCHAR(50),
  `reference_number` VARCHAR(100),
  `created_by` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id),
  FOREIGN KEY (created_by) REFERENCES users(id),
  INDEX idx_transaction_code (transaction_code),
  INDEX idx_transaction_type (transaction_type),
  INDEX idx_business_id (business_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- Table: notifications\nDROP TABLE IF EXISTS `notifications`;\n
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `message` TEXT NOT NULL,
  `type` ENUM('info','warning','error','success') NOT NULL DEFAULT 'info',
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  `related_id` VARCHAR(36),
  `related_type` VARCHAR(50),
  `action_url` VARCHAR(255),
  `created_at` DATETIME NOT NULL,
  INDEX idx_user_id (user_id),
  INDEX idx_is_read (is_read),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- Table: activity_logs\nDROP TABLE IF EXISTS `activity_logs`;\n
CREATE TABLE IF NOT EXISTS `activity_logs` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36) NOT NULL,
  `action` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `ip_address` VARCHAR(45),
  `user_agent` VARCHAR(255),
  `related_id` VARCHAR(36),
  `related_type` VARCHAR(50),
  `created_at` DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_id (user_id),
  INDEX idx_action (action),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n\n-- =============================================\n-- INSERT DATA\n-- =============================================\n\n-- Data for table: roles\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (1, 'Owner', 'Pemilik sistem dengan akses penuh', '{}', '2025-12-11T05:32:03.821176+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (2, 'Manager', 'Manajer operasional', '{}', '2025-12-11T05:32:03.821187+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (3, 'Finance', 'Staff keuangan', '{}', '2025-12-11T05:32:03.821190+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (4, 'Customer Service', 'Customer Service', '{}', '2025-12-11T05:32:03.821192+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (5, 'Kasir', 'Kasir', '{}', '2025-12-11T05:32:03.821193+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (6, 'Loket', 'Petugas Loket', '{}', '2025-12-11T05:32:03.821195+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (7, 'Teknisi', 'Teknisi Lapangan', '{}', '2025-12-11T05:32:03.821196+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (1, 'Owner', 'Pemilik sistem dengan akses penuh', '{}', '2025-12-11T05:32:03.821294+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (2, 'Manager', 'Manajer operasional', '{}', '2025-12-11T05:32:03.821296+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (3, 'Finance', 'Staff keuangan', '{}', '2025-12-11T05:32:03.821298+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (4, 'Customer Service', 'Customer Service', '{}', '2025-12-11T05:32:03.821300+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (5, 'Kasir', 'Kasir', '{}', '2025-12-11T05:32:03.821301+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (6, 'Loket', 'Petugas Loket', '{}', '2025-12-11T05:32:03.821303+00:00');\nINSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `created_at`) VALUES (7, 'Teknisi', 'Teknisi Lapangan', '{}', '2025-12-11T05:32:03.821304+00:00');\n\n-- Data for table: users\nINSERT INTO `users` (`id`, `username`, `email`, `password`, `full_name`, `phone`, `role_id`, `is_active`, `created_at`, `updated_at`, `last_login`) VALUES ('8cd31a3c-48ae-40ee-bc67-dbbe522b0d0c', 'owner', 'owner@gelis.com', '$2b$12$DQhtIm5.EDFAEJN607u.TOTnQm99kmqUrIcls.sDH8ZauUyc0Cpa2', 'Owner GELIS', '081234567890', 1, 1, '2025-12-11T05:32:04.080810+00:00', '2025-12-11T05:32:04.080823+00:00', '2025-12-11T05:32:53.096991+00:00');\nINSERT INTO `users` (`id`, `username`, `email`, `password`, `full_name`, `phone`, `role_id`, `is_active`, `created_at`, `updated_at`, `last_login`) VALUES ('f32562a1-7e9d-49c9-8e6e-ce3fdb1c1bea', 'owner', 'owner@gelis.com', '$2b$12$uGX7WY4007WWMfZWj92qWO3LKYtjo11RHeLQcEn73ofsh85jqTzEi', 'Owner GELIS', '081234567890', 1, 1, '2025-12-11T05:32:04.309449+00:00', '2025-12-11T05:32:04.309459+00:00', NULL);\n\n-- Data for table: businesses\nINSERT INTO `businesses` (`id`, `name`, `category`, `description`, `address`, `phone`, `email`, `settings`, `is_active`, `created_by`, `created_at`, `updated_at`) VALUES ('8e43388d-170e-4be0-bcc0-7a71a126a8b8', 'Loket PPOB Pusat', 'PPOB', 'Layanan pembayaran PPOB (listrik, air, pulsa, dll)', 'Jl. Contoh No. 123', '0211234567', 'ppob@gelis.com', '{"commission_rate": 0.05}', 1, '8cd31a3c-48ae-40ee-bc67-dbbe522b0d0c', '2025-12-11T05:32:04.309951+00:00', '2025-12-11T05:32:04.309955+00:00');\nINSERT INTO `businesses` (`id`, `name`, `category`, `description`, `address`, `phone`, `email`, `settings`, `is_active`, `created_by`, `created_at`, `updated_at`) VALUES ('3072eab7-2065-41b3-a0a8-51530c35eb49', 'Loket PPOB Pusat', 'PPOB', 'Layanan pembayaran PPOB (listrik, air, pulsa, dll)', 'Jl. Contoh No. 123', '0211234567', 'ppob@gelis.com', '{"commission_rate": 0.05}', 1, 'f32562a1-7e9d-49c9-8e6e-ce3fdb1c1bea', '2025-12-11T05:32:04.310379+00:00', '2025-12-11T05:32:04.310382+00:00');\n\n-- Data for table: activity_logs\nINSERT INTO `activity_logs` (`id`, `user_id`, `action`, `description`, `ip_address`, `user_agent`, `created_at`) VALUES ('bc74538d-1f1a-4c1d-8f62-975fae61a484', '8cd31a3c-48ae-40ee-bc67-dbbe522b0d0c', 'login', 'Login dari 10.64.139.36', '10.64.139.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/143.0.7499.4 Safari/537.36', '2025-12-11T05:32:50.533525+00:00');\nINSERT INTO `activity_logs` (`id`, `user_id`, `action`, `description`, `ip_address`, `user_agent`, `created_at`) VALUES ('96e31eba-1d91-4a8f-b0dd-a9bd91f6e84f', '8cd31a3c-48ae-40ee-bc67-dbbe522b0d0c', 'login', 'Login dari 10.64.139.53', '10.64.139.53', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2025-12-11T05:32:53.098679+00:00');\n\nSET FOREIGN_KEY_CHECKS=1;\n