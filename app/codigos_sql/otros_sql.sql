SELECT
	e.id_empleado,
	, CONCAT(p.nombres,' ',p.apellidos) empleado
	, p.ci
FROM empleados e LEFT JOIN personas p ON e.id_empleado = p.id_persona