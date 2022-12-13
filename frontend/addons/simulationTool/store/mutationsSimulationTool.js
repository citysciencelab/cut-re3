import { generateSimpleMutations } from "../../../src/app-store/utils/generators";
import stateSimulationTool from "./stateSimulationTool";

const mutations = {
  ...generateSimpleMutations(stateSimulationTool),
};

export default mutations;
