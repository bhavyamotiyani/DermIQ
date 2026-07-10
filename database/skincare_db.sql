-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 10, 2026 at 02:16 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `skincare_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `addresses`
--

CREATE TABLE `addresses` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `street_address` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `pin_code` varchar(20) NOT NULL,
  `is_default` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `addresses`
--

INSERT INTO `addresses` (`id`, `user_id`, `full_name`, `phone`, `street_address`, `city`, `state`, `pin_code`, `is_default`, `created_at`) VALUES
(1, 2, 'Bhavya Motiyani', '+919773061563', '1-The Royal Palace Pg for Girls Near One plus moblie showroom near swastik cross road Navrangpura Ahmedabad', 'AHMEDABAD', 'Gujarat', '380009', 1, '2026-07-08 17:50:54'),
(2, 3, 'Rudra Bhavsar', '+918200214115', '1, Bliss Homes 3, CG Road', 'Navsari', 'Gujarat', '396445', 1, '2026-07-08 18:08:52'),
(3, 4, 'Kashish Sainani', '+916377117784', '86, Ganesh Farm Society', 'Valsad', 'Gujarat', '396001', 1, '2026-07-08 18:12:02'),
(4, 5, 'Zeel Gandhi', '+919510758676', '83, Shailesh Park Society', 'Vadodara', 'Gujarat', '390001', 1, '2026-07-08 18:18:34'),
(5, 5, 'Bhavya Motiyani', '09773061563', '1-The Royal Palace Pg for Girls Near One plus moblie showroom near swastik cross road Navrangpura Ahmedabad', 'AHMEDABAD', 'Gujarat', '380009', 0, '2026-07-08 18:18:49'),
(6, 6, 'Mayank Pritmani', '+917203887396', '56, Ram Nagar', 'Anand', 'Gujarat', '388001', 1, '2026-07-08 18:40:36');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `id` int(11) NOT NULL,
  `transaction_id` int(11) NOT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `payment_status` varchar(50) DEFAULT NULL,
  `amount_paid` float NOT NULL,
  `transaction_ref` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`id`, `transaction_id`, `payment_method`, `payment_status`, `amount_paid`, `transaction_ref`, `created_at`) VALUES
(1, 1, 'ONLINE', 'paid', 1349, 'pay_TB6IQENWDntfTv', '2026-07-08 18:04:03'),
(2, 2, 'ONLINE', 'paid', 399, 'pay_TB6IQENWDntfTv', '2026-07-08 18:04:03'),
(3, 3, 'ONLINE', 'paid', 999, 'pay_TB6IQENWDntfTv', '2026-07-08 18:04:03'),
(4, 4, 'COD', 'pending', 1349, NULL, '2026-07-08 18:09:24'),
(5, 5, 'COD', 'pending', 699, NULL, '2026-07-08 18:09:24'),
(6, 6, 'ONLINE', 'paid', 349, 'pay_TB6Raivg2pxaCj', '2026-07-08 18:12:43'),
(7, 7, 'ONLINE', 'paid', 698, 'pay_TB6Raivg2pxaCj', '2026-07-08 18:12:43'),
(8, 8, 'COD', 'pending', 1598, NULL, '2026-07-08 18:18:37'),
(9, 9, 'ONLINE', 'paid', 349, 'pay_TB6vXgseD9Idjm', '2026-07-08 18:41:04'),
(10, 10, 'ONLINE', 'paid', 349, 'pay_TBJqoZmHtImmwO', '2026-07-09 07:19:38'),
(11, 11, 'ONLINE', 'paid', 549, 'pay_TBJqoZmHtImmwO', '2026-07-09 07:19:39');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `brand` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `price` float NOT NULL,
  `rating` float DEFAULT NULL,
  `ingredients` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `suitable_for` varchar(100) DEFAULT NULL,
  `concerns` varchar(255) DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `name`, `brand`, `category`, `price`, `rating`, `ingredients`, `description`, `image_url`, `suitable_for`, `concerns`, `stock`, `is_active`, `created_at`) VALUES
(1, 'Hydrating Facial Cleanser', 'CeraVe', 'Cleanser', 1349, 4.7, 'Ceramides, Hyaluronic Acid, Glycerin', 'A gentle, non-foaming cleanser designed to hydrate and restore the skin\'s natural barrier.', 'cerave_cleanser.jpg', 'Dry, Normal, Sensitive', 'Dryness, Sensitivity', 50, 1, '2026-07-10 16:00:23'),
(2, 'Toleriane Purifying Foaming Cleanser', 'La Roche-Posay', 'Cleanser', 1599, 4.8, 'Ceramide-3, Niacinamide, Glycerin, La Roche-Posay Prebiotic Thermal Water', 'A daily foaming face wash for normal to oily sensitive skin that effectively removes dirt and makeup.', 'lrp_cleanser.jpg', 'Oily, Combination, Sensitive', 'Acne, Pores, Oil Control', 45, 1, '2026-07-10 16:00:23'),
(3, 'Gentle Skin Cleanser', 'Cetaphil', 'Cleanser', 349, 4.5, 'Glycerin, Panthenol (Vitamin B5), Niacinamide (Vitamin B3)', 'Clinically proven to hydrate while cleansing, leaving skin feeling soft, smooth and healthy.', 'cetaphil_cleanser.jpg', 'All Skin Types', 'Dryness, Sensitivity', 100, 1, '2026-07-10 16:00:23'),
(4, 'Glycolic Acid 7% Toning Solution', 'The Ordinary', 'Toner', 999, 4.6, 'Glycolic Acid, Aloe Barbadensis Leaf Water, Ginseng Root Extract', 'An exfoliating toning solution that offers mild exfoliation for improved skin radiance and visible clarity.', 'ordinary_toner.jpg', 'Normal, Oily, Combination', 'Pores, Dullness, Dark Spots', 60, 1, '2026-07-10 16:00:23'),
(5, 'Skin Perfecting 2% BHA Liquid Exfoliant', 'Paula\'s Choice', 'Toner', 2800, 4.8, 'Salicylic Acid 2%, Green Tea Extract, Methylpropanediol', 'A gentle leave-on exfoliant that quickly unclogs pores, smooths wrinkles, brightens and evens out skin tone.', 'paulas_choice_toner.jpg', 'Oily, Combination, Normal', 'Acne, Pores, Blackheads', 30, 1, '2026-07-10 16:00:23'),
(6, 'Calendula Herbal-Extract Alcohol-Free Toner', 'Kiehl\'s', 'Toner', 3200, 4.7, 'Calendula, Allantoin, Great Burdock Root', 'A gentle, alcohol-free facial toner formulated with Calendula petals to soothe and refresh skin.', 'kiehls_toner.jpg', 'Dry, Normal, Sensitive', 'Redness, Sensitivity', 25, 1, '2026-07-10 16:00:23'),
(7, 'Vitamin C Suspension 23% + HA Spheres 2%', 'The Ordinary', 'Vitamin C Serum', 699, 4.3, 'L-Ascorbic Acid 23%, Hyaluronic Acid Spheres', 'A water-free, silicone-free stable suspension that offers direct Vitamin C to visibly target aging and dullness.', 'ordinary_vitc.jpg', 'All Skin Types', 'Dark Spots, Dullness, Aging', 80, 1, '2026-07-10 16:00:23'),
(8, 'Revitalift 10% Pure Vitamin C Serum', 'L\'Oreal Paris', 'Vitamin C Serum', 1199, 4.5, 'Ascorbic Acid 10%, Adenosine, Glycerin', 'Dermatologist-validated, lightweight yet potent serum that brightens skin tone and reduces wrinkles.', 'loreal_vitc.jpg', 'All Skin Types', 'Dullness, Fine Lines, Dark Spots', 40, 1, '2026-07-10 16:00:23'),
(9, 'UV Clear Broad-Spectrum SPF 46', 'EltaMD', 'Sunscreen', 3800, 4.9, 'Zinc Oxide 9%, Niacinamide 4%, Sodium Hyaluronate', 'Oil-free sunscreen protects sensitive skin types prone to breakouts, rosacea, and discoloration.', 'eltamd_sunscreen.jpg', 'Sensitive, Oily, Acne-prone', 'Acne, Redness, Sun Protection', 35, 1, '2026-07-10 16:00:23'),
(10, 'Ultra Sheer Dry-Touch Sunscreen SPF 50+', 'Neutrogena', 'Sunscreen', 549, 4.4, 'Helioplex Technology, Homosalate, Oxybenzone', 'Lightweight, non-greasy sunscreen that provides superior broad-spectrum protection with a dry-touch finish.', 'neutrogena_sunscreen.jpg', 'All Skin Types', 'Sun Protection, Aging', 120, 1, '2026-07-10 16:00:23'),
(11, 'Retinol 0.5% in Squalane', 'The Ordinary', 'Treatment Serum', 799, 4.5, 'Retinol 0.5%, Squalane, Jojoba Seed Oil', 'A highly stable, water-free solution that targets signs of aging, fine lines, and skin texture.', 'ordinary_retinol.jpg', 'Dry, Normal, Oily, Combination', 'Aging, Fine Lines, Texture', 65, 1, '2026-07-10 16:00:23'),
(12, 'BHA Blackhead Power Liquid', 'COSRX', 'Treatment Serum', 1450, 4.6, 'Betaine Salicylate 4%, Niacinamide 2%, White Willow Bark Water', 'Clinically proven to reduce blackheads, sebum build-up, and unclog pores using gentle chemical exfoliation.', 'cosrx_bha.jpg', 'Oily, Combination, Acne-prone', 'Acne, Pores, Blackheads', 50, 1, '2026-07-10 16:00:23');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `amount` float NOT NULL,
  `quantity` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `address_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `product_id`, `amount`, `quantity`, `status`, `date`, `address_id`) VALUES
