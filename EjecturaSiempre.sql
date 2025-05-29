USE ProyectoFMetodos;


SELECT * FROM Metodos;


INSERT INTO Metodos (Nombre, Descripcion, Tipo)
VALUES 
('Newton-Raphson', 
 'M�todo iterativo para encontrar ra�ces de funciones mediante aproximaciones usando derivadas.', 
 'Iteraci�n'),

('Secante', 
 'M�todo num�rico para encontrar ra�ces aproximadas de funciones, utilizando secantes en lugar de derivadas.', 
 'Iteraci�n'),

('M�ller', 
 'M�todo de aproximaci�n para encontrar ra�ces de funciones basado en interpolaci�n cuadr�tica.', 
 'Iteraci�n'),

('Gauss-Jordan', 
 'Algoritmo para resolver sistemas de ecuaciones lineales mediante eliminaci�n y reducci�n a matriz identidad.', 
 'Eliminaci�n');
