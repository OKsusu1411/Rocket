%% Nominal Vehicle Parameters
%Moments of Inertia (in kg m^2)
Ix_n=490167.882*10^(-6);
Iy_n=5102208.808*10^(-6);
Iz_n=5286501.923*10^(-6);

Ix2_n=3222479.077*10^(-6);
Iy2_n=5164582.426*10^(-6);
Iz2_n=3390566.455*10^(-6);

%Mass (in kg)
m_dry_n=8.376;  %Mass of everything but fuel
m2_dry_n=3.462;  %Mass of everything but fuel
g=9.81;

%Distance between CG and TVC Mount (in m)
l_n=0.80834;
l2_n=0.41934;

%% Control Parameters
%Control Cycle Time (in s)
dt=0.01;

%Servo Actuator Delay (in s)
servo_delay_n=0.05;  %서보딜레이
ignition_delay_n=1.5;  %2단 점화
twostage_delay_n=1.5;%단분리 시간

%% Vehicle Parameter Error (variance from nominal values)
%Misalignment of TVC Mount on Y and Z axes (in m)
Ix_v=0.0001;% 0.1% 
Iy_v=0.0001;
Iz_v=0.0001;

Ix2_v=0.000002131;
Iy2_v=0.000002131;
Iz2_v=0.000002131;

m_dry_v=0.01;% 100g 오차
m2_dry_v=0.01;% 100g 오차
mis_y_v=0.001;% 1cm 오차
mis_z_v=0.001;% 1cm 오차
l_v=0.01;% 10cm 오차
l2_v=0.01;% 10cm 오차

ignition_delay_v=0.01;%점화 딜레이 0.1초 오차
servo_delay_v=0.001;%서보딜레이 0.01초 오차

%% Monte-Carlo
runs=1;
results=struct;
tic
for k=1:runs

    %관성모멘트 불확실성
    Ix_mc=Ix_n+randn*Ix_v;
    Iy_mc=Iy_n+randn*Iy_v;
    Iz_mc=Iz_n+randn*Iz_v;

    Ix2_mc=Ix2_n+randn*Ix2_v;
    Iy2_mc=Iy2_n+randn*Iy2_v;
    Iz2_mc=Iz2_n+randn*Iz2_v;
    
    %엔진 설치 위치의 불확실성
    l_mc=l_n+randn*l_v;%
    l2_mc=l2_n+randn*l2_v;
    mis_y_mc=randn*mis_y_v;%
    mis_z_mc=randn*mis_z_v;%
    
    %ignition 불확실성
    ignition_delay_mc=ignition_delay_n+randn*ignition_delay_v;

    %단분리 불확실성
    servo_delay_mc=servo_delay_n+randn*servo_delay_v;

    %연료 불확실성
    m_dry_mc=m_dry_n+randn*m_dry_v;
    m2_dry_mc=m2_dry_n+randn*m2_dry_v;

    %센서딜레이 불확실성

    sim('Twostage_TVC6DOF_sim.slx',7);
    results.run(k)=ans;
end
toc

%% Plotting Simulated Trajectories
figure(1)
for i=1:runs
    plot3(results.run(1,i).position.signals.values(:,2),results.run(1,i).position.signals.values(:,3),results.run(1,i).position.signals.values(:,1))
    hold on
end
title(sprintf('%d Simulated Monte-Carlo Flight Trajectories',runs))
xlabel('Downrange (m)')
ylabel('Crossrange (m)')
zlabel('Altitude (m)')
axis equal