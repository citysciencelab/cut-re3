<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import ToolTemplate from "../../../src/modules/tools/ToolTemplate.vue";
import SimulationProcesses from "./SimulationProcesses.vue";
import SimulationProcess from "./SimulationProcess.vue";
import SimulationProcessJob from "./SimulationProcessJob.vue";
import actions from "../store/actionsSimulationTool";
import getters from "../store/gettersSimulationTool";
import mutations from "../store/mutationsSimulationTool";

export default {
  name: "SimulationTool",
  components: {
    ToolTemplate,
    SimulationProcesses,
    SimulationProcess,
    SimulationProcessJob,
  },
  data() {
    return {};
  },
  computed: {
    ...mapGetters("Tools/SimulationTool", Object.keys(getters)),
  },
  watch: {
    /**
     * Listens to the active property change.
     * @param {Boolean} isActive Value deciding whether the tool gets activated or deactivated.
     * @returns {void}
     */
    active(isActive) {
      if (isActive) {
        this.setMode("processes");
        this.fetchProcesses();
      }
    },
  },
  created() {
    this.$on("close", this.close);
  },
  /**
   * Put initialize here if mounting occurs after config parsing
   * @returns {void}
   */
  mounted() {},
  methods: {
    ...mapMutations("Tools/SimulationTool", Object.keys(mutations)),
    ...mapActions("Tools/SimulationTool", Object.keys(actions)),
    /**
     * Selects a process by id
     * @returns {void}
     */
    selectProcess(id) {
      if (typeof id === "string") {
        this.setSelectedProcessId(id);
        this.setMode("process");
      } else {
        this.setSelectedProcessId(null);
        this.setMode("processes");
      }
    },
    /**
     * Selects a job by id
     * @returns {void}
     */
    selectJob(id) {
      this.setSelectedJobId(typeof id === "string" ? id : null);

      if (typeof id === "string") {
        this.setMode("job");
      } else if (this.selectedProcessId) {
        this.setMode("process");
      } else {
        this.setMode("processes");
      }
    },
    /**
     * Closes this tool window by setting active to false
     * @returns {void}
     */
    close() {
      this.setActive(false);

      const model = Radio.request("ModelList", "getModelByAttributes", {
        id: this.$store.state.Tools.SimulationTool.id,
      });

      if (model) {
        model.set("isActive", false);
      }
    },
  },
};
</script>

<template>
  <ToolTemplate
    :title="$t(name)"
    :icon="icon"
    :active="active"
    :render-to-window="renderToWindow"
    :resizable-window="resizableWindow"
    :deactivate-gfi="deactivateGFI"
    :initial-width="initialWidth"
    :initial-width-mobile="initialWidthMobile"
  >
    <template #toolBody>
      <div v-if="active" id="tool-simulationTool">
        <SimulationProcesses
          v-if="mode === 'processes'"
          :processes="processes"
          @selected="selectProcess"
        />

        <SimulationProcess
          v-if="mode === 'process'"
          :process-id="selectedProcessId"
          @selected="selectJob"
          @close="selectProcess"
        />

        <SimulationProcessJob
          v-if="mode === 'job'"
          :job-id="selectedJobId"
          @close="selectJob"
        />
      </div>
    </template>
  </ToolTemplate>
</template>

<style lang="scss" scoped>
#tool-simulationTool {
  background: white;
}
</style>
