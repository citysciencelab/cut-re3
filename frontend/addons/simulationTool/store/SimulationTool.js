import GenericTool from "../../../src/modules/tools/indexTools";
import composeModules from "../../../src/app-store/utils/composeModules";
import actions from "./actionsSimulationTool";
import getters from "./gettersSimulationTool";
import mutations from "./mutationsSimulationTool";
import state from "./stateSimulationTool";

export default composeModules([
    GenericTool,
    {
        namespaced: true, // mandatory
        state,
        actions,
        mutations,
        getters,
    },
]);

