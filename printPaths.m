
path =[ 147, 21, 1, 12, 104, 126] + 1;
path =[96, 56, 14, 0, 29]+1;

nNodes = 150

step = 2*pi/nNodes;

t = 0 : step : 2*pi;

#plot(cos(t),sin(t),'.r','markersize',30)

hold on
length(path)-1
for i = 1 : length(path)-1
   h = line([cos(t(path(i))), cos(t(path(i+1)))],[sin(t(path(i))),sin(t(path(i+1)))]);
   set(h,'color','r','linewidth',3);
end

