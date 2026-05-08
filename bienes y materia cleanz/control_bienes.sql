-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 07-05-2026 a las 00:18:16
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `control_bienes`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bienes_materia`
--

CREATE TABLE `bienes_materia` (
  `id_item` int(10) NOT NULL,
  `id_seccion` int(10) NOT NULL,
  `id_subgrupo` int(11) DEFAULT NULL,
  `id_area` int(10) DEFAULT NULL,
  `id_responsable` int(11) DEFAULT NULL,
  `nro_identificacion` varchar(50) DEFAULT NULL,
  `id_grupo` int(10) DEFAULT NULL,
  `nombre_elementos` varchar(255) NOT NULL,
  `departamento` varchar(100) DEFAULT NULL,
  `area_especifica` varchar(100) DEFAULT NULL,
  `anio_ingreso` varchar(20) DEFAULT NULL,
  `cantidad` int(10) NOT NULL,
  `valor_unitario` decimal(15,2) NOT NULL,
  `valor_total` decimal(15,2) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `id_usuario` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `bienes_materia`
--

INSERT INTO `bienes_materia` (`id_item`, `id_seccion`, `id_subgrupo`, `id_area`, `id_responsable`, `nro_identificacion`, `id_grupo`, `nombre_elementos`, `departamento`, `area_especifica`, `anio_ingreso`, `cantidad`, `valor_unitario`, `valor_total`, `fecha_ingreso`, `id_usuario`) VALUES
(35, 31, 7, 7, NULL, '20010-0122-2', 2, 'EXTINTOR PEQUEÑO', 'PRESIDENCIA', 'DESPACHO', '06/05/2026', 1, 120000.00, 120000.00, '2026-05-06', 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `bienes_materia`
--
ALTER TABLE `bienes_materia`
  ADD PRIMARY KEY (`id_item`),
  ADD UNIQUE KEY `nro_identificacion` (`nro_identificacion`),
  ADD KEY `id_seccion` (`id_seccion`,`id_area`,`id_responsable`),
  ADD KEY `usuario` (`id_usuario`),
  ADD KEY `id_subgrupo` (`id_subgrupo`),
  ADD KEY `id_area` (`id_area`),
  ADD KEY `fk_responsable_bien` (`id_responsable`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `bienes_materia`
--
ALTER TABLE `bienes_materia`
  MODIFY `id_item` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `bienes_materia`
--
ALTER TABLE `bienes_materia`
  ADD CONSTRAINT `bienes_materia_ibfk_1` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`) ON UPDATE CASCADE,
  ADD CONSTRAINT `bienes_materia_ibfk_4` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_bienes_area` FOREIGN KEY (`id_area`) REFERENCES `areas` (`id_area`),
  ADD CONSTRAINT `fk_responsable_bien` FOREIGN KEY (`id_responsable`) REFERENCES `responsables` (`id_responsable`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
