function puntos = calcular_posiciones(theta_OA, O, C, D, L_OA, L_AB, L_BF, L_BC, L_DE, L_EF, L_FG, L_EG)
% Calcula las posiciones de los puntos clave de la pata
% theta_OA: ángulo de la manivela en radianes
% Retorna estructura con campos: A, B, C, D, E, F, G

% Punto A (manivela)
A = O + L_OA*[cos(theta_OA), sin(theta_OA)];

% Sistema de ecuaciones no lineales para B, E, F, G
% Variables: xB, yB, xE, yE, xF, yF, xG, yG
fun = @(X) restricciones(X, A, C, D, L_AB, L_BF, L_BC, L_DE, L_EF, L_FG, L_EG);

% Estimación inicial (puede mejorarse)
X0 = [A(1)+L_AB, A(2), D(1)+L_DE, D(2), A(1)+L_AB+L_BF, A(2), A(1)+L_AB+L_BF+L_FG, A(2)];

options = optimset('Display','off');
X = fsolve(fun, X0, options);

B = X(1:2);
E = X(3:4);
F = X(5:6);
G = X(7:8);

puntos = struct('O',O,'A',A,'B',B,'C',C,'D',D,'E',E,'F',F,'G',G);
end

function F = restricciones(X, A, C, D, L_AB, L_BF, L_BC, L_DE, L_EF, L_FG, L_EG)
% Ecuaciones de restricción vectorial
xB = X(1); yB = X(2);
xE = X(3); yE = X(4);
xF = X(5); yF = X(6);
xG = X(7); yG = X(8);

% Circuito O-A-B-C
F1 = norm([xB, yB] - A) - L_AB;
F2 = norm([xB, yB] - C) - L_BC;
F3 = norm([xF, yF] - [xB, yB]) - L_BF;

% Circuito D-E-F
F4 = norm([xE, yE] - D) - L_DE;
F5 = norm([xF, yF] - [xE, yE]) - L_EF;

% Triángulo E-F-G
F6 = norm([xG, yG] - [xF, yF]) - L_FG;
F7 = norm([xG, yG] - [xE, yE]) - L_EG;
F8 = norm([xE, yE] - [xF, yF]) - L_EF;

F = [F1; F2; F3; F4; F5; F6; F7; F8];
end
