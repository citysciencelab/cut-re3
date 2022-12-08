import SimulationToolComponent from "./components/SimulationTool.vue";
import SimulationToolStore from "./store/SimulationTool";
import deLocale from "./locales/de/additional.json";
import enLocale from "./locales/en/additional.json";

export default {
    component: SimulationToolComponent,
    store: SimulationToolStore,
    locales: {
        de: deLocale,
        en: enLocale,
    },
};