(1, 2, 52, 1349, 1, 'completed', '2026-07-08 18:04:03', 1),
(2, 2, 54, 399, 1, 'completed', '2026-07-08 18:04:03', 1),
(3, 2, 82, 999, 1, 'completed', '2026-07-08 18:04:03', 1),
(4, 3, 52, 1349, 1, 'completed', '2026-07-08 18:09:24', 2),
(5, 3, 63, 699, 1, 'completed', '2026-07-08 18:09:24', 2),
(6, 4, 57, 349, 1, 'completed', '2026-07-08 18:12:43', 3),
(7, 4, 70, 698, 2, 'completed', '2026-07-08 18:12:43', 3),
(8, 5, 51, 1598, 2, 'completed', '2026-07-08 18:18:37', 4),
(9, 6, 57, 349, 1, 'completed', '2026-07-08 18:41:04', 6),
(10, 6, 57, 349, 1, 'completed', '2026-07-09 07:19:38', 6),
(11, 6, 79, 549, 1, 'completed', '2026-07-09 07:19:39', 6);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `skin_type` varchar(50) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `concerns` text DEFAULT NULL,
  `quiz_results` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `is_admin`, `skin_type`, `age`, `concerns`, `quiz_results`, `created_at`) VALUES
(1, 'Admin User', 'admin@dermiq.com', '0192023a7bbd732', 'admin', 1, 'normal', NULL, NULL, NULL, '2026-07-07 09:58:21'),
(2, 'Bhavya Motiyani', 'bhavyamotiyani29@gmail.com', '6ad14ba9986e361', 'user', 0, 'Normal', NULL, '[\"Dryness\", \"Pores\"]', '{\"q1\": \"normal\", \"q2\": \"rarely\", \"q3\": \"mild\", \"q4\": \"medium\", \"q5\": \"no\", \"q6\": \"yes\", \"analyzed_at\": \"08 Jul 2026\", \"budget\": 2000.0, \"sensitivity\": \"mild\"}', '2026-07-07 10:12:40'),
(3, 'Rudra Bhavsar', 'rudrabhavsar04@gmail.com', '25f9e794323b453', 'user', 0, 'Dry', NULL, '[\"Dryness\"]', '{\"q1\": \"dry\", \"q2\": \"rarely\", \"q3\": \"strong\", \"q4\": \"invisible\", \"q5\": \"no\", \"q6\": \"no\", \"analyzed_at\": \"08 Jul 2026\", \"budget\": 2000.0, \"sensitivity\": \"mild\"}', '2026-07-08 18:06:36'),
(4, 'Kashish Sainani', 'kashishsainani@gmail.com', '25f9e794323b453', 'user', 0, 'Combination', NULL, '[\"Acne\"]', '{\"budget\": 2000.0, \"sensitivity\": \"mild\"}', '2026-07-08 18:10:20'),
(5, 'Zeel Gandhi', 'zeelgandhi@gmail.com', '25f9e794323b453', 'user', 0, 'Combination', NULL, '[\"Dryness\", \"Dark Spots\"]', '{\"budget\": 2000.0, \"sensitivity\": \"mild\"}', '2026-07-08 18:16:36'),
(6, 'Mayank Pritmani', 'mayankpritmani@gmail.com', '25f9e794323b453', 'user', 0, 'Oily', NULL, '[\"Pores\"]', '{\"budget\": 2000.0, \"sensitivity\": \"mild\"}', '2026-07-08 18:33:49');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `addresses`
--
ALTER TABLE `addresses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `transaction_id` (`transaction_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `address_id` (`address_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `addresses`
--
ALTER TABLE `addresses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `addresses`
--
ALTER TABLE `addresses`
  ADD CONSTRAINT `addresses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`id`);

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `transactions_ibfk_3` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
