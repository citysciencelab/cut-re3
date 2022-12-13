import { generateSimpleGetters } from "../../../src/app-store/utils/generators";
import simulationToolState from "./stateSimulationTool";

const getters = {
    ...generateSimpleGetters(simulationToolState),
};

export default getters;
