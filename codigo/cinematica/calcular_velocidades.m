function [v_G, omega_AB, omega_BC, omega_DE, omega_EF, omega_FG] = calcular_velocidades(theta_OA, omega_OA, puntos, params)
% Calcula la velocidad lineal del punto G y velocidades angulares de eslabones
% theta_OA: ángulo de la manivela (rad)
% omega_OA: velocidad angular de la manivela (rad/s)
% puntos: estructura con posiciones
% params: estructura con longitudes


% Extraer posiciones
O = puntos.O; A = puntos.A; B = puntos.B; C = puntos.C;
D = puntos.D; E = puntos.E; F = puntos.F; G = puntos.G;

L_OA = params.L_OA; L_AB = params.L_AB; L_BF = params.L_BF; L_BC = params.L_BC;
L_DE = params.L_DE; L_EF = params.L_EF; L_FG = params.L_FG; L_EG = params.L_EG;

% Velocidad de A (manivela)
v_A = omega_OA * L_OA * [-sin(theta_OA), cos(theta_OA)];

% Ángulos de eslabones
vec_AB = B - A; theta_AB = atan2(vec_AB(2), vec_AB(1));
vec_BC = C - B; theta_BC = atan2(vec_BC(2), vec_BC(1));

% Jacobiano circuito O-A-B-C
J1 = [ -L_AB*sin(theta_AB), -L_BC*sin(theta_BC);
	L_AB*cos(theta_AB),  L_BC*cos(theta_BC) ];
b1 = -v_A';
omegas1 = J1 \ b1;
omega_AB = omegas1(1); omega_BC = omegas1(2);

% Velocidad de F (en línea con AB)
v_F = v_A + omega_AB * (L_AB + L_BF) * [-sin(theta_AB), cos(theta_AB)];

% Ángulos del triángulo superior
vec_DE = E - D; theta_DE = atan2(vec_DE(2), vec_DE(1));
vec_EF = F - E; theta_EF = atan2(vec_EF(2), vec_EF(1));

% Jacobiano circuito D-E-F
J2 = [ -L_DE*sin(theta_DE), -L_EF*sin(theta_EF);
	L_DE*cos(theta_DE),  L_EF*cos(theta_EF) ];
b2 = v_F';
omegas2 = J2 \ b2;
omega_DE = omegas2(1); omega_EF = omegas2(2);

% Velocidad de E
v_E = omega_DE * L_DE * [-sin(theta_DE), cos(theta_DE)];

% Ángulos del triángulo E-F-G
vec_FG = G - F; theta_FG = atan2(vec_FG(2), vec_FG(1));
vec_EG = G - E; theta_EG = atan2(vec_EG(2), vec_EG(1));

% Jacobiano triángulo E-F-G
J3 = [ -L_FG*sin(theta_FG),  L_EG*sin(theta_EG);
	L_FG*cos(theta_FG), -L_EG*cos(theta_EG) ];
b3 = v_E' - v_F';
omegas3 = J3 \ b3;
omega_FG = omegas3(1);

% Velocidad de G
v_G = v_F + omega_FG * L_FG * [-sin(theta_FG), cos(theta_FG)];

end
