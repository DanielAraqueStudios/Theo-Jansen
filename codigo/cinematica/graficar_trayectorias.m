function graficar_trayectorias(trayectorias_G)
% Visualiza las trayectorias de las 8 patas
figure;
hold on;
for i = 1:size(trayectorias_G,3)
    plot(trayectorias_G(:,1,i), trayectorias_G(:,2,i), 'LineWidth', 2);
end
xlabel('X [cm]'); ylabel('Y [cm]');
title('Trayectorias de las 8 patas (desfase 45°)');
grid on;
legend(arrayfun(@(x) sprintf('Pata %d',x), 1:size(trayectorias_G,3), 'UniformOutput', false));
hold off;
end
