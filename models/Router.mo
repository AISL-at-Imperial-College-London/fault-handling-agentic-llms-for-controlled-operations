// Define a Router model that will be used as an outer component.
// This model defines one input connector (routerInput)
// and an array of two output connectors (routerOutput) which are expected
// to be connected conditionally.
model Router
  // Use the StateGraph.Transition connector for routing.
  // (You could also define your own connector type if desired.)
  Modelica.StateGraph.Transition routerInput
    annotation(Placement(transformation(origin = {-180,100}, extent = {{-10,-10},{10,10}})));
  Modelica.StateGraph.Transition routerOutput[2]
    annotation(Placement(transformation(origin = {-120,100}, extent = {{-10,-10},{10,10}})));
  
  // (No equations are needed here since this model mainly provides connectors)
end Router;
